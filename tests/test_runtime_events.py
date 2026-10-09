"""Offline event-routing and unload-policy checks, no Home Assistant runtime."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler" / "runtime_events.py"
spec = importlib.util.spec_from_file_location("runtime_events_isolated", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class FakeRuntime:
    def __init__(self):
        self.calls = []

    async def manual_off(self, entry_id):
        self.calls.append(entry_id)


class EventRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_off_routes_only_to_matching_entry(self):
        runtime = FakeRuntime()
        router = module.StateEventRouter(runtime, {
            "entry_a": "switch.test_a", "entry_b": "switch.test_b",
        })
        self.assertTrue(await router.handle_change("switch.test_b", "on", "off"))
        self.assertEqual(runtime.calls, ["entry_b"])

    async def test_ignore_unrelated_and_unavailable(self):
        runtime = FakeRuntime()
        router = module.StateEventRouter(runtime, {"a": "switch.test"})
        for entity, old, new in (
            ("switch.heating", "on", "off"),
            ("switch.test", "on", "unavailable"),
            ("switch.test", "unavailable", "off"),
            ("switch.test", "off", "off"),
            ("switch.test", "off", "on"),
        ):
            with self.subTest(entity=entity, old=old, new=new):
                self.assertFalse(await router.handle_change(entity, old, new))
        self.assertEqual(runtime.calls, [])

    async def test_duplicate_target_mapping_fails_closed(self):
        runtime = FakeRuntime()
        router = module.StateEventRouter(runtime, {
            "a": "switch.test", "b": "switch.test",
        })
        self.assertFalse(await router.handle_change("switch.test", "on", "off"))
        self.assertEqual(runtime.calls, [])

    async def test_active_entry_requires_explicit_shutdown_policy(self):
        with self.assertRaises(module.UnsafeUnload):
            module.assert_idle_before_unload(frozenset({"a"}), "a")
        module.assert_idle_before_unload(frozenset({"a"}), "b")
        module.assert_idle_before_unload(frozenset(), "a")


if __name__ == "__main__":
    unittest.main()
