from __future__ import annotations

from datetime import datetime, timezone

from openclaw_memory.core.engram_graph import EngramGraph


def decay_with_time(graph: EngramGraph, lambda_rate: float = 0.03) -> int:
    return graph.decay_edges(decay_rate=lambda_rate)


def capacity_prune(graph: EngramGraph, max_nodes: int = 500) -> int:
    if len(graph.nodes) <= max_nodes:
        return 0
    victims = sorted(
        graph.nodes.values(),
        key=lambda n: (n.salience + n.confidence + n.trust + n.recall_count / 10),
    )[: len(graph.nodes) - max_nodes]
    victim_ids = {v.id for v in victims}
    for victim_id in victim_ids:
        del graph.nodes[victim_id]
        graph.adj.pop(victim_id, None)
    for source in list(graph.adj.keys()):
        for target in list(graph.adj[source].keys()):
            if target in victim_ids:
                del graph.adj[source][target]
    return len(victim_ids)


def mark_accessed(graph: EngramGraph, node_id: str) -> None:
    if node_id in graph.nodes:
        node = graph.nodes[node_id]
        node.recall_count += 1
        node.last_accessed = datetime.now(timezone.utc)
