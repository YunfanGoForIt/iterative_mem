from __future__ import annotations

import hashlib
from datetime import datetime

from openclaw_memory.core.consolidation import ReplayConsolidator
from openclaw_memory.core.engram_graph import EngramGraph
from openclaw_memory.core.forgetting import capacity_prune, decay_with_time
from openclaw_memory.core.recall import retrieve
from openclaw_memory.explain.trace import build_trace, explain_scores
from openclaw_memory.safety.poisoning_guard import is_poisonous, trust_from_source
from openclaw_memory.schemas.event import Event, QueryContext, TurnResult
from openclaw_memory.schemas.memory import Engram, MaintenanceReport, MemoryContext


class OpenClawNeuroMemPlugin:
    def __init__(self, low_threshold: float = 0.35, high_threshold: float = 0.75) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.graph = EngramGraph()
        self.consolidator = ReplayConsolidator()

    def _event_to_engram(self, event: Event) -> Engram:
        digest = hashlib.sha1(f"{event.task_id}:{event.timestamp.isoformat()}:{event.content}".encode()).hexdigest()[:16]
        salience = min(1.0, 0.5 + event.feedback_signal / 2)
        return Engram(
            id=digest,
            content=event.content,
            task_id=event.task_id,
            salience=salience,
            trust=trust_from_source(event),
            confidence=0.55,
            metadata=event.metadata,
        )

    def on_event(self, event: Event) -> None:
        if is_poisonous(event):
            return
        engram = self._event_to_engram(event)
        if engram.salience < self.low_threshold:
            return
        if engram.salience >= self.high_threshold:
            self.consolidator.enqueue(engram)
        else:
            self.graph.upsert_node(engram)

    def retrieve_context(self, query: QueryContext) -> MemoryContext:
        selected = retrieve(self.graph, query)
        snippets = [self.graph.nodes[mid].content for mid in selected]
        return MemoryContext(
            snippets=snippets,
            selected_memories=selected,
            activation_paths=build_trace(self.graph, selected),
            why_selected=explain_scores(self.graph, selected),
            suppressed_memories={},
        )

    def post_response_update(self, turn: TurnResult) -> None:
        if turn.reward <= 0:
            return
        q = QueryContext(query=turn.query, task_id="default", top_k=3)
        selected = retrieve(self.graph, q)
        for node_id in selected:
            node = self.graph.nodes[node_id]
            node.confidence = min(1.0, node.confidence + turn.reward * 0.1)

    def run_maintenance(self, now: datetime) -> MaintenanceReport:
        consolidated = self.consolidator.consolidate(self.graph)
        decayed = decay_with_time(self.graph, lambda_rate=0.02)
        pruned = self.graph.prune_edges(min_abs_weight=0.03)
        capacity_prune(self.graph, max_nodes=1000)
        return MaintenanceReport(consolidated=consolidated, pruned_edges=pruned, decayed_edges=decayed)
