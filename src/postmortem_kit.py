
"""Incident postmortem kit.

Good postmortems have a shape: a sorted timeline of what happened,
a five-whys chain digging at root cause, and action items with owners
and due dates. This kit builds that shape in code and renders it to
markdown for the final document.

Design:
- Events insert sorted by timestamp: the timeline is always ordered no
  matter what order facts arrive in.
- The five-whys chain is a list of (why, because) pairs; depth()
  reports how deep the analysis went (five is the aspiration, not a
  requirement).
- Action items track done/open; open_actions() drives the follow-up
  meeting.
- to_markdown() renders the canonical postmortem sections in one pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TimelineEvent:
    """One timestamped fact."""
    ts: datetime
    actor: str
    event: str


@dataclass
class ActionItem:
    """One follow-up action."""
    action_id: str
    description: str
    owner: str
    due: str
    done: bool = False


class Postmortem:
    """A postmortem document under construction."""

    def __init__(self, incident_id, title):
        self.incident_id = incident_id
        self.title = title
        self._events = []
        self._whys = []
        self._actions = {}

    def add_event(self, ts, actor, event):
        """Add a timeline event (kept sorted by timestamp)."""
        if not isinstance(ts, datetime):
            raise TypeError("ts must be a datetime")
        record = TimelineEvent(ts, actor, event)
        self._events.append(record)
        self._events.sort(key=lambda e: e.ts)
        return record

    def timeline(self):
        return list(self._events)

    def add_why(self, why, because):
        """Append one five-whys link."""
        self._whys.append((why, because))
        return (why, because)

    def why_chain(self):
        return list(self._whys)

    def depth(self):
        return len(self._whys)

    def root_cause(self):
        """The deepest 'because': the current best root-cause statement."""
        return self._whys[-1][1] if self._whys else None

    def add_action(self, action):
        if action.action_id in self._actions:
            raise ValueError("duplicate action_id %r" % (action.action_id,))
        self._actions[action.action_id] = action
        return action

    def complete_action(self, action_id):
        try:
            action = self._actions[action_id]
        except KeyError:
            raise KeyError("unknown action_id %r" % (action_id,))
        action.done = True
        return action

    def open_actions(self):
        return sorted((a for a in self._actions.values() if not a.done),
                      key=lambda a: a.action_id)

    def action_completion(self):
        total = len(self._actions)
        if not total:
            return 1.0
        done = sum(1 for a in self._actions.values() if a.done)
        return round(done / total, 3)

    def to_markdown(self):
        lines = ["# Postmortem: %s" % self.title,
                 "Incident: %s" % self.incident_id,
                 "", "## Timeline", ""]
        for event in self._events:
            lines.append("- %s | %s: %s" % (
                event.ts.strftime("%Y-%m-%d %H:%M"), event.actor, event.event))
        lines += ["", "## Five whys", ""]
        for i, (why, because) in enumerate(self._whys, 1):
            lines.append("%d. Why %s? Because %s." % (i, why, because))
        lines += ["", "## Action items", ""]
        for action in sorted(self._actions.values(), key=lambda a: a.action_id):
            mark = "x" if action.done else " "
            lines.append("- [%s] %s (owner: %s, due: %s)" % (
                mark, action.description, action.owner, action.due))
        return "\n".join(lines)
