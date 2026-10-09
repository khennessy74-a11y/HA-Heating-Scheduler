"""Offline tests for Scheduler Component bridge; no Home Assistant dependency."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("scheduler_bridge_isolated")
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


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def test_validation(self):
        bridge.validate_schedule("Morning", "05:30", ["mon"], 15)
        for kwargs in (
            {"name": "", "start": "05:30", "weekdays": ["mon"], "minutes": 15},
            {"name": "A", "start": "25:30", "weekdays": ["mon"], "minutes": 15},
            {"name": "A", "start": "05:30", "weekdays": ["mon", "mon"], "minutes": 15},
            {"name": "A", "start": "05:30", "weekdays": ["mon"], "minutes": True},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(bridge.ScheduleError):
                bridge.validate_schedule(**kwargs)

    async def test_owned_schedule_restriction(self):
        attrs = {"actions": [{"service": "heating_scheduler.start",
                             "service_data": {"entry_id": "a", "minutes": 60}}]}
        self.assertTrue(bridge.owned_schedule("switch.schedule_a", attrs, "a"))
        self.assertFalse(bridge.owned_schedule("switch.schedule_a", attrs, "b"))
        self.assertFalse(bridge.owned_schedule("switch.heating", attrs, "a"))

    async def test_add_disabled_targets_only_created_schedule(self):
        schedules = {}
        calls = []
        async def call(domain, service, data):
            calls.append((domain, service, data))
            if (domain, service) == ("scheduler", "add"):
                schedules["switch.schedule_new"] = {
                    "friendly_name": "Scheduler New", "state": "on",
                    "actions": [bridge.schedule_action("a", 15)],
                }
        b = bridge.SchedulerBridge(call, lambda: schedules)
        created = await b.add(entry_id="a", name="New", start="05:30",
                              weekdays=["mon"], minutes=15, enabled=False)
        self.assertEqual(created, "switch.schedule_new")
        self.assertEqual(calls[-1], ("switch", "turn_off", {"entity_id": created}))

    async def test_cannot_delete_foreign_or_enabled(self):
        schedules = {
            "switch.schedule_mine": {
                "friendly_name": "Scheduler Mine", "state": "on",
                "actions": [bridge.schedule_action("a", 15)]
            }
        }
        async def call(*args):
            raise AssertionError("Should not be called")
        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaises(bridge.ScheduleError):
            await b.remove(entry_id="b", entity_id="switch.schedule_mine")
        with self.assertRaises(bridge.ScheduleError):
            await b.remove(entry_id="a", entity_id="switch.schedule_mine")


if __name__ == "__main__":
    unittest.main()
