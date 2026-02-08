"""Extracts transcript/captions from YouTube videos.

This tool retrieves the transcript or closed captions from YouTube videos
using the publicly available caption data. No API key required.
"""

import re

from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


class Input(BaseModel):
    url: str
    language: str = "en"
    preserve_formatting: bool = False


class Output(BaseModel):
    transcript: str = ""
    video_id: str = ""
    language: str = ""
    auto_generated: bool = False
    word_count: int = 0
    success: bool = True
    error_message: str = ""


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id: str, language: str = "en") -> tuple[list[dict], bool]:
    """Fetch transcript from YouTube.

    Returns:
        Tuple of (transcript_list, is_auto_generated)
    """
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    # Try to get manual transcript first
    try:
        transcript = transcript_list.find_transcript([language])
        return transcript.fetch(), False
    except NoTranscriptFound:
        pass

    # Fall back to auto-generated
    try:
        transcript = transcript_list.find_generated_transcript([language])
        return transcript.fetch(), True
    except NoTranscriptFound:
        # Try English as fallback
        if language != "en":
            try:
                transcript = transcript_list.find_generated_transcript(["en"])
                return transcript.fetch(), True
            except NoTranscriptFound:
                pass

    raise NoTranscriptFound(
        video_id, f"No transcript found for language: {language}", []
    )


def format_transcript(transcript_data, preserve_formatting: bool = False) -> str:
    """Format transcript data into readable text.

    Args:
        transcript_data: FetchedTranscript object with snippets
        preserve_formatting: If True, include timestamps
    """
    if preserve_formatting:
        # Include timestamps
        formatted_lines = []
        for segment in transcript_data:
            timestamp = format_timestamp(segment.start)
            formatted_lines.append(f"[{timestamp}] {segment.text}")
        return "\n".join(formatted_lines)
    else:
        # Plain text, joined naturally
        return " ".join(segment.text for segment in transcript_data)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def execute(input_data: Input) -> Output:
    """Extract transcript from YouTube video URL.

    Fetches available captions/transcript and returns as formatted text.
    Prefers manual captions over auto-generated when available.
    """
    # Extract video ID
    video_id = extract_video_id(input_data.url)
    if not video_id:
        return Output(
            success=False,
            error_message="Invalid YouTube URL. Could not extract video ID.",
        )

    try:
        # Fetch transcript
        transcript_data, is_auto_generated = get_transcript(
            video_id, input_data.language
        )

        # Format transcript
        transcript_text = format_transcript(
            transcript_data, input_data.preserve_formatting
        )

        # Count words
        word_count = len(transcript_text.split())

        return Output(
            transcript=transcript_text,
            video_id=video_id,
            language=input_data.language,
            auto_generated=is_auto_generated,
            word_count=word_count,
            success=True,
            error_message="",
        )

    except TranscriptsDisabled:
        return Output(
            video_id=video_id,
            success=False,
            error_message="Transcripts are disabled for this video.",
        )

    except VideoUnavailable:
        return Output(
            video_id=video_id,
            success=False,
            error_message="Video is unavailable or does not exist.",
        )

    except NoTranscriptFound:
        return Output(
            video_id=video_id,
            success=False,
            error_message=f"No transcript available for language '{input_data.language}'. Video may not have captions.",
        )

    except Exception as e:
        return Output(
            video_id=video_id,
            success=False,
            error_message=f"An unexpected error occurred: {str(e)}",
        )
