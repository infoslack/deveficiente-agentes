import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


response = client.responses.create(
    model="gpt-4o-mini",
    input="""Extraia informações do evento do texto e retorne em JSON.
    Texto: Daniel e Alberto vão transmitir uma live na segunda-feira.
EXEMPLO DA FORMATAÇÃO
{
  "formato_saida": {
    "pessoas": ["..."],
    "ação": "...",
    "tipo_evento": "...",
    "data": "..."
  }
}

    """,
)

print(response.output_text)
