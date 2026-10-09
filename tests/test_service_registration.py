"""Fail-closed registration tests with a simulated Home Assistant instance."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

import voluptuous as vol

base = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"
pkg = types.ModuleType("registration_test_pkg")
pkg.__path__ = [str(base)]
sys.modules[pkg.__name__] = pkg

ha = types.ModuleType("homeassistant")
ha.__path__ = []
core = types.ModuleType("homeassistant.core")
core.HomeAssistant = type("HomeAssistant", (), {})
core.ServiceCall = type("ServiceCall", (), {})
exceptions = types.ModuleType("homeassistant.exceptions")
exceptions.ServiceValidationError = type("ServiceValidationError", (Exception,), {})
sys.modules.update({
    "homeassistant": ha,
    "homeassistant.core": core,
    "homeassistant.exceptions": exceptions,
})


def load(name):
    spec = importlib.util.spec_from_file_location(f"{pkg.__name__}.{name}", base / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


load("const")
load("scheduler_bridge")
load("ha_scheduler_services")
registration = load("service_registration")


class FakeServices:
    def __init__(self):
        self.handlers = {}

    def async_register(self, domain, name, handler, schema):
        self.handlers[name] = (handler, schema)


class FakeHass:
    def __init__(self, options=None):
        self.data = {"heating_scheduler": {"entry_a": {"target_entity": "switch.test"}}}
        self.services = FakeServices()
        self.entry = types.SimpleNamespace(
            domain="heating_scheduler", options=options or {},
        )
        self.config_entries = types.SimpleNamespace(
            async_get_entry=lambda entry_id: self.entry if entry_id == "entry_a" else None,
        )


class RegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_default_registration_does_not_write(self):
        hass = FakeHass()
        registration.async_register_schedule_services(hass)
        self.assertEqual(set(hass.services.handlers), {
            "add_schedule", "edit_schedule", "remove_schedule",
        })
        self.assertFalse(registration.schedule_writes_allowed(hass, "entry_a"))
        for name, (handler, _) in hass.services.handlers.items():
            with self.subTest(name=name), self.assertRaises(exceptions.ServiceValidationError):
                await handler(types.SimpleNamespace(
                    service=name, data={"entry_id": "entry_a"},
                ))

    async def test_registration_idempotent(self):
        hass = FakeHass()
        registration.async_register_schedule_services(hass)
        registration.async_register_schedule_services(hass)
        self.assertEqual(len(hass.services.handlers), 3)

    async def test_write_gate_requires_exact_bool_true(self):
        hass = FakeHass({"enable_schedule_writes": "true"})
        self.assertFalse(registration.schedule_writes_allowed(hass, "entry_a"))
        hass.entry.options["enable_schedule_writes"] = True
        self.assertTrue(registration.schedule_writes_allowed(hass, "entry_a"))
        hass.data["heating_scheduler"].pop("entry_a")
        self.assertFalse(registration.schedule_writes_allowed(hass, "entry_a"))

    async def test_unknown_entry_rejected(self):
        hass = FakeHass({"enable_schedule_writes": True})
        self.assertFalse(registration.schedule_writes_allowed(hass, "missing"))


if __name__ == "__main__":
    unittest.main()
