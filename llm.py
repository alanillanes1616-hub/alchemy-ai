"""
llm.py — Wrapper sobre ChatGoogleGenerativeAI.

Centraliza la creación del LLM y expone invoke con manejo de errores.
"""

from __future__ import annotations

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from utils import get_logger

logger = get_logger("llm")


# ── Configuración del LLM ─────────────────────────────────────────────────────

class LLMConfig:
    """Parámetros de configuración del LLM."""

    def __init__(
        self,
        model: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        top_k: int,
        api_key: str,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.api_key = api_key

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LLMConfig):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


# ── Factory ───────────────────────────────────────────────────────────────────

def build_llm(cfg: LLMConfig) -> ChatGoogleGenerativeAI:
    """
    Crea una instancia de ChatGoogleGenerativeAI con la configuración dada.

    Args:
        cfg: Parámetros del modelo.

    Returns:
        Instancia configurada de ChatGoogleGenerativeAI.
    """
    logger.info("Building LLM: %s (temp=%.2f)", cfg.model, cfg.temperature)
    return ChatGoogleGenerativeAI(
        model=cfg.model,
        google_api_key=cfg.api_key,
        temperature=cfg.temperature,
        max_output_tokens=cfg.max_tokens,
        top_p=cfg.top_p,
        top_k=cfg.top_k,
        convert_system_message_to_human=True,
    )


# ── Invocación con manejo de errores ──────────────────────────────────────────

def invoke(llm: ChatGoogleGenerativeAI, messages: list[BaseMessage]) -> str:
    """
    Invoca el LLM con la lista de mensajes y devuelve el contenido de texto.

    Args:
        llm:      Instancia de ChatGoogleGenerativeAI.
        messages: Lista de BaseMessage (System + historial + pregunta actual).

    Returns:
        Respuesta como string. En caso de error, devuelve mensaje de error amigable.
    """
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as exc:
        logger.error("LLM invocation error: %s", exc)
        return (
            f"Error al contactar el modelo: {exc}\n\n"
            "Verifica que tu API key sea válida y que el modelo esté disponible."
        )