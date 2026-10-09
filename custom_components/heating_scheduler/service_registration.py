"""Register fail-closed schedule-management services.

A service call requires an explicitly enabled config entry option.
No default config enables writes; heating start/stop remain unavailable.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .ha_scheduler_services import HomeAssistantSchedulerServices

OPT_ENABLE_SCHEDULE_WRITES = "enable_schedule_writes"
_REGISTERED_KEY = "_schedule_services_registered"

_COMMON = {
    vol.Required("entry_id"): str,
}
_SCHEDULE_FIELDS = {
    **_COMMON,
    vol.Required("name"): str,
    vol.Required("start"): str,
    vol.Required("weekdays"): [str],
    vol.Required("minutes"): int,
    vol.Optional("enabled", default=True): bool,
}
_SCHEMAS = {
    "add_schedule": vol.Schema(_SCHEDULE_FIELDS),
    "edit_schedule": vol.Schema({**_SCHEDULE_FIELDS, vol.Required("entity_id"): str}),
    "remove_schedule": vol.Schema({**_COMMON, vol.Required("entity_id"): str}),
}


def schedule_writes_allowed(hass: HomeAssistant, entry_id: str) -> bool:
    """Only a loaded, explicitly opted-in entry may mutate schedules."""
    entry = hass.config_entries.async_get_entry(entry_id)
    return bool(
        entry is not None
        and entry.domain == DOMAIN
        and entry_id in hass.data.get(DOMAIN, {})
        and entry.options.get(OPT_ENABLE_SCHEDULE_WRITES) is True
    )


def async_register_schedule_services(hass: HomeAssistant) -> None:
    """Register services once; all handlers are disabled by default."""
    storage = hass.data.setdefault(DOMAIN, {})
    if storage.get(_REGISTERED_KEY):
        return

    adapter = HomeAssistantSchedulerServices(hass)

    async def _dispatch(call: ServiceCall) -> None:
        entry_id = call.data["entry_id"]
        if not schedule_writes_allowed(hass, entry_id):
            raise HomeAssistantError(
                "Heating Scheduler write services are disabled for this entry"
            )
        entries = {
            entry_id: hass.data[DOMAIN][entry_id],
        }
        try:
            if call.service == "add_schedule":
                await adapter.add(entries=entries, **dict(call.data))
            elif call.service == "edit_schedule":
                await adapter.edit(entries=entries, **dict(call.data))
            elif call.service == "remove_schedule":
                await adapter.remove(entries=entries, **dict(call.data))
            else:
                raise HomeAssistantError("Unsupported Heating Scheduler service")
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err

    for name, schema in _SCHEMAS.items():
        hass.services.async_register(DOMAIN, name, _dispatch, schema=schema)
    storage[_REGISTERED_KEY] = True
