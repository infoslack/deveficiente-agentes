from openai import OpenAI

client = OpenAI()


def perguntar_sem_memoria():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Me conte uma piada sobre programação"},
        ],
    )
    return response.choices[0].message.content


def perguntar_continuacao_sem_memoria():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Qual foi minha pergunta anterior?"},
        ],
    )
    return response.choices[0].message.content


def perguntar_continuacao_com_memoria(resposta: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Me conte uma piada sobre programação"},
            {"role": "assistant", "content": resposta},
            {"role": "user", "content": "Qual foi minha pergunta anterior?"},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Primeiro: Pedir uma piada
    resposta_piada = perguntar_sem_memoria()
    print(resposta_piada, "\n")

    # Segundo: Fazer pergunta de acompanhamento sem memória (IA fica confusa)
    resposta_confusa = perguntar_continuacao_sem_memoria()
    print(resposta_confusa, "\n")

    # Terceiro: Fazer pergunta de acompanhamento com memória (IA se lembrará)
    resposta_com_memoria = perguntar_continuacao_com_memoria(resposta_piada)
    print(resposta_com_memoria)
