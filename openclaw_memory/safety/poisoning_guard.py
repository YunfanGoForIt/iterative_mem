from __future__ import annotations

from openclaw_memory.schemas.event import Event

DANGEROUS_PATTERNS = [
    "ignore previous instructions",
    "store this forever",
    "exfiltrate",
    "system prompt",
]


def is_poisonous(event: Event) -> bool:
    content = event.content.lower()
    return any(pattern in content for pattern in DANGEROUS_PATTERNS)


def trust_from_source(event: Event) -> float:
    if event.speaker == "user":
        return 0.8
    if event.speaker == "tool":
        return 0.9
    if event.speaker == "assistant":
        return 0.6
    return 0.5
