"""
Feedback Humano, fornece pontos estratégicos onde julgamento humano é necessário.
Este componente implementa fluxos de aprovação e processos human-in-the-loop
para decisões de risco ou julgamentos complexos.
"""

from openai import OpenAI


def obter_aprovacao_humana(conteudo: str) -> str:
    print(f"Conteúdo gerado:\n{conteudo}\n")
    resposta = input("Aprovar (s), Refazer (r) ou Cancelar (n): ")

    if resposta.lower().startswith("s"):
        return "aprovado"
    elif resposta.lower().startswith("r"):
        return "refazer"
    else:
        return "cancelado"


def inteligencia_com_feedback_humano(prompt: str) -> None:
    client = OpenAI()

    while True:
        response = client.responses.create(model="gpt-4o-mini", input=prompt)
        rascunho_resposta = response.output_text

        decisao = obter_aprovacao_humana(rascunho_resposta)

        if decisao == "aprovado":
            print("Resposta final aprovada")
            break
        elif decisao == "cancelado":
            print("Resposta não aprovada")
            break
        # Se "refazer", continua o loop
        print("Gerando nova versão...\n")


if __name__ == "__main__":
    inteligencia_com_feedback_humano("De forma simples fale o que é machine learning")
