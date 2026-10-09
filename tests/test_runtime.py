"""Fail-closed timed-heating coordinator tests."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("runtime_test_isolated")
pkg.__path__ = [str(base)]
sys.modules[pkg.__name__] = pkg


def load(name):
    spec = importlib.util.spec_from_file_location(
        f"{pkg.__name__}.{name}", base / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load("const")
load("session")
load("controller")
runtime = load("runtime")


class CoordinatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_start_rejected_without_constructing_switch(self):
        attempts = []

        def make_switch(entry_id):
            attempts.append(entry_id)
            raise AssertionError("No switch should be constructed")

        coordinator = runtime.HeatingRuntimeCoordinator(make_switch)
        with self.assertRaises(runtime.HeatingRuntimeUnavailable):
            await coordinator.start("test_entry", 15)
        self.assertEqual(attempts, [])
        self.assertFalse(coordinator.active_entries)

    async def test_stop_rejected_without_hardware_action(self):
        coordinator = runtime.HeatingRuntimeCoordinator(
            lambda _: self.fail("Must not create a switch")
        )
        with self.assertRaises(runtime.HeatingRuntimeUnavailable):
            await coordinator.stop("test_entry")
        self.assertFalse(coordinator.active_entries)

    async def test_runtime_disabled_by_default(self):
        self.assertIs(runtime.HEATING_RUNTIME_RELEASED, False)

    async def test_manual_off_when_idle_does_not_construct_switch(self):
        coordinator = runtime.HeatingRuntimeCoordinator(
            lambda _: self.fail("Must not create a switch")
        )
        await coordinator.manual_off("test_entry")
        self.assertFalse(coordinator.active_entries)


if __name__ == "__main__":
    unittest.main()
