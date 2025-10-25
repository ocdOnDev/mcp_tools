"""Gets the weather at a certain location.

This tool retrieves the weather information for a specified location.
"""


from pydantic import BaseModel


class Input(BaseModel):
    location: str


class Output(BaseModel):
    weather: str


# Dummy function
def get_weather(location):
    return f"the weather in {location} is sunny with low temperatures. \n"


def execute(input_data: Input) -> Output:
    return Output(weather=get_weather(input_data.location))
