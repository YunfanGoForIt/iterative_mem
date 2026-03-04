from openclaw_memory.adapters.openclaw_plugin import OpenClawNeuroMemPlugin
from openclaw_memory.schemas.event import Event, QueryContext, TurnResult


def test_post_response_update_increases_confidence_on_reward() -> None:
    plugin = OpenClawNeuroMemPlugin(low_threshold=0.1, high_threshold=0.95)
    plugin.on_event(Event(content="project codename is atlas", speaker="assistant", task_id="default", feedback_signal=0.2))
    before = plugin.retrieve_context(QueryContext(query="atlas", task_id="default", top_k=1)).selected_memories[0]
    confidence_before = plugin.graph.nodes[before].confidence
    plugin.post_response_update(TurnResult(query="atlas", response="ok", reward=1.0))
    confidence_after = plugin.graph.nodes[before].confidence
    assert confidence_after > confidence_before
