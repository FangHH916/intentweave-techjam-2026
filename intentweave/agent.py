from __future__ import annotations

from pathlib import Path

from .retrieval import HybridRetriever
from .state import SessionState


class Agent:
    """Offline hybrid agent implementing the official TechJam interface."""

    def __init__(self, catalog_path: str | Path = "data/catalog.jsonl") -> None:
        self.retriever = HybridRetriever(Path(catalog_path))
        self.sessions: dict[str, SessionState] = {}

    def reset(self, session_id: str, user_profile: dict) -> None:
        self.sessions[session_id] = SessionState(session_id=session_id, user_profile=dict(user_profile or {}))

    def respond(self, session_id: str, user_message: str, turn: int, top_k: int) -> dict:
        if session_id not in self.sessions:
            raise RuntimeError("reset must be called before respond")
        state = self.sessions[session_id]
        state.update(user_message)
        recommendations = self.retriever.search(
            messages=state.messages, signals=state.signals, constraints=state.constraints,
            goal=state.goal, profile_terms=state.profile_terms,
            top_k=min(10, max(1, int(top_k))),
        )
        ask_attribute, message = self._clarification(state, turn, len(recommendations))
        if ask_attribute:
            state.asked_attributes.append(ask_attribute)
        return {
            "message": message,
            "ask_attribute": ask_attribute,
            "recommendations": recommendations,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
        }

    @staticmethod
    def _clarification(state: SessionState, turn: int, candidate_count: int) -> tuple[str | None, str]:
        if turn >= 10:
            return None, "These are the strongest matches for your current requirements."
        if not state.constraints:
            return "other", "What is the single most important requirement or use case for you?"
        if len(state.constraints) < 4 or candidate_count >= 10:
            return "other", "What remaining requirement would best distinguish the right option?"
        return "other", "Is there one final must-have requirement I should prioritize?"
