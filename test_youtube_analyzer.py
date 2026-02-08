"""Test script for YouTube analyzer tool."""

from tools.youtube_analyzer import Input, execute


def test_valid_url():
    """Test with a valid YouTube URL."""
    print("Testing with valid YouTube URL...")
    data = Input(url="https://www.youtube.com/watch?v=l8MESrQgdiI")
    result = execute(data)
    print(result.model_dump_json(indent=2))
    print()


def test_short_url():
    """Test with a shortened youtu.be URL."""
    print("Testing with shortened URL...")
    data = Input(url="https://youtu.be/l8MESrQgdiI")
    result = execute(data)
    print(result.model_dump_json(indent=2))
    print()


def test_invalid_url():
    """Test with an invalid URL."""
    print("Testing with invalid URL...")
    data = Input(url="https://invalid.com/watch?v=123")
    result = execute(data)
    print(result.model_dump_json(indent=2))
    print()


def test_nonexistent_video():
    """Test with a nonexistent video ID."""
    print("Testing with nonexistent video...")
    data = Input(url="https://www.youtube.com/watch?v=invalidvideoid123")
    result = execute(data)
    print(result.model_dump_json(indent=2))
    print()


if __name__ == "__main__":
    test_valid_url()
    test_short_url()
    test_invalid_url()
    test_nonexistent_video()
