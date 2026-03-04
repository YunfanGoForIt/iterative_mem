from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Engram:
    id: str
    content: str
    task_id: str
    salience: float
    trust: float = 1.0
    confidence: float = 0.5
    recall_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemoryContext:
    snippets: list[str]
    selected_memories: list[str]
    activation_paths: list[tuple[str, str]]
    why_selected: dict[str, dict[str, float]]
    suppressed_memories: dict[str, str]


@dataclass(slots=True)
class MaintenanceReport:
    consolidated: int
    pruned_edges: int
    decayed_edges: int
