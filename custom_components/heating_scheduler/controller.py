"""Inactive, dependency-injected heating session controller.

No Home Assistant imports or automatic registration. A future integration
adapter must supply the switch calls and wait_for_on implementation.
Do not use with production heating until runtime tests are complete.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol

from .session import make_request


class HeatingSwitch(Protocol):
    async def is_off(self) -> bool: ...
    async def turn_on(self) -> None: ...
    async def wait_until_on(self, timeout: float) -> bool: ...
    async def turn_off(self) -> None: ...


class TimedHeatingController:
    """Own one heating session; never start concurrently.

    Only the active session can issue OFF in its finalizer. An external manual
    OFF notification marks the session as stopped and cancels its timer.
    """

    def __init__(
        self,
        switch: HeatingSwitch,
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        confirmation_seconds: float = 10.0,
    ) -> None:
        self._switch = switch
        self._sleep = sleep
        self._confirmation_seconds = confirmation_seconds
        self._task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()
        self._manually_off = False

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self, minutes: int) -> None:
        """Start asynchronously; raises ValueError if busy or unsafe."""
        async with self._lock:
            # Validate before creating or replacing task.
            req = make_request(
                minutes,
                timer_active=self.running,
                switch_off=await self._switch.is_off(),
            )
            self._manually_off = False
            self._task = asyncio.create_task(self._run(req.seconds))
            # Yield so immediate calls can observe start failures through task.
            await asyncio.sleep(0)

    async def _run(self, seconds: int) -> None:
        try:
            await self._switch.turn_on()
            confirmed = await self._switch.wait_until_on(self._confirmation_seconds)
            if not confirmed:
                raise RuntimeError("Heating switch did not confirm ON")
            await self._sleep(seconds)
        finally:
            # A physical/manual OFF cancels this task without a second OFF.
            if not self._manually_off:
                await self._switch.turn_off()

    async def notify_manual_off(self) -> None:
        """Cancel a countdown after external OFF, without toggling switch."""
        self._manually_off = True
        if self.running:
            assert self._task is not None
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def stop(self) -> None:
        """Cancel a running session, requesting OFF in the finalizer."""
        if self.running:
            assert self._task is not None
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def wait_finished(self) -> None:
        """Await the session result; use in tests and future HA adapter."""
        if self._task is not None:
            await self._task
