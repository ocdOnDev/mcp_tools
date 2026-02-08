"""Analyzes YouTube URLs and extracts video metadata.

This tool retrieves title, author, and thumbnail information from YouTube videos
using the public oEmbed API. No authentication required.
"""

import re

import requests
from pydantic import BaseModel


class Input(BaseModel):
    url: str


class Output(BaseModel):
    title: str = ""
    author: str = ""
    thumbnail_url: str = ""
    provider: str = ""
    success: bool = True
    error_message: str = ""


def is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube video URL.

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r"^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"^https?://youtu\.be/[\w-]+",
        r"^https?://(?:www\.)?youtube\.com/embed/[\w-]+",
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def get_video_metadata(url: str) -> dict:
    """Fetch video metadata from YouTube oEmbed API.

    Uses the public oEmbed endpoint which requires no authentication.
    Returns basic metadata including title, author, and thumbnail.
    """
    oembed_url = "https://www.youtube.com/oembed"
    params = {"url": url, "format": "json"}

    response = requests.get(oembed_url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def execute(input_data: Input) -> Output:
    """Extract video metadata from YouTube URL.

    Validates the URL format and fetches metadata using YouTube's oEmbed API.
    Returns structured information about the video or an error message.
    """
    # Validate YouTube URL format
    if not is_valid_youtube_url(input_data.url):
        return Output(
            success=False,
            error_message="Invalid YouTube URL format. Please provide a valid YouTube video URL.",
        )

    try:
        # Fetch metadata from oEmbed API
        data = get_video_metadata(input_data.url)

        return Output(
            title=data.get("title", ""),
            author=data.get("author_name", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            provider=data.get("provider_name", "YouTube"),
            success=True,
            error_message="",
        )

    except requests.exceptions.Timeout:
        return Output(
            success=False,
            error_message="Request timed out. Please try again later.",
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return Output(
                success=False,
                error_message="Video not found. The video may be private, deleted, or the URL is incorrect.",
            )
        return Output(
            success=False,
            error_message=f"HTTP error occurred: {str(e)}",
        )

    except requests.exceptions.RequestException as e:
        return Output(
            success=False,
            error_message=f"Network error occurred: {str(e)}",
        )

    except Exception as e:
        return Output(
            success=False,
            error_message=f"An unexpected error occurred: {str(e)}",
        )
