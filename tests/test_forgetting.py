from openclaw_memory.core.engram_graph import EngramGraph
from openclaw_memory.core.forgetting import capacity_prune
from openclaw_memory.schemas.memory import Engram


def test_capacity_prune_removes_low_priority_nodes() -> None:
    graph = EngramGraph()
    for i in range(5):
        graph.upsert_node(Engram(id=str(i), content=f"n{i}", task_id="t", salience=0.1 * i, confidence=0.1, trust=0.1))
    removed = capacity_prune(graph, max_nodes=3)
    assert removed == 2
    assert len(graph.nodes) == 3
