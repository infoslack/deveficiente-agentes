"""
Feedback Humano, fornece pontos estratégicos onde julgamento humano é necessário.
Este componente implementa fluxos de aprovação e processos human-in-the-loop
para decisões de risco ou julgamentos complexos.
"""

from openai import OpenAI


def obter_aprovacao_humana(conteudo: str) -> bool:
    print(f"Conteúdo gerado:\n{conteudo}\n")
    resposta = input("Aprovar isso? (s/n): ")
    return resposta.lower().startswith("s")


def inteligencia_com_feedback_humano(prompt: str) -> None:
    client = OpenAI()

    response = client.responses.create(model="gpt-4o-mini", input=prompt)
    rascunho_resposta = response.output_text

    if obter_aprovacao_humana(rascunho_resposta):
        print("Resposta final aprovada")
    else:
        print("Resposta não aprovada")


if __name__ == "__main__":
    inteligencia_com_feedback_humano("De forma simples fale o que é machine learning")
