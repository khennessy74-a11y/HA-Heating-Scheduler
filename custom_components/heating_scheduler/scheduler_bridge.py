"""Scheduler Component bridge: validation and owned schedule operations.

NOT REGISTERED or CALLED by integration setup; safe for offline testing.
Activation requires HA runtime tests and explicit opt-in.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from .const import DURATIONS, WEEKDAYS

ActionCall = Callable[[str, str, dict[str, Any]], Awaitable[None]]
GetSchedules = Callable[[], Mapping[str, Mapping[str, Any]]]


class ScheduleError(ValueError):
    """Scheduling request was rejected before modifying anything."""


def validate_schedule(name: str, start: str, weekdays: list[str], minutes: int) -> None:
    """Validate incoming schedule fields."""
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
        raise ScheduleError("Enter a schedule name of up to 80 characters")
    import re
    if not isinstance(start, str) or re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", start) is None:
        raise ScheduleError("Start must be HH:MM")
    if not isinstance(weekdays, list) or not weekdays or len(set(weekdays)) != len(weekdays):
        raise ScheduleError("Choose unique weekdays")
    if not all(day in WEEKDAYS for day in weekdays):
        raise ScheduleError("Invalid weekday")
    if type(minutes) is not int or minutes not in DURATIONS:
        raise ScheduleError("Unsupported heating duration")


def schedule_name(attributes: Mapping[str, Any]) -> str:
    """Normalize the display name assigned by Scheduler Component."""
    name = str(attributes.get("friendly_name") or "").strip()
    return name[len("Scheduler "):] if name.casefold().startswith("scheduler ") else name


def owned_schedule(entity_id: str, attributes: Mapping[str, Any], entry_id: str) -> bool:
    """A schedule is owned only if its action targets this entry's service."""
    if not entity_id.startswith("switch.schedule_"):
        return False
    for action in attributes.get("actions") or []:
        if not isinstance(action, dict) or action.get("service") != "heating_scheduler.start":
            continue
        data = action.get("data") or action.get("service_data") or {}
        if isinstance(data, dict) and data.get("entry_id") == entry_id:
            return True
    return False


def schedule_action(entry_id: str, minutes: int) -> dict[str, Any]:
    """Scheduler action with explicit entry ownership."""
    return {
        "service": "heating_scheduler.start",
        "service_data": {"entry_id": entry_id, "minutes": minutes},
    }


class SchedulerBridge:
    """Dependency-injected Scheduler Component service bridge, currently inactive."""

    def __init__(self, call: ActionCall, get_schedules: GetSchedules) -> None:
        self._call = call
        self._get_schedules = get_schedules

    def _owned(self, entry_id: str) -> dict[str, Mapping[str, Any]]:
        return {
            entity_id: attrs
            for entity_id, attrs in self._get_schedules().items()
            if owned_schedule(entity_id, attrs, entry_id)
        }

    def _reject_duplicate(self, entry_id: str, name: str, ignore: str | None = None) -> None:
        wanted = name.strip().casefold()
        for entity_id, attrs in self._owned(entry_id).items():
            if entity_id != ignore and schedule_name(attrs).casefold() == wanted:
                raise ScheduleError("Duplicate heating schedule name")

    async def resolve_new(
        self, entry_id: str, name: str, before: set[str], *, retries: int = 20,
        delay: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> str:
        """Return exactly one new owned schedule; never guess generated entity IDs."""
        wanted = name.strip().casefold()
        for _ in range(retries):
            matches = [
                entity_id
                for entity_id, attrs in self._owned(entry_id).items()
                if entity_id not in before and schedule_name(attrs).casefold() == wanted
            ]
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise ScheduleError("Ambiguous newly created schedule")
            await delay(0.25)
        raise ScheduleError("Schedule may exist but cannot be identified. Check Scheduler before retrying.")

    async def set_enabled(self, entity_id: str, enabled: bool) -> None:
        """Only call with an entity ID separately validated as owned."""
        await self._call("switch", "turn_on" if enabled else "turn_off", {"entity_id": entity_id})

    async def add(
        self, *, entry_id: str, name: str, start: str, weekdays: list[str],
        minutes: int, enabled: bool = True,
    ) -> str:
        validate_schedule(name, start, weekdays, minutes)
        self._reject_duplicate(entry_id, name)
        before = set(self._owned(entry_id))
        await self._call("scheduler", "add", {
            "name": name.strip(), "weekdays": weekdays, "repeat_type": "repeat",
            "timeslots": [{"start": start, "actions": [schedule_action(entry_id, minutes)]}],
        })
        entity_id = await self.resolve_new(entry_id, name, before)
        await self.set_enabled(entity_id, enabled)
        return entity_id

    async def resolve_edited(
        self, entry_id: str, original_id: str, name: str, before: set[str],
        *, retries: int = 20,
        delay: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> str:
        """Resolve a renamed schedule without assuming the entity ID is stable.

        Accept only the original entity or a newly created owned entity.
        An ambiguous outcome is an error, never a guess.
        """
        wanted = name.strip().casefold()
        for _ in range(retries):
            candidates = [
                entity_id for entity_id, attrs in self._owned(entry_id).items()
                if (entity_id == original_id or entity_id not in before)
                and schedule_name(attrs).casefold() == wanted
            ]
            if len(candidates) == 1:
                return candidates[0]
            if len(candidates) > 1:
                raise ScheduleError("Ambiguous renamed schedule; state was not changed")
            await delay(0.25)
        raise ScheduleError(
            "Schedule edit may have succeeded, but its entity could not be "
            "identified safely. Check Scheduler before retrying."
        )

    async def edit(
        self, *, entry_id: str, entity_id: str, name: str, start: str,
        weekdays: list[str], minutes: int, enabled: bool,
    ) -> str:
        """Edit an owned schedule; apply state only to its verified identity."""
        validate_schedule(name, start, weekdays, minutes)
        owned = self._owned(entry_id)
        if entity_id not in owned:
            raise ScheduleError("Cannot edit an unowned schedule")
        self._reject_duplicate(entry_id, name, ignore=entity_id)
        before = set(owned)
        original_name = schedule_name(owned[entity_id])
        payload: dict[str, Any] = {
            "entity_id": entity_id,
            "weekdays": weekdays,
            "timeslots": [{
                "start": start,
                "actions": [schedule_action(entry_id, minutes)],
            }],
        }
        if name.strip() != original_name:
            payload["name"] = name.strip()
        await self._call("scheduler", "edit", payload)
        resolved = await self.resolve_edited(entry_id, entity_id, name, before)
        await self.set_enabled(resolved, enabled)
        return resolved

    async def remove(self, *, entry_id: str, entity_id: str) -> None:
        attrs = self._owned(entry_id).get(entity_id)
        if attrs is None:
            raise ScheduleError("Cannot delete an unowned schedule")
        if attrs.get("state") != "off":
            raise ScheduleError("Disable schedule before deletion")
        await self._call("scheduler", "remove", {"entity_id": entity_id})
