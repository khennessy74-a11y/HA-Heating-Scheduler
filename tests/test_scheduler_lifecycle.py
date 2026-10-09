"""End-to-end bridge lifecycle simulation with all hardware gates closed."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
package = types.ModuleType("scheduler_lifecycle_isolated")
package.__path__ = [str(base)]
sys.modules[package.__name__] = package

def load(name):
    spec = importlib.util.spec_from_file_location(
        f"{package.__name__}.{name}", base / (name + ".py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

load("const")
bridge_module = load("scheduler_bridge")
fake_module = load("scheduler_simulator")
Bridge = bridge_module.SchedulerBridge
Error = bridge_module.ScheduleError
Simulator = fake_module.SimulatedScheduler

class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fake = Simulator()
        self.bridge = Bridge(self.fake.call, self.fake.snapshot)

    async def add(self, **overrides):
        args = dict(entry_id="owner_a", name="Morning", start="06:30",
                    weekdays=["mon", "tue"], minutes=60, enabled=True)
        args.update(overrides)
        return await self.bridge.add(**args)

    async def test_full_create_edit_disable_delete_lifecycle(self):
        eid = await self.add()
        self.assertEqual(self.fake.entities[eid]["state"], "on")
        eid2 = await self.bridge.edit(
            entry_id="owner_a", entity_id=eid, name="Morning updated",
            start="07:15", weekdays=["fri"], minutes=90, enabled=False,
        )
        self.assertEqual(eid, eid2)
        self.assertEqual(self.fake.entities[eid]["state"], "off")
        self.assertEqual(self.fake.entities[eid]["timeslots"], ["07:15"])
        self.assertEqual(self.fake.entities[eid]["weekdays"], ["fri"])
        await self.bridge.remove(entry_id="owner_a", entity_id=eid)
        self.assertNotIn(eid, self.fake.entities)

    async def test_rename_to_new_entity_id(self):
        old = await self.add()
        self.fake.fail.add("rename_id")
        new = await self.bridge.edit(
            entry_id="owner_a", entity_id=old, name="Changed",
            start="07:15", weekdays=["fri"], minutes=30, enabled=False,
        )
        self.assertNotEqual(old, new)
        self.assertNotIn(old, self.fake.entities)
        self.assertEqual(self.fake.entities[new]["state"], "off")

    async def test_owner_isolation_and_duplicate_name(self):
        eid = await self.add()
        before = len(self.fake.calls)
        with self.assertRaisesRegex(Error, "Duplicate"):
            await self.add(name="morning")
        with self.assertRaisesRegex(Error, "unowned"):
            await self.bridge.remove(entry_id="owner_b", entity_id=eid)
        self.assertEqual(before, len(self.fake.calls))

    async def test_disabled_creation_denied_before_first_service(self):
        with self.assertRaisesRegex(Error, "Creating disabled"):
            await self.add(enabled=False)
        self.assertEqual(self.fake.calls, [])

    async def test_enabled_delete_denied_before_service(self):
        eid = await self.add()
        before = len(self.fake.calls)
        with self.assertRaisesRegex(Error, "Disable schedule"):
            await self.bridge.remove(entry_id="owner_a", entity_id=eid)
        self.assertEqual(before, len(self.fake.calls))

    async def test_switch_confirmation_failure_is_not_success(self):
        self.fake.skip_state.add("switch.turn_off")
        eid = await self.add()
        with self.assertRaisesRegex(Error, "did not confirm"):
            await self.bridge.edit(
                entry_id="owner_a", entity_id=eid, name="Morning",
                start="06:30", weekdays=["mon"], minutes=60, enabled=False,
            )

    async def test_remove_confirmation_failure_is_not_success(self):
        eid = await self.add()
        await self.bridge.edit(
            entry_id="owner_a", entity_id=eid, name="Morning",
            start="06:30", weekdays=["mon"], minutes=60, enabled=False,
        )
        self.fake.skip_state.add("scheduler.remove")
        with self.assertRaisesRegex(Error, "did not confirm removal"):
            await self.bridge.remove(entry_id="owner_a", entity_id=eid)

    async def test_service_error_propagates_without_false_success(self):
        self.fake.fail.add("scheduler.add")
        with self.assertRaisesRegex(RuntimeError, "Simulated service failure"):
            await self.add()
        self.assertFalse(self.fake.entities)

    async def test_parallel_creates_are_serialized(self):
        a, b = await asyncio.gather(
            self.add(name="Morning"),
            self.add(name="Evening", start="20:00")
        )
        self.assertNotEqual(a, b)
        self.assertEqual(len(self.fake.entities), 2)
