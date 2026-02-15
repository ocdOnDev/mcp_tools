"""Summarizes text using the Anthropic (Claude) API.

This tool sends text to the Anthropic Messages API for summarization.
Requires an Anthropic API key (via input parameter or ANTHROPIC_API_KEY env var).
"""

import os

import anthropic
from pydantic import BaseModel


class Input(BaseModel):
    text: str
    model: str = "claude-sonnet-4-5-20250929"
    summary_length: str = "medium"
    api_key: str = ""


class Output(BaseModel):
    summary: str = ""
    model_used: str = ""
    input_length: int = 0
    summary_length: int = 0
    success: bool = True
    error_message: str = ""


def truncate_text(text: str, max_words: int = 8000) -> str:
    """Truncate text to stay within context limits.

    Claude models support large contexts, so we allow more than Ollama.
    8000 words ≈ 10K tokens, well within limits.
    """
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text


def build_prompt(text: str, summary_length: str) -> str:
    """Build the summarization prompt based on desired length."""
    length_instructions = {
        "brief": "Provide a brief 2-3 sentence summary.",
        "medium": "Provide a comprehensive summary in 1-2 paragraphs.",
        "detailed": "Provide a detailed summary covering all main points in 3-4 paragraphs.",
    }

    instruction = length_instructions.get(summary_length, length_instructions["medium"])

    return f"""Please summarize the following text. {instruction}

Text to summarize:
{text}"""


def execute(input_data: Input) -> Output:
    """Summarize text using the Anthropic Claude API."""
    valid_lengths = ["brief", "medium", "detailed"]
    if input_data.summary_length not in valid_lengths:
        return Output(
            success=False,
            error_message=f"Invalid summary_length. Must be one of: {', '.join(valid_lengths)}",
        )

    api_key = input_data.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return Output(
            success=False,
            error_message="No API key provided. Set ANTHROPIC_API_KEY env var or pass api_key.",
        )

    original_length = len(input_data.text.split())
    truncated_text = truncate_text(input_data.text)
    prompt = build_prompt(truncated_text, input_data.summary_length)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=input_data.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        summary = message.content[0].text.strip()
        summary_word_count = len(summary.split())

        return Output(
            summary=summary,
            model_used=input_data.model,
            input_length=original_length,
            summary_length=summary_word_count,
            success=True,
        )

    except anthropic.AuthenticationError:
        return Output(
            success=False,
            error_message="Invalid Anthropic API key.",
        )

    except anthropic.RateLimitError:
        return Output(
            success=False,
            error_message="Anthropic rate limit exceeded. Try again later.",
        )

    except anthropic.APIError as e:
        return Output(
            success=False,
            error_message=f"Anthropic API error: {str(e)}",
        )

    except Exception as e:
        return Output(
            success=False,
            error_message=f"An unexpected error occurred: {str(e)}",
        )
