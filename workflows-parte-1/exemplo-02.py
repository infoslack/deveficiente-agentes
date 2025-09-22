import os

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


response = client.responses.parse(
    model="gpt-4o-mini",
    input="Daniel e Alberto vão transmitir uma live na segunda-feira.",
    instructions="Extraia informações do evento.",
    text_format=CalendarEvent,
)

event = response.output_parsed
event.date
event.participants

print(event.model_dump_json(indent=2))
