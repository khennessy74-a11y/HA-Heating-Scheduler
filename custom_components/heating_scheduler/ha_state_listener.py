"""Test-only HA state listener, never registered by integration setup.

Use only with a disposable switch and an injected fake runtime. Physical heating
control and the schedule mutation release gates remain closed.
"""
from __future__ import annotations

import asyncio
from collections.abc import Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .runtime_events import StateEventRouter


def attach_test_state_listener(
    hass: HomeAssistant, router: StateEventRouter, entity_id: str
) -> Callable[[], None]:
    """Install an isolated listener and return cleanup callback.

    Never register automatically on setup; no action calls are made here.
    """
    if not entity_id.startswith("switch.disposable_"):
        raise ValueError("Only a disposable switch test entity is permitted")

    pending: set[asyncio.Task] = set()
    closed = False

    @callback
    def on_change(event):
        if closed:
            return
        old = event.data.get("old_state")
        new = event.data.get("new_state")
        if old is None or new is None:
            return
        if event.data.get("entity_id") != entity_id:
            return
        task = hass.async_create_task(
            router.handle_change(entity_id, old.state, new.state),
            eager_start=False,
        )
        pending.add(task)
        task.add_done_callback(pending.discard)

    unsubscribe = async_track_state_change_event(hass, [entity_id], on_change)

    def cleanup():
        nonlocal closed
        if closed:
            return
        closed = True
        unsubscribe()
        for task in tuple(pending):
            task.cancel()

    return cleanup
