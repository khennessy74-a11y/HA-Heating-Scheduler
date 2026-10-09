"""Disposable Home Assistant core test: no physical heating services."""
from types import SimpleNamespace

import pytest

from custom_components.heating_scheduler import (
    async_setup, async_setup_entry, async_unload_entry,
)
from custom_components.heating_scheduler.const import DOMAIN
from custom_components.heating_scheduler.service_registration import (
    schedule_writes_allowed,
)
from homeassistant.exceptions import HomeAssistantError


@pytest.mark.asyncio
async def test_real_hass_setup_unload_and_write_denial(hass, enable_custom_integrations):
    """Use the real HA service registry and actual integration coroutines."""
    entry = SimpleNamespace(
        entry_id="disposable_test_entry", domain=DOMAIN,
        data={"target_entity": "switch.disposable_test"},
        options={"enable_schedule_writes": True},
    )
    hass.states.async_set("switch.disposable_test", "off")
    assert await async_setup(hass, {})
    assert await async_setup_entry(hass, entry)
    assert hass.data[DOMAIN][entry.entry_id]["target_entity"] == "switch.disposable_test"
    for service in ("add_schedule", "edit_schedule", "remove_schedule"):
        assert hass.services.has_service(DOMAIN, service)
        payload = {"entry_id": entry.entry_id}
        if service in ("add_schedule", "edit_schedule"):
            payload.update({
                "name": "Test", "start": "06:30",
                "weekdays": ["mon"], "minutes": 15,
            })
        if service in ("edit_schedule", "remove_schedule"):
            payload["entity_id"] = "switch.schedule_test"
        with pytest.raises(HomeAssistantError):
            await hass.services.async_call(DOMAIN, service, payload, blocking=True)
    assert hass.states.get("switch.disposable_test").state == "off"
    assert not schedule_writes_allowed(hass, entry.entry_id)
    assert await async_unload_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]
    assert hass.states.get("switch.disposable_test").state == "off"
