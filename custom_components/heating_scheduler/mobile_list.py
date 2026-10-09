"""Read-only mobile schedule list data, never exposed as an HA write service."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .schedule_projection import schedule_rows


def mobile_schedule_list(
    snapshots: Mapping[str, Mapping[str, Any]], entry_id: str,
) -> dict[str, Any]:
    """Render entry-owned schedule rows into a safe mobile UI data contract."""
    rows = schedule_rows(snapshots, entry_id)
    items = []
    for row in rows:
        enabled = row["enabled"]
        items.append({
            "entity_id": row["entity_id"],
            "title": row["name"] or "Unnamed schedule",
            "subtitle": _subtitle(row),
            "status": ("Enabled" if enabled is True
                       else "Disabled" if enabled is False else "Unknown"),
            "status_color": ("green" if enabled is True
                             else "grey" if enabled is False else "neutral"),
            "edit_action": None,
            "delete_action": None,
            "can_delete_after_confirmation": bool(row["can_delete"]),
        })
    return {
        "entry_id": entry_id,
        "title": "Heating Control",
        "read_only": True,
        "items": items,
        "empty_message": "No matching heating schedules" if not items else None,
    }


def _subtitle(row: Mapping[str, Any]) -> str:
    start = row["start"] or "Time unknown"
    duration = (f'{row["minutes"]} min' if row["minutes"] is not None
                else "Duration unknown")
    weekdays = ", ".join(day.capitalize() for day in (row["weekdays"] or []))
    return " · ".join((start, duration, weekdays or "Days unknown"))
