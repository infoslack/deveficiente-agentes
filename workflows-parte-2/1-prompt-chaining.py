from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"


class ExtracaoEvento(BaseModel):
    """Primeira chamada LLM: Extrair informações básicas do evento"""

    descricao: str = Field(description="Descrição bruta do evento")
    eh_evento_calendario: bool = Field(
        description="Se este texto descreve um evento de calendário"
    )
    pontuacao_confianca: float = Field(description="Pontuação de confiança entre 0 e 1")


class DetalhesEvento(BaseModel):
    """Segunda chamada LLM: Analisar detalhes específicos do evento"""

    nome: str = Field(description="Nome do evento")
    data: str = Field(
        description="Data e hora do evento. Use formato ISO 8601 para este valor."
    )
    duracao_minutos: int = Field(description="Duração esperada em minutos")
    participantes: list[str] = Field(description="Lista de participantes")


class ConfirmacaoEvento(BaseModel):
    """Terceira chamada LLM: Gerar mensagem de confirmação"""

    mensagem_confirmacao: str = Field(
        description="Mensagem de confirmação em linguagem natural"
    )
    link_calendario: Optional[str] = Field(
        description="Link do calendário gerado se aplicável"
    )


def extrair_informacao_evento(entrada_usuario: str) -> ExtracaoEvento:
    """Primeira chamada LLM para determinar se a entrada é um evento de calendário"""
    logger.info("Iniciando análise de extração de evento")
    logger.debug(f"Texto de entrada: {entrada_usuario}")

    hoje = datetime.now()
    contexto_data = f"Hoje é {hoje.strftime('%A, %d de %B de %Y')}."

    response = client.responses.parse(
        model=modelo,
        input=f"{contexto_data} Analise se o texto descreve um evento de calendário.",
        instructions=f"Extraia informações sobre um possível evento deste texto: '{entrada_usuario}'",
        text_format=ExtracaoEvento,
    )

    resultado = response.output_parsed
    logger.info(
        f"Extração concluída - É evento de calendário: {resultado.eh_evento_calendario}, Confiança: {resultado.pontuacao_confianca:.2f}"
    )
    return resultado


def analisar_detalhes_evento(descricao: str) -> DetalhesEvento:
    """Segunda chamada LLM para extrair detalhes específicos do evento"""
    logger.info("Iniciando análise de detalhes do evento")

    hoje = datetime.now()
    contexto_data = f"Hoje é {hoje.strftime('%A, %d de %B de %Y')}."

    response = client.responses.parse(
        model=modelo,
        input=f"{contexto_data} Extraia informações detalhadas do evento. Quando as datas fizerem referência a 'próxima terça-feira' ou datas relativas similares, use a data atual como referência.",
        instructions=f"Extraia detalhes estruturados deste texto de evento: '{descricao}'",
        text_format=DetalhesEvento,
    )

    resultado = response.output_parsed
    logger.info(
        f"Detalhes do evento analisados - Nome: {resultado.nome}, Data: {resultado.data}, Duração: {resultado.duracao_minutos}min"
    )
    logger.debug(f"Participantes: {', '.join(resultado.participantes)}")
    return resultado


def gerar_confirmacao(detalhes_evento: DetalhesEvento) -> ConfirmacaoEvento:
    """Terceira chamada LLM para gerar mensagem de confirmação"""
    logger.info("Gerando mensagem de confirmação")

    response = client.responses.parse(
        model=modelo,
        input="Gere uma mensagem de confirmação natural para o evento. Assine a mensagem com seu nome: Skynet",
        instructions=f"Crie uma confirmação para este evento: {detalhes_evento.model_dump()}",
        text_format=ConfirmacaoEvento,
    )

    resultado = response.output_parsed
    logger.info("Mensagem de confirmação gerada com sucesso")
    return resultado


def processar_solicitacao_calendario(
    entrada_usuario: str,
) -> Optional[ConfirmacaoEvento]:
    """Função principal implementando a cadeia de prompts com verificação de porta"""
    logger.info("Processando solicitação de calendário")
    logger.debug(f"Entrada bruta: {entrada_usuario}")

    # Primeira chamada LLM: Extrair informações básicas
    extracao_inicial = extrair_informacao_evento(entrada_usuario)

    # Verificação de porta: Verificar se é um evento de calendário com confiança suficiente
    if (
        not extracao_inicial.eh_evento_calendario
        or extracao_inicial.pontuacao_confianca < 0.7
    ):
        logger.warning(
            f"Verificação de porta falhou - eh_evento_calendario: {extracao_inicial.eh_evento_calendario}, confiança: {extracao_inicial.pontuacao_confianca:.2f}"
        )
        return None

    logger.info("Verificação de porta passou, prosseguindo com processamento do evento")

    # Segunda chamada LLM: Obter informações detalhadas do evento
    detalhes_evento = analisar_detalhes_evento(extracao_inicial.descricao)

    # Terceira chamada LLM: Gerar confirmação
    confirmacao = gerar_confirmacao(detalhes_evento)

    logger.info("Processamento da solicitação de calendário concluído com sucesso")
    return confirmacao


# Exemplos de uso
entrada_usuario = "Vamos fazer uma transmissão ao vivo na próxima segunda-feira às 20h com Daniel e Alberto para apresentar o lançamento do novo curso, deve durar umas 2 horas"

resultado = processar_solicitacao_calendario(entrada_usuario)
if resultado:
    print(f"Confirmação: {resultado.mensagem_confirmacao}")
    if resultado.link_calendario:
        print(f"Link do Calendário: {resultado.link_calendario}")
else:
    print("Isto não parece ser uma solicitação de evento de calendário.")

print("\n" + "=" * 50 + "\n")

entrada_usuario = (
    "Você pode enviar um e-mail para Alice e Bob para discutir o roteiro do projeto?"
)

resultado = processar_solicitacao_calendario(entrada_usuario)
if resultado:
    print(f"Confirmação: {resultado.mensagem_confirmacao}")
    if resultado.link_calendario:
        print(f"Link do Calendário: {resultado.link_calendario}")
else:
    print("Isto não parece ser uma solicitação de evento de calendário.")
