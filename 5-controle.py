from openai import OpenAI
from pydantic import BaseModel
from typing import Literal


class ClassificacaoIntencao(BaseModel):
    intencao: Literal["pergunta", "solicitacao", "reclamacao"]
    confianca: float
    raciocinio: str


def roteamento_por_intencao(entrada_usuario: str) -> tuple[str, ClassificacaoIntencao]:
    client = OpenAI()
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "Classifique a entrada do usuário em uma das três categorias: "
                    "pergunta, solicitacao ou reclamacao. Forneça seu raciocínio e nível de confiança."
                ),
            },
            {"role": "user", "content": entrada_usuario},
        ],
        text_format=ClassificacaoIntencao,
    )

    classificacao = response.output_parsed
    intencao = classificacao.intencao

    if intencao == "pergunta":
        resultado = responder_pergunta(entrada_usuario)
    elif intencao == "solicitacao":
        resultado = processar_solicitacao(entrada_usuario)
    elif intencao == "reclamacao":
        resultado = tratar_reclamacao(entrada_usuario)
    else:
        resultado = "Não sei como ajudar com isso."

    return resultado, classificacao


def responder_pergunta(pergunta: str) -> str:
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o", input=f"Responda a seguinte pergunta: {pergunta}"
    )
    return response.output_text


def processar_solicitacao(solicitacao: str) -> str:
    return f"Processando sua solicitação: {solicitacao}"


def tratar_reclamacao(reclamacao: str) -> str:
    return f"Entendo sua preocupação sobre: {reclamacao}. Vou encaminhar para análise."


if __name__ == "__main__":
    entradas_teste = [
        "O que é machine learning?",
        "Por favor, agende uma reunião para amanhã",
        "Não estou satisfeito com a qualidade do serviço",
    ]

    for entrada in entradas_teste:
        print(f"\nEntrada: {entrada}")
        resultado, classificacao = roteamento_por_intencao(entrada)
        print(
            f"Intenção: {classificacao.intencao} (confiança: {classificacao.confianca})"
        )
        print(f"Raciocínio: {classificacao.raciocinio}")
        print(f"Resposta: {resultado}")
