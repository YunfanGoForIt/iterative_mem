from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Event:
    content: str
    speaker: str
    task_id: str
    feedback_signal: float = 0.0
    tool_trace: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class QueryContext:
    query: str
    task_id: str
    top_k: int = 5
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class TurnResult:
    query: str
    response: str
    reward: float = 0.0
    corrections: list[str] = field(default_factory=list)
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
