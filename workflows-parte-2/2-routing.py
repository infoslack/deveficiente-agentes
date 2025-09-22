from typing import Optional, Literal
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

# --------------------------------------------------------------
# Passo 1: Definir modelos de dados para roteamento e respostas
# --------------------------------------------------------------


class TipoSolicitacaoCalendario(BaseModel):
    """Chamada LLM de roteamento: Determinar o tipo de solicitação de calendário"""

    tipo_solicitacao: Literal["novo_evento", "modificar_evento", "outro"] = Field(
        description="Tipo de solicitação de calendário sendo feita"
    )
    pontuacao_confianca: float = Field(description="Pontuação de confiança entre 0 e 1")
    descricao: str = Field(description="Descrição limpa da solicitação")


class DetalhesNovoEvento(BaseModel):
    """Detalhes para criar um novo evento"""

    nome: str = Field(description="Nome do evento")
    data: str = Field(description="Data e hora do evento (ISO 8601)")
    duracao_minutos: int = Field(description="Duração em minutos")
    participantes: list[str] = Field(description="Lista de participantes")


class Mudanca(BaseModel):
    """Detalhes para alterar um evento existente"""

    campo: str = Field(description="Campo a ser alterado")
    novo_valor: str = Field(description="Novo valor para o campo")


class DetalhesModificarEvento(BaseModel):
    """Detalhes para modificar um evento existente"""

    identificador_evento: str = Field(
        description="Descrição para identificar o evento existente"
    )
    mudancas: list[Mudanca] = Field(description="Lista de mudanças a fazer")
    participantes_adicionar: list[str] = Field(
        description="Novos participantes para adicionar"
    )
    participantes_remover: list[str] = Field(description="Participantes para remover")


class RespostaCalendario(BaseModel):
    """Formato de resposta final"""

    sucesso: bool = Field(description="Se a operação foi bem-sucedida")
    mensagem: str = Field(description="Mensagem de resposta amigável ao usuário")
    link_calendario: Optional[str] = Field(
        description="Link do calendário se aplicável"
    )


# --------------------------------------------------------------
# Passo 2: Definir funções de roteamento e processamento
# --------------------------------------------------------------


def rotear_solicitacao_calendario(entrada_usuario: str) -> TipoSolicitacaoCalendario:
    """Chamada LLM de roteamento para determinar o tipo de solicitação de calendário"""
    logger.info("Roteando solicitação de calendário")

    response = client.responses.parse(
        model=modelo,
        input="Determine se esta é uma solicitação para criar um novo evento de calendário ou modificar um existente.",
        instructions=f"Analise esta solicitação: '{entrada_usuario}'",
        text_format=TipoSolicitacaoCalendario,
    )
    resultado = response.output_parsed
    logger.info(
        f"Solicitação roteada como: {resultado.tipo_solicitacao} com confiança: {resultado.pontuacao_confianca}"
    )
    return resultado


def processar_novo_evento(descricao: str) -> RespostaCalendario:
    """Processar uma solicitação de novo evento"""
    logger.info("Processando solicitação de novo evento")

    # Obter detalhes do evento
    response = client.responses.parse(
        model=modelo,
        input="Extraia detalhes para criar um novo evento de calendário.",
        instructions=f"Extraia informações estruturadas desta descrição: '{descricao}'",
        text_format=DetalhesNovoEvento,
    )
    detalhes = response.output_parsed

    logger.info(f"Novo evento: {detalhes.model_dump_json(indent=2)}")

    # Gerar resposta
    return RespostaCalendario(
        sucesso=True,
        mensagem=f"Criado novo evento '{detalhes.nome}' para {detalhes.data} com {', '.join(detalhes.participantes)}",
        link_calendario=f"calendar://new?event={detalhes.nome}",
    )


def processar_modificar_evento(descricao: str) -> RespostaCalendario:
    """Processar uma solicitação de modificação de evento"""
    logger.info("Processando solicitação de modificação de evento")

    # Obter detalhes de modificação
    response = client.responses.parse(
        model=modelo,
        input="Extraia detalhes para modificar um evento de calendário existente.",
        instructions=f"Extraia informações de modificação desta descrição: '{descricao}'",
        text_format=DetalhesModificarEvento,
    )
    detalhes = response.output_parsed

    logger.info(f"Evento modificado: {detalhes.model_dump_json(indent=2)}")

    # Gerar resposta
    return RespostaCalendario(
        sucesso=True,
        mensagem=f"Modificado evento '{detalhes.identificador_evento}' com as mudanças solicitadas",
        link_calendario=f"calendar://modify?event={detalhes.identificador_evento}",
    )


def processar_solicitacao_calendario(
    entrada_usuario: str,
) -> Optional[RespostaCalendario]:
    """Função principal implementando o fluxo de trabalho de roteamento"""
    logger.info("Processando solicitação de calendário")

    # Rotear a solicitação
    resultado_roteamento = rotear_solicitacao_calendario(entrada_usuario)

    # Verificar limite de confiança
    if resultado_roteamento.pontuacao_confianca < 0.7:
        logger.warning(
            f"Pontuação de confiança baixa: {resultado_roteamento.pontuacao_confianca}"
        )
        return None

    # Rotear para o manipulador apropriado
    if resultado_roteamento.tipo_solicitacao == "novo_evento":
        return processar_novo_evento(resultado_roteamento.descricao)
    elif resultado_roteamento.tipo_solicitacao == "modificar_evento":
        return processar_modificar_evento(resultado_roteamento.descricao)
    else:
        logger.warning("Tipo de solicitação não suportada")
        return None


# --------------------------------------------------------------
# Passo 3: Testar com novo evento
# --------------------------------------------------------------

entrada_novo_evento = (
    "Vamos agendar uma reunião de equipe na próxima terça-feira às 14h com Alice e Bob"
)
resultado = processar_solicitacao_calendario(entrada_novo_evento)
if resultado:
    print(f"Resposta: {resultado.mensagem}")
else:
    print("Solicitação não reconhecida como operação de calendário")

print("\n" + "=" * 50 + "\n")

# --------------------------------------------------------------
# Passo 4: Testar com modificação de evento
# --------------------------------------------------------------

entrada_modificar_evento = (
    "Você pode mover a reunião de equipe com Alice e Bob para quarta-feira às 15h?"
)
resultado = processar_solicitacao_calendario(entrada_modificar_evento)
if resultado:
    print(f"Resposta: {resultado.mensagem}")
else:
    print("Solicitação não reconhecida como operação de calendário")

print("\n" + "=" * 50 + "\n")

# --------------------------------------------------------------
# Passo 5: Testar com solicitação inválida
# --------------------------------------------------------------

entrada_invalida = "Como está o clima hoje?"
resultado = processar_solicitacao_calendario(entrada_invalida)
if not resultado:
    print("Solicitação não reconhecida como operação de calendário")
