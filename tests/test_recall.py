from openclaw_memory.adapters.openclaw_plugin import OpenClawNeuroMemPlugin
from openclaw_memory.schemas.event import Event, QueryContext


def test_retrieve_context_returns_matching_memory() -> None:
    plugin = OpenClawNeuroMemPlugin(low_threshold=0.1, high_threshold=0.9)
    plugin.on_event(Event(content="user likes oolong tea", speaker="user", task_id="t1", feedback_signal=0.1))
    result = plugin.retrieve_context(QueryContext(query="oolong", task_id="t1", top_k=3))
    assert result.snippets
    assert "oolong" in result.snippets[0]
