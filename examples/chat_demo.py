import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openclaw_memory.adapters.openclaw_plugin import OpenClawNeuroMemPlugin
from openclaw_memory.schemas.event import Event, QueryContext

plugin = OpenClawNeuroMemPlugin(low_threshold=0.1, high_threshold=0.8)
plugin.on_event(Event(content="My favorite editor is neovim", speaker="user", task_id="demo", feedback_signal=0.7))
plugin.run_maintenance(__import__("datetime").datetime.utcnow())
ctx = plugin.retrieve_context(QueryContext(query="favorite editor", task_id="demo"))
print(ctx.snippets)
