"""Offline tests for the inactive Home Assistant Scheduler adapter."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("scheduler_adapter_isolated")
pkg.__path__ = [str(base)]
sys.modules[pkg.__name__] = pkg

ha = types.ModuleType("homeassistant")
ha.__path__ = []
core = types.ModuleType("homeassistant.core")
core.HomeAssistant = type("HomeAssistant", (), {})
sys.modules.update({"homeassistant": ha, "homeassistant.core": core})


def load(name):
    spec = importlib.util.spec_from_file_location(f"{pkg.__name__}.{name}", base / f"{name}.py")
    obj = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = obj
    spec.loader.exec_module(obj)
    return obj


load("const")
bridge = load("scheduler_bridge")
adapter = load("ha_scheduler_services")


class FakeHass:
    def __init__(self):
        self.current = []
        self.states = types.SimpleNamespace(async_all=lambda domain: self.current)
        self.services = types.SimpleNamespace(async_call=AsyncMock())


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_snapshot_contains_state_and_attributes(self):
        hass = FakeHass()
        hass.current = [
            types.SimpleNamespace(
                entity_id="switch.schedule_morning", state="off",
                attributes={"friendly_name": "Scheduler Morning"}
            ),
            types.SimpleNamespace(
                entity_id="switch.other", state="on", attributes={}
            ),
        ]
        snapshot = adapter.scheduler_snapshot(hass)
        self.assertEqual(snapshot["switch.schedule_morning"]["state"], "off")
        self.assertNotIn("switch.other", snapshot)

    async def test_rejects_missing_entry_without_service_calls(self):
        hass = FakeHass()
        services = adapter.HomeAssistantSchedulerServices(hass)
        with self.assertRaises(bridge.ScheduleError):
            await services.add(
                entry_id="missing", entries={}, name="Morning", start="05:30",
                weekdays=["mon"], minutes=15, enabled=True,
            )
        hass.services.async_call.assert_not_awaited()

    async def test_restricts_service_domains(self):
        hass = FakeHass()
        services = adapter.HomeAssistantSchedulerServices(hass)
        with self.assertRaises(bridge.ScheduleError):
            await services._call("climate", "set_temperature", {})
        hass.services.async_call.assert_not_awaited()

    async def test_delete_rejects_enabled_schedule(self):
        hass = FakeHass()
        hass.current = [types.SimpleNamespace(
            entity_id="switch.schedule_morning", state="on",
            attributes={
                "friendly_name": "Scheduler Morning",
                "actions": [bridge.schedule_action("entry1", 15)],
            }
        )]
        services = adapter.HomeAssistantSchedulerServices(hass)
        with self.assertRaises(bridge.ScheduleError):
            await services.remove(
                entry_id="entry1", entries={"entry1": {}},
                entity_id="switch.schedule_morning",
            )
        hass.services.async_call.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
