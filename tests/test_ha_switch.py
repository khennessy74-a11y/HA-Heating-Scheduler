"""Isolated adapter tests with fake Home Assistant modules (no live switch)."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock


def install_fake_homeassistant():
    ha = types.ModuleType("homeassistant")
    ha.__path__ = []
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    const = types.ModuleType("homeassistant.const")
    const.STATE_ON = "on"
    const.STATE_OFF = "off"
    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    events = types.ModuleType("homeassistant.helpers.event")

    def track(hass, entity_ids, callback):
        hass.callbacks.append(callback)
        def unsubscribe():
            hass.callbacks.remove(callback)
        return unsubscribe

    events.async_track_state_change_event = track
    sys.modules.update({
        "homeassistant": ha,
        "homeassistant.core": core,
        "homeassistant.const": const,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.event": events,
    })


install_fake_homeassistant()
path = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler" / "ha_switch.py"
spec = importlib.util.spec_from_file_location("heating_switch_adapter_test", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
Adapter = module.HomeAssistantHeatingSwitch


class FakeStates:
    def __init__(self, initial):
        self.value = initial

    def get(self, entity_id):
        return None if self.value is None else types.SimpleNamespace(state=self.value)


class FakeHass:
    def __init__(self, initial="off"):
        self.loop = asyncio.get_running_loop()
        self.states = FakeStates(initial)
        self.services = types.SimpleNamespace(async_call=AsyncMock())
        self.callbacks = []

    def emit(self, new_state):
        self.states.value = new_state
        event = types.SimpleNamespace(
            data={"new_state": types.SimpleNamespace(state=new_state)}
        )
        for callback in list(self.callbacks):
            callback(event)


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_entity_domain(self):
        with self.assertRaises(ValueError):
            Adapter(FakeHass(), "light.kitchen")

    async def test_off_state_and_unavailable(self):
        hass = FakeHass("off")
        adapter = Adapter(hass, "switch.test_outlet")
        self.assertTrue(await adapter.is_off())
        hass.states.value = "unavailable"
        self.assertFalse(await adapter.is_off())
        hass.states.value = None
        self.assertFalse(await adapter.is_off())

    async def test_immediate_on_confirmation(self):
        hass = FakeHass("on")
        adapter = Adapter(hass, "switch.test_outlet")
        self.assertTrue(await adapter.wait_until_on(0.1))
        self.assertFalse(hass.callbacks)

    async def test_delayed_on_confirmation_and_unsubscribe(self):
        hass = FakeHass()
        adapter = Adapter(hass, "switch.test_outlet")
        waiter = asyncio.create_task(adapter.wait_until_on(1.0))
        await asyncio.sleep(0)
        self.assertEqual(len(hass.callbacks), 1)
        hass.emit("on")
        self.assertTrue(await waiter)
        self.assertFalse(hass.callbacks)

    async def test_unavailable_then_timeout(self):
        hass = FakeHass("unavailable")
        adapter = Adapter(hass, "switch.test_outlet")
        self.assertFalse(await adapter.wait_until_on(0.01))
        self.assertFalse(hass.callbacks)

    async def test_service_calls_target_only_selected_switch(self):
        hass = FakeHass()
        adapter = Adapter(hass, "switch.test_outlet")
        await adapter.turn_on()
        await adapter.turn_off()
        self.assertEqual(
            hass.services.async_call.await_args_list[0].args,
            ("switch", "turn_on", {"entity_id": "switch.test_outlet"}),
        )
        self.assertEqual(
            hass.services.async_call.await_args_list[1].args,
            ("switch", "turn_off", {"entity_id": "switch.test_outlet"}),
        )
        self.assertTrue(all(
            item.kwargs["blocking"] for item in hass.services.async_call.await_args_list
        ))


if __name__ == "__main__":
    unittest.main()
