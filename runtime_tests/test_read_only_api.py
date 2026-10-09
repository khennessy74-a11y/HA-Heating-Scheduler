"""Read-only schedule-list service exercised against disposable HA fixture."""
import pytest

from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from custom_components.heating_scheduler import async_setup, async_setup_entry, async_unload_entry
from custom_components.heating_scheduler.const import DOMAIN
from types import SimpleNamespace
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.mark.asyncio
async def test_read_only_schedule_list_uses_entry_ownership(hass, enable_custom_integrations):
    entry = MockConfigEntry(
        entry_id="read_only_owner", domain=DOMAIN,
        data={"target_entity": "switch.disposable_heater"}, options={},
    )
    entry.add_to_hass(hass)
    hass.states.async_set("switch.disposable_heater", "off")
    hass.states.async_set("switch.schedule_owned", "on", {
        "friendly_name": "Scheduler Morning",
        "actions": [{"service": "heating_scheduler.start",
                     "service_data": {"entry_id": entry.entry_id, "minutes": 30}}],
        "weekdays": ["mon"], "timeslots": ["07:00"],
    })
    hass.states.async_set("switch.schedule_foreign", "off", {
        "friendly_name": "Scheduler Foreign",
        "actions": [{"service": "heating_scheduler.start",
                     "service_data": {"entry_id": "another_entry", "minutes": 15}}],
    })
    assert await async_setup(hass, {})
    assert await async_setup_entry(hass, entry)
    assert hass.services.has_service(DOMAIN, "list_schedules")
    result = await hass.services.async_call(
        DOMAIN, "list_schedules", {"entry_id": entry.entry_id},
        blocking=True, return_response=True,
    )
    assert result["read_only"] is True
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == "Morning"
    assert result["items"][0]["status"] == "Enabled"
    assert result["items"][0]["edit_action"] is None
    assert result["items"][0]["delete_action"] is None
    assert hass.states.get("switch.disposable_heater").state == "off"
    assert await async_unload_entry(hass, entry)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN, "list_schedules", {"entry_id": entry.entry_id},
            blocking=True, return_response=True,
        )


@pytest.mark.asyncio
async def test_read_only_service_idempotent(hass, enable_custom_integrations):
    assert await async_setup(hass, {})
    assert await async_setup(hass, {})
    assert hass.services.has_service(DOMAIN, "list_schedules")
    assert hass.services.supports_response(DOMAIN, "list_schedules") == SupportsResponse.ONLY
