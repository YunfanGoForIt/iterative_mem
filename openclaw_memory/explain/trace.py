from __future__ import annotations

from openclaw_memory.core.engram_graph import EngramGraph


def build_trace(graph: EngramGraph, selected: list[str]) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    selected_set = set(selected)
    for source in selected:
        for target in graph.adj.get(source, {}):
            if target in selected_set:
                paths.append((source, target))
    return paths


def explain_scores(graph: EngramGraph, selected: list[str]) -> dict[str, dict[str, float]]:
    response: dict[str, dict[str, float]] = {}
    for node_id in selected:
        node = graph.nodes[node_id]
        response[node_id] = {
            "salience": node.salience,
            "confidence": node.confidence,
            "trust": node.trust,
            "recall_count": float(node.recall_count),
        }
    return response
