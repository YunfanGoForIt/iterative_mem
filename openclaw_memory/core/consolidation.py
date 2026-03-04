from __future__ import annotations

from collections import deque

from openclaw_memory.core.engram_graph import EngramGraph
from openclaw_memory.schemas.memory import Engram


class ReplayConsolidator:
    def __init__(self) -> None:
        self.queue: deque[Engram] = deque()

    def enqueue(self, engram: Engram) -> None:
        self.queue.append(engram)

    def consolidate(self, graph: EngramGraph, limit: int = 20) -> int:
        consolidated = 0
        while self.queue and consolidated < limit:
            current = self.queue.popleft()
            graph.upsert_node(current)
            for existing in list(graph.nodes.values()):
                if existing.id == current.id:
                    continue
                if existing.task_id == current.task_id:
                    graph.connect(existing.id, current.id, weight=min(1.0, (existing.salience + current.salience) / 2))
            consolidated += 1
        return consolidated
