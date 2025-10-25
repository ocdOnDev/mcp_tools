"""Extracts text from a PDF file using PyMuPDF.

This tool reads a PDF from a given file path and returns all textual content
as a single string. Useful for content ingestion, summarization, or indexing.
"""

import fitz  # PyMuPDF
from pydantic import BaseModel


class Input(BaseModel):
    file_path: str


class Output(BaseModel):
    text: str


def execute(input_data: Input) -> Output:
    with fitz.open(input_data.file_path) as pdf:
        text = "".join([page.get_text() for page in pdf])
    return Output(text=text)
