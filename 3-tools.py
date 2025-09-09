import json
import requests
from openai import OpenAI


def obter_cotacao_acao(simbolo: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}",
        headers=headers,
    )
    data = response.json()
    resultado = data["chart"]["result"][0]
    meta = resultado["meta"]
    preco = meta["regularMarketPrice"]
    nome = meta.get("longName", simbolo)
    return f"{nome} ({simbolo}): ${preco:.2f}"


def chamar_funcao(nome: str, argumentos: dict) -> str:
    if nome == "obter_cotacao_acao":
        return obter_cotacao_acao(**argumentos)
    raise ValueError(f"Função desconhecida: {nome}")


def inteligencia_com_ferramentas(prompt: str) -> str:
    client = OpenAI()

    ferramentas = [
        {
            "type": "function",
            "name": "obter_cotacao_acao",
            "description": "Obtém cotação atual de uma ação da bolsa de valores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "simbolo": {"type": "string"},
                },
                "required": ["simbolo"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]

    mensagens = [{"role": "user", "content": prompt}]

    # Passo 1: Chamar modelo com ferramentas
    response = client.responses.create(
        model="gpt-4o-mini",
        input=mensagens,
        tools=ferramentas,
    )

    # Passo 2: Verificar e executar chamadas de função
    for tool_call in response.output:
        if tool_call.type == "function_call":
            nome = tool_call.name
            argumentos = json.loads(tool_call.arguments)
            resultado = chamar_funcao(nome, argumentos)

            # Adiciona chamada e resultado no histórico
            mensagens.append(tool_call)
            mensagens.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(resultado),
                }
            )

    # Passo 3: Obter resposta final
    resposta_final = client.responses.create(
        model="gpt-4o-mini",
        input=mensagens,
        tools=ferramentas,
    )

    return resposta_final.output_text


if __name__ == "__main__":
    resultado = inteligencia_com_ferramentas("Qual é o preço da ação da Apple?")
    print("Resultado com Ferramentas:")
    print(resultado)
