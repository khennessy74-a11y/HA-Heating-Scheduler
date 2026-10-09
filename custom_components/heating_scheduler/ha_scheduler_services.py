"""Inactive Home Assistant adapter for Scheduler Component operations.

The adapter is NOT instantiated or registered by integration setup.
The selected configuration entry must be explicitly verified by the caller.
"""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .scheduler_bridge import ScheduleError, SchedulerBridge


def scheduler_snapshot(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Read schedule switches, retaining state and attributes for safety checks."""
    return {
        state.entity_id: {"state": state.state, **dict(state.attributes)}
        for state in hass.states.async_all("switch")
        if state.entity_id.startswith("switch.schedule_")
    }


class HomeAssistantSchedulerServices:
    """Connect the pure scheduling bridge to Home Assistant service calls.

    No Home Assistant service is registered merely by importing this class.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.bridge = SchedulerBridge(self._call, lambda: scheduler_snapshot(hass))

    async def _call(self, domain: str, service: str, data: dict[str, Any]) -> None:
        """Restrict outgoing actions to reviewed domains and service names."""
        allowed = {
            "scheduler": {"add", "edit", "remove"},
            "switch": {"turn_on", "turn_off"},
        }
        if service not in allowed.get(domain, set()):
            raise ScheduleError("Unsupported Scheduler service request")
        await self.hass.services.async_call(domain, service, data, blocking=True)

    @staticmethod
    def require_entry(entry_id: str, entries: dict[str, Any]) -> None:
        """Fail closed if the requested integration entry is absent."""
        if not entry_id or entry_id not in entries:
            raise ScheduleError("Unknown Heating Scheduler configuration entry")

    async def add(
        self, *, entry_id: str, entries: dict[str, Any], name: str,
        start: str, weekdays: list[str], minutes: int, enabled: bool,
    ) -> str:
        self.require_entry(entry_id, entries)
        return await self.bridge.add(
            entry_id=entry_id, name=name, start=start,
            weekdays=weekdays, minutes=minutes, enabled=enabled,
        )

    async def edit(
        self, *, entry_id: str, entries: dict[str, Any], entity_id: str,
        name: str, start: str, weekdays: list[str], minutes: int,
        enabled: bool,
    ) -> str:
        self.require_entry(entry_id, entries)
        return await self.bridge.edit(
            entry_id=entry_id, entity_id=entity_id, name=name,
            start=start, weekdays=weekdays, minutes=minutes, enabled=enabled,
        )

    async def remove(
        self, *, entry_id: str, entries: dict[str, Any], entity_id: str,
    ) -> None:
        self.require_entry(entry_id, entries)
        await self.bridge.remove(entry_id=entry_id, entity_id=entity_id)
