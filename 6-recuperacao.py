from typing import Optional
from openai import OpenAI
from pydantic import BaseModel


class InfoPessoa(BaseModel):
    nome: str
    telefone: str
    cidade: Optional[str] = None


def inteligencia_resiliente(prompt: str) -> str:
    client = OpenAI()

    # Obter saída estruturada
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": "Extraia informações pessoais do texto fornecido.",
            },
            {"role": "user", "content": prompt},
        ],
        text_format=InfoPessoa,
        temperature=0.0,
    )

    dados_pessoa = response.output_parsed.model_dump()

    try:
        # Tentar acessar o campo cidade e verificar se é válido
        cidade = dados_pessoa["cidade"]
        if cidade is None:
            raise ValueError("Cidade é None")
        info_cidade = f"Pessoa mora em {cidade}"
        return info_cidade

    except (KeyError, TypeError, ValueError):
        print("❌ Cidade não disponível, usando informações de fallback...")

        # Fallback para informações disponíveis
        return f"Contato: {dados_pessoa['nome']} - Telefone: {dados_pessoa['telefone']}"


if __name__ == "__main__":
    resultado = inteligencia_resiliente(
        "Meu nome é Maria Silva e meu telefone é (11) 99999-9999"
    )
    print("Resultado com Recuperação:")
    print(resultado)
