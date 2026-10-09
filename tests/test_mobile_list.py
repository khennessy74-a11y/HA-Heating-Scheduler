"""Mobile list contract tests without heating controls or Home Assistant."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

root = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("mobile_list_isolated")
pkg.__path__ = [str(root)]
sys.modules[pkg.__name__] = pkg


def load(name):
    spec = importlib.util.spec_from_file_location(f"{pkg.__name__}.{name}", root / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load("const")
bridge = load("scheduler_bridge")
load("schedule_projection")
mobile = load("mobile_list")


class MobileListTests(unittest.TestCase):
    def test_owned_rows_have_display_labels_but_no_actions(self):
        attrs = {
            "state": "on",
            "friendly_name": "Scheduler Morning",
            "actions": [bridge.schedule_action("mine", 60)],
            "weekdays": ["mon", "tue"],
            "timeslots": ["06:30"],
        }
        result = mobile.mobile_schedule_list(
            {"switch.schedule_morning": attrs}, "mine",
        )
        self.assertTrue(result["read_only"])
        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["title"], "Morning")
        self.assertEqual(item["status"], "Enabled")
        self.assertEqual(item["status_color"], "green")
        self.assertIn("60 min", item["subtitle"])
        self.assertIsNone(item["edit_action"])
        self.assertIsNone(item["delete_action"])
        self.assertFalse(item["can_delete_after_confirmation"])

    def test_foreign_schedule_not_displayed(self):
        attrs = {
            "state": "off", "friendly_name": "Scheduler Foreign",
            "actions": [bridge.schedule_action("other", 30)],
        }
        result = mobile.mobile_schedule_list(
            {"switch.schedule_foreign": attrs}, "mine",
        )
        self.assertEqual(result["items"], [])
        self.assertIsNotNone(result["empty_message"])

    def test_disabled_schedule_still_has_no_active_delete(self):
        attrs = {
            "state": "off", "friendly_name": "Scheduler Evening",
            "actions": [bridge.schedule_action("mine", 45)],
        }
        item = mobile.mobile_schedule_list(
            {"switch.schedule_evening": attrs}, "mine",
        )["items"][0]
        self.assertEqual(item["status"], "Disabled")
        self.assertTrue(item["can_delete_after_confirmation"])
        self.assertIsNone(item["delete_action"])

    def test_unknown_status_is_not_enabled_or_deletable(self):
        attrs = {
            "state": "unavailable", "friendly_name": "Scheduler Unknown",
            "actions": [bridge.schedule_action("mine", 30)],
        }
        item = mobile.mobile_schedule_list(
            {"switch.schedule_unknown": attrs}, "mine",
        )["items"][0]
        self.assertEqual(item["status"], "Unknown")
        self.assertFalse(item["can_delete_after_confirmation"])
