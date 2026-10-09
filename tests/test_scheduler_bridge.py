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


    async def test_edit_rename_and_disable_new_entity(self):
        schedules = {
            "switch.schedule_old": {
                "friendly_name": "Scheduler Old", "state": "on",
                "actions": [bridge.schedule_action("a", 15)],
            },
            "switch.schedule_other": {
                "friendly_name": "Scheduler Other", "state": "on",
                "actions": [bridge.schedule_action("b", 15)],
            },
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))
            if (domain, service) == ("scheduler", "edit"):
                schedules.pop("switch.schedule_old")
                schedules["switch.schedule_renamed"] = {
                    "friendly_name": "Scheduler Renamed", "state": "on",
                    "actions": [bridge.schedule_action("a", 30)],
                }

        b = bridge.SchedulerBridge(call, lambda: schedules)
        result = await b.edit(
            entry_id="a", entity_id="switch.schedule_old", name="Renamed",
            start="05:45", weekdays=["tue"], minutes=30, enabled=False,
        )
        self.assertEqual(result, "switch.schedule_renamed")
        self.assertEqual(calls[0][2]["name"], "Renamed")
        self.assertEqual(
            calls[-1],
            ("switch", "turn_off", {"entity_id": "switch.schedule_renamed"}),
        )

    async def test_edit_without_rename_preserves_name(self):
        schedules = {
            "switch.schedule_existing": {
                "friendly_name": "Scheduler Existing", "state": "off",
                "actions": [bridge.schedule_action("a", 15)],
            },
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))

        b = bridge.SchedulerBridge(call, lambda: schedules)
        result = await b.edit(
            entry_id="a", entity_id="switch.schedule_existing", name="Existing",
            start="08:30", weekdays=["wed"], minutes=60, enabled=True,
        )
        self.assertEqual(result, "switch.schedule_existing")
        self.assertNotIn("name", calls[0][2])
        self.assertEqual(calls[-1][1], "turn_on")

    async def test_edit_rejects_duplicate_before_any_write(self):
        schedules = {
            "switch.schedule_first": {
                "friendly_name": "Scheduler First",
                "actions": [bridge.schedule_action("a", 15)],
            },
            "switch.schedule_second": {
                "friendly_name": "Scheduler Second",
                "actions": [bridge.schedule_action("a", 15)],
            },
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "Duplicate"):
            await b.edit(
                entry_id="a", entity_id="switch.schedule_first", name="second",
                start="09:00", weekdays=["mon"], minutes=15, enabled=False,
            )
        self.assertEqual(calls, [])

    async def test_edit_rejects_foreign_schedule_before_any_write(self):
        schedules = {
            "switch.schedule_foreign": {
                "friendly_name": "Scheduler Foreign",
                "actions": [bridge.schedule_action("other", 15)],
            },
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaises(bridge.ScheduleError):
            await b.edit(
                entry_id="a", entity_id="switch.schedule_foreign", name="Foreign",
                start="09:00", weekdays=["mon"], minutes=15, enabled=True,
            )
        self.assertEqual(calls, [])

    async def test_unresolved_rename_does_not_toggle_other_schedule(self):
        schedules = {
            "switch.schedule_old": {
                "friendly_name": "Scheduler Old",
                "actions": [bridge.schedule_action("a", 15)],
            },
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))
            # Simulate a rename that never becomes visible.

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "identified safely"):
            await b.edit(
                entry_id="a", entity_id="switch.schedule_old", name="New",
                start="09:00", weekdays=["mon"], minutes=15, enabled=False,
            )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "edit")



    async def test_duplicate_add_does_not_call_scheduler(self):
        schedules = {
            "switch.schedule_morning": {
                "friendly_name": "Scheduler Morning",
                "actions": [bridge.schedule_action("a", 15)],
            }
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "Duplicate"):
            await b.add(
                entry_id="a", name="morning", start="06:30",
                weekdays=["mon"], minutes=15,
            )
        self.assertEqual(calls, [])

    async def test_ambiguous_new_schedule_does_not_toggle_either(self):
        schedules = {}
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))
            if (domain, service) == ("scheduler", "add"):
                for suffix in ("one", "two"):
                    schedules[f"switch.schedule_{suffix}"] = {
                        "friendly_name": "Scheduler Morning",
                        "actions": [bridge.schedule_action("a", 15)],
                    }

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "Ambiguous"):
            await b.add(
                entry_id="a", name="Morning", start="06:30",
                weekdays=["mon"], minutes=15, enabled=False,
            )
        self.assertEqual([(d, s) for d, s, _ in calls], [("scheduler", "add")])

    async def test_unresolved_add_does_not_change_existing_schedule(self):
        schedules = {
            "switch.schedule_existing": {
                "friendly_name": "Scheduler Existing",
                "actions": [bridge.schedule_action("a", 15)],
            }
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "cannot be identified"):
            await b.add(
                entry_id="a", name="Morning", start="06:30",
                weekdays=["mon"], minutes=15, enabled=False,
            )
        self.assertEqual([(d, s) for d, s, _ in calls], [("scheduler", "add")])

    async def test_rename_ambiguous_never_toggles_another_schedule(self):
        schedules = {
            "switch.schedule_original": {
                "friendly_name": "Scheduler Original",
                "actions": [bridge.schedule_action("a", 15)],
            }
        }
        calls = []

        async def call(domain, service, data):
            calls.append((domain, service, data))
            if (domain, service) == ("scheduler", "edit"):
                schedules["switch.schedule_first"] = {
                    "friendly_name": "Scheduler Renamed",
                    "actions": [bridge.schedule_action("a", 15)],
                }
                schedules["switch.schedule_second"] = {
                    "friendly_name": "Scheduler Renamed",
                    "actions": [bridge.schedule_action("a", 15)],
                }

        b = bridge.SchedulerBridge(call, lambda: schedules)
        with self.assertRaisesRegex(bridge.ScheduleError, "Ambiguous"):
            await b.edit(
                entry_id="a", entity_id="switch.schedule_original",
                name="Renamed", start="06:30", weekdays=["mon"],
                minutes=15, enabled=False,
            )
        self.assertEqual([(d, s) for d, s, _ in calls], [("scheduler", "edit")])


    async def test_simultaneous_add_same_name_only_creates_one(self):
        schedules = {}
        calls = []
        entered = asyncio.Event()
        release = asyncio.Event()

        async def call(domain, service, data):
            calls.append((domain, service, data))
            if (domain, service) == ("scheduler", "add"):
                entered.set()
                await release.wait()
                schedules["switch.schedule_morning"] = {
                    "friendly_name": "Scheduler Morning", "state": "on",
                    "actions": [bridge.schedule_action("a", 15)],
                }

        b = bridge.SchedulerBridge(call, lambda: schedules)
        kwargs = dict(
            entry_id="a", name="Morning", start="06:30",
            weekdays=["mon"], minutes=15, enabled=True,
        )
        first = asyncio.create_task(b.add(**kwargs))
        await asyncio.wait_for(entered.wait(), timeout=1)
        second = asyncio.create_task(b.add(**kwargs))
        await asyncio.sleep(0)
        release.set()
        created = await first
        self.assertEqual(created, "switch.schedule_morning")
        with self.assertRaisesRegex(bridge.ScheduleError, "Duplicate"):
            await second
        self.assertEqual(sum((d, s) == ("scheduler", "add") for d, s, _ in calls), 1)


if __name__ == "__main__":
    unittest.main()
