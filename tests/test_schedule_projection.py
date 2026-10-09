"""Display-only schedule projections, requiring no Home Assistant installation."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("schedule_projection_isolated")
pkg.__path__ = [str(base)]
sys.modules[pkg.__name__] = pkg


def load(name):
    spec = importlib.util.spec_from_file_location(f"{pkg.__name__}.{name}", base / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load("const")
bridge = load("scheduler_bridge")
projection = load("schedule_projection")


def schedule(name, owner, state="off", minutes=30, timeslots=None):
    return {
        "friendly_name": f"Scheduler {name}",
        "state": state,
        "actions": [bridge.schedule_action(owner, minutes)],
        "weekdays": ["mon", "wed"],
        "timeslots": ["06:30"] if timeslots is None else timeslots,
    }


class ScheduleProjectionTests(unittest.TestCase):
    def test_owned_rows_sorted_and_fields_recovered(self):
        schedules = {
            "switch.schedule_z": schedule("Z", "entry_a", "off", 60),
            "switch.schedule_a": schedule("A", "entry_a", "on", 15),
            "switch.schedule_foreign": schedule("Foreign", "entry_b"),
        }
        rows = projection.schedule_rows(schedules, "entry_a")
        self.assertEqual([r["name"] for r in rows], ["A", "Z"])
        self.assertEqual(rows[0]["start"], "06:30")
        self.assertEqual(rows[0]["minutes"], 15)
        self.assertEqual(rows[0]["weekdays"], ["mon", "wed"])
        self.assertTrue(rows[0]["enabled"])
        self.assertFalse(rows[0]["can_delete"])
        self.assertTrue(rows[1]["can_delete"])
        self.assertTrue(all(not r["editable"] for r in rows))

    def test_unknown_states_never_enable_deletion(self):
        for state in ("unknown", "unavailable", None):
            with self.subTest(state=state):
                row = projection.schedule_rows(
                    {"switch.schedule_test": schedule("Test", "entry_a", state)},
                    "entry_a",
                )[0]
                self.assertIsNone(row["enabled"])
                self.assertFalse(row["can_delete"])

    def test_ambiguous_or_unavailable_display_data_remains_unknown(self):
        attrs = schedule("Test", "entry_a", timeslots=["06:30 - 07:30"])
        attrs["weekdays"] = ["daily"]
        attrs["actions"] = [
            bridge.schedule_action("entry_a", 15),
            bridge.schedule_action("entry_a", 30),
        ]
        row = projection.schedule_rows({"switch.schedule_test": attrs}, "entry_a")[0]
        self.assertIsNone(row["start"])
        self.assertIsNone(row["minutes"])
        self.assertIsNone(row["weekdays"])

    def test_empty_and_foreign_only_are_safe(self):
        self.assertEqual(projection.schedule_rows({}, "entry_a"), [])
        self.assertEqual(projection.schedule_rows(
            {"switch.schedule_foreign": schedule("Other", "entry_b")}, "entry_a",
        ), [])
