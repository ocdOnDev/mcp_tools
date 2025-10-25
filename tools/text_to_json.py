"""transforms text to json  using pydantic.

This tool reads a text string and transforms it into a structured JSON format.
"""

import json
from pydantic import BaseModel


class Input(BaseModel):
    text: str


class Output(BaseModel):
    json_data: dict


def execute(input_data: Input) -> Output:
    try:
        result = json.loads(input_data.text)
    except Exception as e:
        result = {"error": str(e)}
    return Output(json_data=result)
