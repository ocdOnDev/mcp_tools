"""Comprehensive test suite for YouTube tools."""

from tools.youtube_transcript import Input as TranscriptInput
from tools.youtube_transcript import execute as get_transcript
from tools.summarize_with_ollama import Input as SummarizerInput
from tools.summarize_with_ollama import execute as summarize
from tools.youtube_summary import Input as SummaryInput
from tools.youtube_summary import execute as get_summary


def test_transcript():
    """Test transcript extraction."""
    print("=" * 60)
    print("TEST 1: YouTube Transcript Extraction")
    print("=" * 60)

    # Test with a short video that has captions
    data = TranscriptInput(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    result = get_transcript(data)

    print(f"Success: {result.success}")
    print(f"Video ID: {result.video_id}")
    print(f"Language: {result.language}")
    print(f"Auto-generated: {result.auto_generated}")
    print(f"Word count: {result.word_count}")
    print("\nFirst 500 characters of transcript:")
    print(result.transcript[:500] if result.transcript else "No transcript")
    print(f"\nError: {result.error_message}" if result.error_message else "")
    print()


def test_transcript_with_timestamps():
    """Test transcript with timestamp formatting."""
    print("=" * 60)
    print("TEST 2: Transcript with Timestamps")
    print("=" * 60)

    data = TranscriptInput(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", preserve_formatting=True
    )
    result = get_transcript(data)

    print(f"Success: {result.success}")
    print("\nFirst 10 lines with timestamps:")
    lines = result.transcript.split("\n")[:10] if result.transcript else []
    for line in lines:
        print(line)
    print()


def test_ollama_summarizer():
    """Test Ollama summarization with sample text."""
    print("=" * 60)
    print("TEST 3: Ollama Text Summarization")
    print("=" * 60)

    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the
    natural intelligence displayed by humans and animals. Leading AI textbooks define the field
    as the study of "intelligent agents": any device that perceives its environment and takes
    actions that maximize its chance of successfully achieving its goals. Colloquially, the
    term "artificial intelligence" is often used to describe machines (or computers) that mimic
    "cognitive" functions that humans associate with the human mind, such as "learning" and
    "problem solving". As machines become increasingly capable, tasks considered to require
    "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect.
    """

    data = SummarizerInput(text=sample_text, summary_length="brief")
    result = summarize(data)

    print(f"Success: {result.success}")
    print(f"Model used: {result.model_used}")
    print(f"Input length: {result.input_length} words")
    print(f"Summary length: {result.summary_length} words")
    print(f"\nSummary:\n{result.summary}")
    print(f"\nError: {result.error_message}" if result.error_message else "")
    print()


def test_youtube_summary():
    """Test combined YouTube summary (transcript + AI summary)."""
    print("=" * 60)
    print("TEST 4: Complete YouTube Video Summary")
    print("=" * 60)

    # Using a short educational video
    data = SummaryInput(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", summary_length="medium"
    )
    result = get_summary(data)

    print(f"Success: {result.success}")
    print(f"Video ID: {result.video_id}")
    print(f"Title: {result.title}")
    print(f"Author: {result.author}")
    print(f"Transcript words: {result.transcript_word_count}")
    print(f"Summary words: {result.summary_word_count}")
    print(f"Model used: {result.model_used}")
    print(f"Auto-generated captions: {result.auto_generated_captions}")
    print(f"\nAI Summary:\n{result.summary}")
    print(f"\nError: {result.error_message}" if result.error_message else "")
    print()


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)

    # Test 1: Invalid URL
    print("Testing invalid URL...")
    data = TranscriptInput(url="https://invalid.com/video")
    result = get_transcript(data)
    print(f"Expected failure: {not result.success}")
    print(f"Error message: {result.error_message}\n")

    # Test 2: Nonexistent video
    print("Testing nonexistent video...")
    data = TranscriptInput(url="https://www.youtube.com/watch?v=invalidvideoid")
    result = get_transcript(data)
    print(f"Expected failure: {not result.success}")
    print(f"Error message: {result.error_message}\n")

    # Test 3: Invalid model
    print("Testing invalid Ollama model...")
    data = SummarizerInput(text="Test text", model="nonexistent-model:latest")
    result = summarize(data)
    print(f"Expected failure: {not result.success}")
    print(f"Error message: {result.error_message}\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("YOUTUBE TOOLS TEST SUITE")
    print("=" * 60 + "\n")

    # Run all tests
    test_transcript()
    test_transcript_with_timestamps()
    test_ollama_summarizer()
    test_youtube_summary()
    test_error_handling()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
