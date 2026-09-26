# Incident Postmortem Kit

Builds incident postmortems with sorted timelines, five-whys analysis, action items, and markdown rendering.

**Stack:** Python 3.12 · stdlib only · unittest

## Problem

Good postmortems have a shape: a sorted timeline of what happened,
a five-whys chain digging at root cause, and action items with owners
and due dates. This kit builds that shape in code and renders it to
markdown for the final document.

## Design decisions

- Events insert sorted by timestamp: the timeline is always ordered no
- The five-whys chain is a list of (why, because) pairs; depth()
- Action items track done/open; open_actions() drives the follow-up
- to_markdown() renders the canonical postmortem sections in one pass.

## Layout

- `README.md`
- `src/postmortem_kit.py`
- `tests/test_postmortem_kit.py`
- `LICENSE`
- `.gitignore`

## Setup

No third-party dependencies — Python 3.11+ standard library only.

```bash
cd govops-postmortem-kit
python -m unittest discover -s tests -v
```

## Usage

```python
from datetime import datetime
from src.postmortem_kit import ActionItem, Postmortem

pm = Postmortem("INC-42", "Model outage")
pm.add_event(datetime(2026, 5, 2, 10, 1), "monitor", "latency spike")
pm.add_why("did latency spike", "cache was cold")
pm.add_action(ActionItem("A1", "Warm cache on deploy", "amy", "2026-05-20"))
print(pm.to_markdown())
```

## License

MIT — see [LICENSE](LICENSE).
