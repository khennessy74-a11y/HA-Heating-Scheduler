"""Pure read-only projection of owned Scheduler Component switch attributes.

No HA services, subscriptions or schedule mutations are performed here.
Incomplete schedule data is displayed as unknown, never guessed.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .const import WEEKDAYS
from .scheduler_bridge import owned_schedule, schedule_name


def _minutes(attributes: Mapping[str, Any], entry_id: str) -> int | None:
    durations = set()
    for action in attributes.get("actions") or []:
        if not isinstance(action, dict) or action.get("service") != "heating_scheduler.start":
            continue
        data = action.get("service_data") or action.get("data") or {}
        if not isinstance(data, dict) or data.get("entry_id") != entry_id:
            continue
        minutes = data.get("minutes")
        if type(minutes) is int and minutes > 0:
            durations.add(minutes)
    return next(iter(durations)) if len(durations) == 1 else None


def _weekdays(attributes: Mapping[str, Any]) -> list[str] | None:
    value = attributes.get("weekdays")
    if not isinstance(value, list) or not value:
        return None
    if all(day in WEEKDAYS for day in value) and len(value) == len(set(value)):
        return list(value)
    return None


def _start(attributes: Mapping[str, Any]) -> str | None:
    # Scheduler's switch timeslots can be human-readable display strings.
    # A single HH:MM segment is safe to show; never infer start for ranges.
    import re
    slots = attributes.get("timeslots")
    if not isinstance(slots, list) or len(slots) != 1:
        return None
    item = slots[0]
    if isinstance(item, str) and re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", item):
        return item
    return None


def schedule_rows(
    schedules: Mapping[str, Mapping[str, Any]], entry_id: str
) -> list[dict[str, Any]]:
    """Return deterministic, display-only rows for exactly one entry."""
    rows = []
    for entity_id, attrs in schedules.items():
        if not isinstance(entity_id, str) or not isinstance(attrs, Mapping):
            continue
        if not owned_schedule(entity_id, attrs, entry_id):
            continue
        state = attrs.get("state")
        rows.append({
            "entity_id": entity_id,
            "name": schedule_name(attrs),
            "start": _start(attrs),
            "minutes": _minutes(attrs, entry_id),
            "weekdays": _weekdays(attrs),
            "enabled": state == "on" if state in ("on", "off") else None,
            "can_delete": state == "off",
            "editable": False,
        })
    return sorted(rows, key=lambda row: (row["name"].casefold(), row["entity_id"]))
