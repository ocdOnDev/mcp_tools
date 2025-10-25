"""
Visits a webpage at the given URL and returns its content as Markdown.
"""

import re
import requests
from markdownify import markdownify
from pydantic import BaseModel
from requests.exceptions import RequestException


# Optional: mimic smolagents truncate_content
def truncate_content(content: str, max_length: int = 10000) -> str:
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content


class Input(BaseModel):
    url: str


class Output(BaseModel):
    markdown_content: str


def execute(input_data: Input) -> Output:
    """Fetch a webpage and return markdown text."""
    try:
        response = requests.get(input_data.url, timeout=20)
        response.raise_for_status()

        # Convert HTML to Markdown
        markdown_content = markdownify(response.text).strip()

        # Clean up redundant newlines
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        markdown_content = truncate_content(markdown_content, 10000)
        return Output(markdown_content=markdown_content)

    except requests.exceptions.Timeout:
        return Output(
            markdown_content="The request timed out. Please try again later or check the URL."
        )
    except RequestException as e:
        return Output(markdown_content=f"Error fetching the webpage: {str(e)}")
    except Exception as e:
        return Output(markdown_content=f"An unexpected error occurred: {str(e)}")
