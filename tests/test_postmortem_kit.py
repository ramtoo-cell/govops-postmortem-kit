
"""Tests for the incident postmortem kit."""
import unittest
from datetime import datetime

from src.postmortem_kit import ActionItem, Postmortem


class TestPostmortem(unittest.TestCase):
    def setUp(self):
        self.pm = Postmortem("INC-42", "Model outage")
        self.pm.add_event(datetime(2026, 5, 2, 10, 5), "soc", "alert fired")
        self.pm.add_event(datetime(2026, 5, 2, 10, 1), "monitor", "latency spike")
        self.pm.add_why("did latency spike", "cache was cold")
        self.pm.add_why("was cache cold", "deploy flushed it")
        self.pm.add_action(ActionItem("A1", "Warm cache on deploy", "amy", "2026-05-20"))
        self.pm.add_action(ActionItem("A2", "Add cache alert", "ben", "2026-05-25"))

    def test_timeline_sorted(self):
        events = self.pm.timeline()
        self.assertEqual(events[0].event, "latency spike")
        self.assertEqual(events[1].event, "alert fired")

    def test_why_chain_and_root_cause(self):
        self.assertEqual(self.pm.depth(), 2)
        self.assertEqual(self.pm.root_cause(), "deploy flushed it")
        self.assertEqual(self.pm.why_chain()[0], ("did latency spike", "cache was cold"))

    def test_actions(self):
        self.assertEqual(len(self.pm.open_actions()), 2)
        self.pm.complete_action("A1")
        self.assertEqual([a.action_id for a in self.pm.open_actions()], ["A2"])
        self.assertEqual(self.pm.action_completion(), 0.5)

    def test_duplicate_action_raises(self):
        with self.assertRaises(ValueError):
            self.pm.add_action(ActionItem("A1", "dup", "x", "2026-06-01"))

    def test_unknown_action_raises(self):
        with self.assertRaises(KeyError):
            self.pm.complete_action("ZZ")

    def test_bad_timestamp_raises(self):
        with self.assertRaises(TypeError):
            self.pm.add_event("not-a-date", "x", "y")

    def test_markdown(self):
        md = self.pm.to_markdown()
        self.assertIn("# Postmortem: Model outage", md)
        self.assertIn("## Timeline", md)
        self.assertIn("## Five whys", md)
        self.assertIn("## Action items", md)
        self.assertIn("latency spike", md)
        # timeline order preserved in markdown
        self.assertLess(md.index("latency spike"), md.index("alert fired"))

    def test_empty_postmortem(self):
        pm = Postmortem("INC-1", "Empty")
        self.assertIsNone(pm.root_cause())
        self.assertEqual(pm.action_completion(), 1.0)
        self.assertIn("INC-1", pm.to_markdown())


if __name__ == "__main__":
    unittest.main()
