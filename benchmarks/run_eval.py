from __future__ import annotations

from dataclasses import dataclass

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openclaw_memory.adapters.openclaw_plugin import OpenClawNeuroMemPlugin
from openclaw_memory.schemas.event import Event, QueryContext


@dataclass
class EvalResult:
    name: str
    passed: bool


def long_term_preference_case() -> EvalResult:
    plugin = OpenClawNeuroMemPlugin(low_threshold=0.1, high_threshold=0.9)
    plugin.on_event(Event(content="I prefer dark mode", speaker="user", task_id="eval", feedback_signal=0.3))
    retrieved = plugin.retrieve_context(QueryContext(query="prefer", task_id="eval", top_k=1)).snippets
    return EvalResult("long_term_preference", bool(retrieved and "dark mode" in retrieved[0]))


if __name__ == "__main__":
    results = [long_term_preference_case()]
    for item in results:
        print(f"{item.name}: {'PASS' if item.passed else 'FAIL'}")
