from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

from openclaw_memory.core.plasticity import clip_weight, stdp_delta
from openclaw_memory.schemas.memory import Engram


@dataclass(slots=True)
class Edge:
    source: str
    target: str
    weight: float
    updated_at: datetime


class EngramGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Engram] = {}
        self.adj: dict[str, dict[str, Edge]] = defaultdict(dict)

    def upsert_node(self, engram: Engram) -> None:
        self.nodes[engram.id] = engram

    def connect(self, source: str, target: str, weight: float = 0.1) -> None:
        now = datetime.now(timezone.utc)
        self.adj[source][target] = Edge(source=source, target=target, weight=weight, updated_at=now)

    def update_synapse(
        self,
        source: str,
        target: str,
        activation_i: float,
        activation_j: float,
        dt_seconds: float,
        interference_penalty: float = 0.0,
    ) -> float:
        edge = self.adj[source].get(target)
        old = edge.weight if edge else 0.0
        delta = stdp_delta(
            activation_i=activation_i,
            activation_j=activation_j,
            dt_seconds=dt_seconds,
            interference_penalty=interference_penalty,
        )
        new_weight = clip_weight(old + delta)
        self.connect(source, target, new_weight)
        return new_weight

    def spread_activation(self, seed_ids: list[str], steps: int = 2) -> dict[str, float]:
        scores = {seed: 1.0 for seed in seed_ids if seed in self.nodes}
        for _ in range(steps):
            updates: dict[str, float] = defaultdict(float)
            for node_id, score in scores.items():
                for neighbor, edge in self.adj.get(node_id, {}).items():
                    updates[neighbor] += max(0.0, score * edge.weight)
            for key, value in updates.items():
                scores[key] = max(scores.get(key, 0.0), value)
        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    def decay_edges(self, decay_rate: float = 0.01) -> int:
        decayed = 0
        for source, targets in self.adj.items():
            for target, edge in targets.items():
                new_weight = clip_weight(edge.weight * (1 - decay_rate))
                if new_weight != edge.weight:
                    decayed += 1
                self.adj[source][target] = Edge(
                    source=edge.source,
                    target=edge.target,
                    weight=new_weight,
                    updated_at=datetime.now(timezone.utc),
                )
        return decayed

    def prune_edges(self, min_abs_weight: float = 0.05) -> int:
        removed = 0
        for source in list(self.adj.keys()):
            for target in list(self.adj[source].keys()):
                if abs(self.adj[source][target].weight) < min_abs_weight:
                    removed += 1
                    del self.adj[source][target]
        return removed
