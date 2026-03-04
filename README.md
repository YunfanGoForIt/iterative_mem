# OpenClaw NeuroMem (Implementation Scaffold)

Biomimetic memory plugin scaffold for OpenClaw.

## Implemented in this repo
- Engram graph memory model (nodes + weighted synapses)
- STDP-like plasticity update utility
- Replay-based consolidation queue
- Forgetting (decay + capacity pruning)
- OpenClaw plugin adapter hooks:
  - `on_event`
  - `retrieve_context`
  - `post_response_update`
  - `run_maintenance`
- Explainability fields for recall trace
- Poisoning guard for basic memory-injection patterns
- Basic benchmark runner and unit tests

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pytest -q
python examples/chat_demo.py
```
