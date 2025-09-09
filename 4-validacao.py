from openai import OpenAI
from pydantic import BaseModel


class ResultadoTarefa(BaseModel):
    tarefa: str
    concluida: bool
    prioridade: int
    data: str | None = None


def inteligencia_estruturada(prompt: str) -> ResultadoTarefa:
    client = OpenAI()
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": "Extraia da entrada do usuário uma tarefa, seu status (concluída ou não), prioridade (1 = baixa, 2 = média, 3 = alta) e data associada, se houver.",
            },
            {"role": "user", "content": prompt},
        ],
        text_format=ResultadoTarefa,
    )
    return response.output_parsed


if __name__ == "__main__":
    entrada = "Preciso organizar uma live sobre agentes na segunda-feira. É prioridade alta e ainda não concluí."
    resultado = inteligencia_estruturada(entrada)

    print("Saída Estruturada:")
    print(resultado.model_dump_json(indent=2))
    print(f"Tarefa: {resultado.tarefa}")
    print(f"Concluída: {resultado.concluida}")
    print(f"Prioridade: {resultado.prioridade}")
    print(f"Data: {resultado.data}")
