from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .schemas import ChatContext, EngineResult


class ChatEngine(ABC):
    """Base protocol for all chatbot engines.

    Each engine handles one intent type and returns structured results
    that feed into the formatter/response builder.
    """

    @abstractmethod
    def handle(self, ctx: ChatContext) -> EngineResult:
        ...

    @classmethod
    def requires_db(cls) -> bool:
        return True

    def actions_for(self, ctx: ChatContext) -> list[dict[str, str]]:
        return []
