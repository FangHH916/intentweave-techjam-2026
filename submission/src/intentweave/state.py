from __future__ import annotations

from dataclasses import dataclass, field
import re


ALLOWED_ATTRIBUTES = {
    "category", "material", "color", "size", "style", "brand",
    "budget", "feature", "use_case", "other",
}


def extract_signal(message: str) -> str:
    """Remove conversational boilerplate while preserving product evidence."""
    value = message.strip()
    lowered = value.lower()
    markers = ("a key requirement is:", "for that, what matters is:", "what i need is:")
    for marker in markers:
        if marker in lowered:
            value = value[lowered.index(marker) + len(marker):]
            break
    else:
        value = re.sub(r"^i(?:'m| am) looking for\s+", "", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip(" .;,\t")


def split_constraints(signal: str) -> list[str]:
    return [part.strip(" .;,\t") for part in signal.split(";") if part.strip(" .;,\t")]


@dataclass
class SessionState:
    session_id: str
    user_profile: dict
    messages: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    asked_attributes: list[str] = field(default_factory=list)
    rejected_attributes: set[str] = field(default_factory=set)
    intent: str = "browsing"
    override_count: int = 0
    goal: str = ""

    def update(self, message: str) -> None:
        self.messages.append(message)
        lowered = message.lower()
        if not self.goal:
            goal_match = re.search(r"i(?:'m| am) looking for\s+(.+?)(?:\.\s|,\s+but\s|$)", message, re.IGNORECASE)
            if goal_match:
                self.goal = goal_match.group(1).strip(" .;,\t")
        if "key requirement" in lowered or "what matters" in lowered:
            self.intent = "buying"
        if "actually" in lowered and ("ignore" in lowered or "instead" in lowered):
            self.intent = "buying"
            self.override_count += 1
        if "don't have" in lowered and "preference for" in lowered:
            match = re.search(r"preference for\s+([a-z_]+)", lowered)
            if match and match.group(1) in ALLOWED_ATTRIBUTES:
                self.rejected_attributes.add(match.group(1))
            return

        signal = extract_signal(message)
        if not signal or "still exploring" in signal.lower():
            return
        self.signals.append(signal)
        for constraint in split_constraints(signal):
            normalized = constraint.casefold()
            if all(item.casefold() != normalized for item in self.constraints):
                self.constraints.append(constraint)

    @property
    def profile_terms(self) -> list[str]:
        tags = self.user_profile.get("preference_tags") or []
        return [str(tag) for tag in tags if str(tag).strip()]
