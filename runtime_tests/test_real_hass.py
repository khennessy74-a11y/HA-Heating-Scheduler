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


@pytest.mark.asyncio
async def test_repeated_entry_cycles_preserve_switch_and_denial(hass, enable_custom_integrations):
    """Repeated setup and unload must not activate hardware or write paths."""
    entry = SimpleNamespace(
        entry_id="cycle_entry", domain=DOMAIN,
        data={"target_entity": "switch.cycle_dummy"},
        options={"enable_schedule_writes": True},
    )
    hass.states.async_set("switch.cycle_dummy", "off")
    for cycle in range(3):
        assert await async_setup(hass, {})
        assert await async_setup_entry(hass, entry)
        assert not schedule_writes_allowed(hass, entry.entry_id)
        assert hass.states.get("switch.cycle_dummy").state == "off"
        assert hass.services.has_service(DOMAIN, "add_schedule")
        with pytest.raises(HomeAssistantError):
            await hass.services.async_call(
                DOMAIN, "add_schedule",
                {"entry_id": entry.entry_id, "name": "Blocked",
                 "start": "06:15", "weekdays": ["mon"], "minutes": 15},
                blocking=True,
            )
        assert await async_unload_entry(hass, entry)
        assert entry.entry_id not in hass.data[DOMAIN]
        assert hass.states.get("switch.cycle_dummy").state == "off"


@pytest.mark.asyncio
async def test_multiple_entries_remain_isolated(hass, enable_custom_integrations):
    """Unloading one entry must leave another entry and its dummy switch alone."""
    entries = [
        SimpleNamespace(
            entry_id=f"isolated_{i}", domain=DOMAIN,
            data={"target_entity": f"switch.isolated_{i}"},
            options={},
        )
        for i in range(2)
    ]
    for entry in entries:
        hass.states.async_set(entry.data["target_entity"], "off")
    assert await async_setup(hass, {})
    for entry in entries:
        assert await async_setup_entry(hass, entry)
    assert await async_unload_entry(hass, entries[0])
    assert entries[0].entry_id not in hass.data[DOMAIN]
    assert entries[1].entry_id in hass.data[DOMAIN]
    assert hass.states.get("switch.isolated_0").state == "off"
    assert hass.states.get("switch.isolated_1").state == "off"
    assert await async_unload_entry(hass, entries[1])
