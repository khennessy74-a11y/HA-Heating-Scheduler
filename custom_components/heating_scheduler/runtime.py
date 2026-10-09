"""Fail-closed timed-heating runtime coordinator.

Not registered in Home Assistant. A separate future activation decision and
real Home Assistant runtime tests are required before any heating service
handler may call this coordinator.
"""
from __future__ import annotations

import asyncio
from collections.abc import Callable

from .controller import HeatingSwitch, TimedHeatingController
from .const import DURATIONS


class HeatingRuntimeUnavailable(RuntimeError):
    """Hardware actuation has not passed release approval."""


HEATING_RUNTIME_RELEASED = False


class HeatingRuntimeCoordinator:
    """Own controllers per entry; reject all requests until release gate opens."""

    def __init__(self, make_switch: Callable[[str], HeatingSwitch]) -> None:
        self._make_switch = make_switch
        self._controllers: dict[str, TimedHeatingController] = {}
        self._lock = asyncio.Lock()

    @property
    def active_entries(self) -> frozenset[str]:
        return frozenset(
            key for key, controller in self._controllers.items()
            if controller.running
        )

    async def start(self, entry_id: str, minutes: int) -> None:
        if not HEATING_RUNTIME_RELEASED:
            raise HeatingRuntimeUnavailable(
                "Timed heating is not enabled in this development release"
            )
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError("A configuration entry ID is required")
        if type(minutes) is not int or minutes not in DURATIONS:
            raise ValueError("Unsupported heating duration")
        async with self._lock:
            controller = self._controllers.get(entry_id)
            if controller is None:
                controller = TimedHeatingController(self._make_switch(entry_id))
                self._controllers[entry_id] = controller
            await controller.start(minutes)

    async def stop(self, entry_id: str) -> None:
        if not HEATING_RUNTIME_RELEASED:
            raise HeatingRuntimeUnavailable(
                "Timed heating is not enabled in this development release"
            )
        controller = self._controllers.get(entry_id)
        if controller is not None:
            await controller.stop()

    async def manual_off(self, entry_id: str) -> None:
        """For future state listeners; currently no listeners are attached."""
        controller = self._controllers.get(entry_id)
        if controller is not None:
            await controller.notify_manual_off()

