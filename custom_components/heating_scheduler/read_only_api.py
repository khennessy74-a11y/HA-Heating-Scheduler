"""Read-only Home Assistant schedule-list service.

Only serializes owned Scheduler Component switch attributes. No switch control,
schedule mutation, network request or timer is triggered.
"""
from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from .const import DOMAIN
from .ha_scheduler_services import scheduler_snapshot
from .mobile_list import mobile_schedule_list

SERVICE_LIST = "list_schedules"
_SERVICE_FLAG = "_read_only_list_registered"
_SCHEMA = vol.Schema({vol.Required("entry_id"): str})


def async_register_read_only_service(hass: HomeAssistant) -> None:
    """Register read-only response-returning service exactly once."""
    data = hass.data.setdefault(DOMAIN, {})
    if data.get(_SERVICE_FLAG):
        return

    async def handle(call: ServiceCall) -> dict:
        entry_id = call.data["entry_id"]
        entry = hass.config_entries.async_get_entry(entry_id)
        if (
            not entry
            or entry.domain != DOMAIN
            or entry_id not in hass.data.get(DOMAIN, {})
        ):
            raise ServiceValidationError("Unknown or unloaded Heating Scheduler entry")
        return mobile_schedule_list(scheduler_snapshot(hass), entry_id)

    hass.services.async_register(
        DOMAIN, SERVICE_LIST, handle,
        schema=_SCHEMA, supports_response=SupportsResponse.ONLY,
    )
    data[_SERVICE_FLAG] = True
