"""
memory.py — Gestión del historial de conversación.

El historial se almacena en st.session_state y se convierte
a mensajes LangChain para cada invocación del LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from utils import now_str, get_logger

logger = get_logger("memory")

Role = Literal["user", "assistant", "system"]


# ── Modelo de mensaje ─────────────────────────────────────────────────────────

@dataclass
class ChatMessage:
    role: Role
    content: str
    timestamp: str = field(default_factory=now_str)


# ── Gestor de historial ───────────────────────────────────────────────────────

class ConversationMemory:
    """
    Mantiene el historial completo de la conversación y lo convierte
    a la representación esperada por LangChain.
    """

    def __init__(self) -> None:
        self._history: list[ChatMessage] = []

    # ── Escritura ─────────────────────────────────────────────────────────────

    def add_user(self, content: str) -> None:
        self._history.append(ChatMessage(role="user", content=content))

    def add_assistant(self, content: str) -> None:
        self._history.append(ChatMessage(role="assistant", content=content))

    def clear(self) -> None:
        self._history.clear()
        logger.info("Conversation history cleared.")

    # ── Lectura ───────────────────────────────────────────────────────────────

    @property
    def messages(self) -> list[ChatMessage]:
        return list(self._history)

    def is_empty(self) -> bool:
        return len(self._history) == 0

    def __len__(self) -> int:
        return len(self._history)

    # ── Conversión a LangChain ────────────────────────────────────────────────

    def to_langchain(self, system_prompt: str) -> list[BaseMessage]:
        """
        Convierte el historial a una lista de BaseMessage para LangChain.
        El system prompt siempre va primero.

        Args:
            system_prompt: Prompt del sistema construido por prompts.py.

        Returns:
            Lista [SystemMessage, HumanMessage | AIMessage, ...].
        """
        lc: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        for msg in self._history:
            if msg.role == "user":
                lc.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc.append(AIMessage(content=msg.content))
        return lc

    # ── Exportación ───────────────────────────────────────────────────────────

    def to_plain_text(self) -> str:
        """Historial como texto plano para exportación."""
        lines = []
        for msg in self._history:
            label = "Usuario" if msg.role == "user" else "Alchemy AI"
            lines.append(f"[{msg.timestamp}] {label}:\n{msg.content}\n")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Historial en formato Markdown."""
        lines = ["# Conversación — Alchemy AI\n"]
        for msg in self._history:
            label = "**Usuario**" if msg.role == "user" else "**Alchemy AI**"
            lines.append(f"### {label} _{msg.timestamp}_\n\n{msg.content}\n")
        return "\n---\n".join(lines)

