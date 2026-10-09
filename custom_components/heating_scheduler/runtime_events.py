"""Inactive state-event router for the timed-heating runtime.

No Home Assistant state listeners are installed or activated by this module.
Future integration glue must route only the specifically configured switch
entity to the matching configuration entry.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol


class RuntimeEvents(Protocol):
    async def manual_off(self, entry_id: str) -> None: ...


class StateEventRouter:
    """Translate a configured target's OFF transition into session cancellation."""

    def __init__(self, runtime: RuntimeEvents, entry_targets: Mapping[str, str]) -> None:
        self._runtime = runtime
        self._targets = dict(entry_targets)

    async def handle_change(
        self, entity_id: str, old_state: str | None, new_state: str | None
    ) -> bool:
        """Handle a manual OFF; ignore unknown/unavailable and unrelated entities.

        OFF detection requires a transition from ON; repeated OFF events do not
        represent new manual switch-offs. The future adapter must distinguish
        controller-requested changes from genuine manual state changes.
        """
        if old_state != "on" or new_state != "off":
            return False
        matched = [
            entry_id for entry_id, target in self._targets.items()
            if entity_id == target
        ]
        # Ambiguous ownership is unsafe; don't cancel either silently.
        if len(matched) != 1:
            return False
        await self._runtime.manual_off(matched[0])
        return True


class UnsafeUnload(RuntimeError):
    """An active session prevents passive unload without explicit policy."""


def assert_idle_before_unload(active_entries: frozenset[str], entry_id: str) -> None:
    """Refuse to pretend a running session has been safely shut down."""
    if entry_id in active_entries:
        raise UnsafeUnload(
            "Cannot passively unload an active heating session; "
            "a verified shutdown policy is required"
        )
