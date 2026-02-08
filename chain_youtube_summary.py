#!/usr/bin/env python3
"""Chain YouTube transcript extraction with Ollama summarization."""

import sys
from invoke_tool import invoke_tool


def get_youtube_summary(url: str, language: str = "en", summary_length: str = "brief"):
    """
    Get a YouTube transcript and summarize it.

    Args:
        url: YouTube video URL
        language: Language code for transcript (default: "en")
        summary_length: "brief", "detailed", or "comprehensive"

    Returns:
        dict: Summary result from Ollama
    """
    # Step 1: Get the transcript
    print(f"Fetching transcript from {url}...")
    transcript_result = invoke_tool(
        "youtube_transcript", {"url": url, "language": language}
    )

    # Check if we got a valid result
    if (
        "result" not in transcript_result
        or "transcript" not in transcript_result["result"]
    ):
        raise ValueError(f"Failed to get transcript: {transcript_result}")

    transcript_text = transcript_result["result"]["transcript"]
    print(f"Transcript retrieved: {len(transcript_text)} characters")

    # Step 2: Summarize the transcript
    print(f"Generating {summary_length} summary...")
    summary_result = invoke_tool(
        "summarize_with_ollama",
        {"text": transcript_text, "summary_length": summary_length},
    )

    return summary_result


if __name__ == "__main__":
    # Example usage
    video_url = "https://www.youtube.com/watch?v=b8ZFmooE2UQ"
    language = "es"

    # Allow command line arguments
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    if len(sys.argv) > 2:
        language = sys.argv[2]

    try:
        result = get_youtube_summary(video_url, language, summary_length="brief")
        print("\n" + "=" * 60)
        print("SUMMARY RESULT:")
        print("=" * 60)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
