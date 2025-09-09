from openai import OpenAI


def basic_intelligence(prompt: str) -> str:
    client = OpenAI()
    response = client.responses.create(model="gpt-4o-mini", input=prompt)
    return response.output_text


if __name__ == "__main__":
    result = basic_intelligence(prompt="O que é inteligência artificial?")
    print("Basic Output:")
    print(result)
