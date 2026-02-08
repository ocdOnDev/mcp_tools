"""Summarizes text using a local Ollama LLM.

This tool sends text to a locally running Ollama instance for summarization.
Requires Ollama to be installed and running. No API key or external service needed.
"""

import requests
from pydantic import BaseModel


class Input(BaseModel):
    text: str
    model: str = "gemma:latest"
    summary_length: str = "medium"
    ollama_url: str = "http://localhost:11434"


class Output(BaseModel):
    summary: str = ""
    model_used: str = ""
    input_length: int = 0
    summary_length: int = 0
    success: bool = True
    error_message: str = ""


def truncate_text(text: str, max_words: int = 4000) -> str:
    """Truncate text to prevent overwhelming the LLM.

    Most local models have context limits around 2048-8192 tokens.
    4000 words ≈ 5300 tokens, leaving room for system prompt and response.
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

    prompt = f"""Please summarize the following text. {instruction}

Text to summarize:
{text}

Summary:"""

    return prompt


def check_ollama_availability(ollama_url: str) -> tuple[bool, str]:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True, ""
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama. Is it running? (Try: ollama serve)"
    except requests.exceptions.Timeout:
        return False, "Ollama connection timed out."
    except Exception as e:
        return False, f"Ollama connection error: {str(e)}"


def check_model_exists(ollama_url: str, model_name: str) -> tuple[bool, list[str]]:
    """Check if the specified model is available in Ollama."""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        available_models = [model["name"] for model in data.get("models", [])]
        model_exists = model_name in available_models
        return model_exists, available_models
    except Exception:
        return False, []


def summarize_with_ollama(
    text: str, model: str, ollama_url: str, summary_length: str
) -> str:
    """Call Ollama API to generate summary."""
    prompt = build_prompt(text, summary_length)

    response = requests.post(
        f"{ollama_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=300,  # 5 minutes max for local generation
    )
    response.raise_for_status()

    result = response.json()
    return result.get("response", "").strip()


def execute(input_data: Input) -> Output:
    """Summarize text using local Ollama LLM.

    Validates Ollama availability, checks model exists, and generates summary.
    """
    # Validate summary_length
    valid_lengths = ["brief", "medium", "detailed"]
    if input_data.summary_length not in valid_lengths:
        return Output(
            success=False,
            error_message=f"Invalid summary_length. Must be one of: {', '.join(valid_lengths)}",
        )

    # Check if Ollama is running
    is_available, error_msg = check_ollama_availability(input_data.ollama_url)
    if not is_available:
        return Output(success=False, error_message=error_msg)

    # Check if model exists
    model_exists, available_models = check_model_exists(
        input_data.ollama_url, input_data.model
    )
    if not model_exists:
        models_str = ", ".join(available_models) if available_models else "none"
        return Output(
            success=False,
            error_message=f"Model '{input_data.model}' not found. Available models: {models_str}. "
            f"Install with: ollama pull {input_data.model}",
        )

    # Truncate text if too long
    original_length = len(input_data.text.split())
    truncated_text = truncate_text(input_data.text)

    try:
        # Generate summary
        summary = summarize_with_ollama(
            truncated_text,
            input_data.model,
            input_data.ollama_url,
            input_data.summary_length,
        )

        summary_word_count = len(summary.split())

        return Output(
            summary=summary,
            model_used=input_data.model,
            input_length=original_length,
            summary_length=summary_word_count,
            success=True,
            error_message="",
        )

    except requests.exceptions.Timeout:
        return Output(
            success=False,
            error_message="Ollama request timed out. The text might be too long or the model is slow.",
        )

    except requests.exceptions.HTTPError as e:
        return Output(
            success=False,
            error_message=f"Ollama HTTP error: {str(e)}",
        )

    except Exception as e:
        return Output(
            success=False,
            error_message=f"An unexpected error occurred: {str(e)}",
        )
