import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def search_kb(question):
    """Busca respostas na base de conhecimento"""
    with open("kb.json", "r", encoding="utf-8") as f:
        return json.load(f)


tools = [
    {
        "type": "function",
        "name": "search_kb",
        "description": "Busca informações na base de conhecimento para responder perguntas",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "A pergunta do usuário"},
            },
            "required": ["question"],
        },
    }
]


# Modelo de resposta
class KBResponse(BaseModel):
    answer: str = Field(description="Resposta à pergunta do usuário")
    confidence: str = Field(description="Nível de confiança: alto, médio ou baixo")


def answer_question(question):
    system_prompt = """
    Você é um assistente virtual de uma loja online brasileira.
    Responda usando apenas as informações da base de conhecimento.
    Se a pergunta não puder ser respondida com a base, informe educadamente.
    """

    # Primeira chamada para verificar se o modelo quer usar a ferramenta
    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"{system_prompt}\n\nPergunta: {question}",
        tools=tools,
    )

    # Verifica se há chamadas de função
    function_calls = [
        output for output in response.output if output.type == "function_call"
    ]

    if function_calls:
        # Obtém dados da base de conhecimento e gera resposta estruturada
        function_call = function_calls[0]
        args = json.loads(function_call.arguments)
        kb_data = search_kb(args.get("question"))

        final_response = client.responses.parse(
            model="gpt-4o-mini",
            input=f"""
            {system_prompt}

            Pergunta: {question}

            Base de conhecimento:
            {json.dumps(kb_data, ensure_ascii=False)}
            """,
            instructions="Forneça uma resposta estruturada baseada nos dados da base de conhecimento",
            text_format=KBResponse,
        )

        return final_response.output_parsed
    else:
        # Resposta direta se nenhuma ferramenta foi chamada
        direct_text = next(
            (output.value for output in response.output if hasattr(output, "value")),
            next(
                (
                    output.content
                    for output in response.output
                    if hasattr(output, "content")
                ),
                "",
            ),
        )

        return KBResponse(answer=direct_text, confidence="baixo")


# Exemplos
question1 = "Qual é a política de devoluções da loja?"
response1 = answer_question(question1)
print(f"\n----- {question1}")
print(f"Resposta: {response1.answer}")
print(f"Confiança: {response1.confidence}")

question2 = "Vocês entregam para o Nordeste?"
response2 = answer_question(question2)
print(f"\n----- {question2}")
print(f"Resposta: {response2.answer}")
print(f"Confiança: {response2.confidence}")

question3 = "Qual a capital da França?"
response3 = answer_question(question3)
print(f"\n----- {question3}")
print(f"Resposta: {response3.answer}")
print(f"Confiança: {response3.confidence}")
