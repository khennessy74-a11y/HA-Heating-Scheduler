"""Async controller tests; no HA runtime or live device required."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("heating_scheduler_isolated")
pkg.__path__ = [str(base)]
sys.modules[pkg.__name__] = pkg

def load(name):
    spec = importlib.util.spec_from_file_location(f"{pkg.__name__}.{name}", base / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

load("session")
Controller = load("controller").TimedHeatingController


class FakeSwitch:
    def __init__(self, confirm=True):
        self.state = "off"
        self.confirm = confirm
        self.on_calls = 0
        self.off_calls = 0

    async def is_off(self):
        return self.state == "off"

    async def turn_on(self):
        self.state = "on"
        self.on_calls += 1

    async def wait_until_on(self, timeout):
        return self.confirm

    async def turn_off(self):
        self.state = "off"
        self.off_calls += 1


class ControllerTests(unittest.IsolatedAsyncioTestCase):
    async def test_session_finishes_and_turns_off(self):
        switch = FakeSwitch()
        delays = []
        async def fake_sleep(seconds):
            delays.append(seconds)
        ctl = Controller(switch, sleep=fake_sleep)
        await ctl.start(15)
        await ctl.wait_finished()
        self.assertEqual(delays, [900])
        self.assertEqual((switch.on_calls, switch.off_calls), (1, 1))

    async def test_confirmation_failure_turns_off(self):
        switch = FakeSwitch(confirm=False)
        ctl = Controller(switch)
        await ctl.start(15)
        with self.assertRaises(RuntimeError):
            await ctl.wait_finished()
        self.assertEqual(switch.off_calls, 1)

    async def test_busy_session_is_rejected(self):
        switch = FakeSwitch()
        gate = asyncio.Event()
        async def hold_sleep(seconds):
            await gate.wait()
        ctl = Controller(switch, sleep=hold_sleep)
        await ctl.start(15)
        with self.assertRaises(ValueError):
            await ctl.start(30)
        await ctl.stop()
        self.assertEqual(switch.off_calls, 1)

    async def test_manual_off_does_not_re_toggle(self):
        switch = FakeSwitch()
        async def wait_forever(seconds):
            await asyncio.Event().wait()
        ctl = Controller(switch, sleep=wait_forever)
        await ctl.start(15)
        switch.state = "off"
        await ctl.notify_manual_off()
        self.assertEqual(switch.off_calls, 0)
        self.assertFalse(ctl.running)

    async def test_stop_requests_off(self):
        switch = FakeSwitch()
        async def wait_forever(seconds):
            await asyncio.Event().wait()
        ctl = Controller(switch, sleep=wait_forever)
        await ctl.start(15)
        await ctl.stop()
        self.assertEqual(switch.off_calls, 1)


if __name__ == "__main__":
    unittest.main()
