"""Heating Scheduler integration setup.

Early GitHub development skeleton. This does not control heating or schedules.
Do not point this development instance at your production heating switch.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .service_registration import async_register_schedule_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Expose schedule management services, disabled unless explicitly opted in."""
    async_register_schedule_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Store a config entry without starting heating or changing schedules."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "target_entity": entry.data["target_entity"],
    }
    _LOGGER.warning(
        "Heating Scheduler preview: hardware controls are inactive; schedule writes are disabled by default"
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Forget the config entry without affecting physical switches."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
