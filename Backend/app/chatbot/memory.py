from __future__ import annotations

from collections import OrderedDict


class ConversationMemory:
    """In-memory conversation history store with LRU eviction.

    Preserves the last N turns per session, capped at M total sessions.
    Thread-safe within a single process (no lock needed for sync use).
    """

    MAX_TURNS = 8
    MAX_SESSIONS = 500

    def __init__(self) -> None:
        self._sessions: OrderedDict[str, list[dict[str, str]]] = OrderedDict()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        history = self._sessions.get(session_id, [])
        if session_id in self._sessions:
            self._sessions.move_to_end(session_id)
        return list(history)

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        history = self._sessions.setdefault(session_id, [])
        history.extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ])
        max_messages = self.MAX_TURNS * 2
        if len(history) > max_messages:
            del history[: len(history) - max_messages]
        self._sessions.move_to_end(session_id)
        while len(self._sessions) > self.MAX_SESSIONS:
            self._sessions.popitem(last=False)

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def get_session_count(self) -> int:
        return len(self._sessions)


memory_store = ConversationMemory()
