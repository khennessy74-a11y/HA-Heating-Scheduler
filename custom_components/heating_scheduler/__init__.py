"""Heating Scheduler integration setup.

Early GitHub development skeleton. This does not control heating or schedules.
Do not point this development instance at your production heating switch.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Allow configuration via the Home Assistant UI."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Store a config entry without starting heating or changing schedules."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "target_entity": entry.data["target_entity"],
    }
    _LOGGER.warning(
        "Heating Scheduler is a development preview: no heating actions are active"
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Forget the config entry without affecting physical switches."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
