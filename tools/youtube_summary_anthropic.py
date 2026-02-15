"""Generates AI summary of YouTube videos using the Anthropic (Claude) API.

This tool combines transcript extraction and AI summarization in one step.
It fetches the video transcript and uses the Anthropic API to generate
a concise summary. Requires an Anthropic API key (env var or parameter).
"""

from pydantic import BaseModel

from tools.youtube_transcript import (
    execute as get_transcript,
    Input as TranscriptInput,
)
from tools.summarize_with_anthropic import (
    execute as summarize_text,
    Input as SummarizerInput,
)


class Input(BaseModel):
    url: str
    model: str = "claude-sonnet-4-5-20250929"
    summary_length: str = "medium"
    language: str = "en"
    api_key: str = ""


class Output(BaseModel):
    summary: str = ""
    video_id: str = ""
    title: str = ""
    author: str = ""
    transcript_word_count: int = 0
    summary_word_count: int = 0
    model_used: str = ""
    auto_generated_captions: bool = False
    success: bool = True
    error_message: str = ""


def execute(input_data: Input) -> Output:
    """Generate AI summary of YouTube video using the Anthropic API.

    Combines transcript extraction and Claude summarization in one operation.
    Returns comprehensive metadata along with the generated summary.
    """
    # Step 1: Get transcript
    transcript_result = get_transcript(
        TranscriptInput(
            url=input_data.url,
            language=input_data.language,
            preserve_formatting=False,
        )
    )

    if not transcript_result.success:
        return Output(
            success=False,
            error_message=f"Failed to get transcript: {transcript_result.error_message}",
        )

    # Step 2: Get video metadata
    try:
        from tools.youtube_analyzer import execute as get_metadata
        from tools.youtube_analyzer import Input as MetadataInput

        metadata_result = get_metadata(MetadataInput(url=input_data.url))
        title = metadata_result.title if metadata_result.success else ""
        author = metadata_result.author if metadata_result.success else ""
    except Exception:
        title = ""
        author = ""

    # Step 3: Summarize transcript
    summary_result = summarize_text(
        SummarizerInput(
            text=transcript_result.transcript,
            model=input_data.model,
            summary_length=input_data.summary_length,
            api_key=input_data.api_key,
        )
    )

    if not summary_result.success:
        return Output(
            video_id=transcript_result.video_id,
            title=title,
            author=author,
            transcript_word_count=transcript_result.word_count,
            auto_generated_captions=transcript_result.auto_generated,
            success=False,
            error_message=f"Failed to generate summary: {summary_result.error_message}",
        )

    return Output(
        summary=summary_result.summary,
        video_id=transcript_result.video_id,
        title=title,
        author=author,
        transcript_word_count=transcript_result.word_count,
        summary_word_count=summary_result.summary_length,
        model_used=summary_result.model_used,
        auto_generated_captions=transcript_result.auto_generated,
        success=True,
    )
