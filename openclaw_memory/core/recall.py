from __future__ import annotations

from openclaw_memory.core.engram_graph import EngramGraph
from openclaw_memory.core.forgetting import mark_accessed
from openclaw_memory.schemas.event import QueryContext


def lexical_seed_nodes(graph: EngramGraph, query: str, task_id: str) -> list[str]:
    q = query.lower()
    return [
        node.id
        for node in graph.nodes.values()
        if node.task_id == task_id and any(token in node.content.lower() for token in q.split())
    ]


def retrieve(graph: EngramGraph, query_context: QueryContext) -> list[str]:
    seeds = lexical_seed_nodes(graph, query_context.query, query_context.task_id)
    ranked = graph.spread_activation(seeds)
    top = list(ranked.keys())[: query_context.top_k]
    for node_id in top:
        mark_accessed(graph, node_id)
    return top
