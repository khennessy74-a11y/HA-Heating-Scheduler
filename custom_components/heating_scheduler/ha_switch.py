"""Home Assistant switch adapter (not registered or activated).

This module exposes the operations required by TimedHeatingController.
It is deliberately NOT instantiated by __init__.py or any service.
"""
from __future__ import annotations

import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.event import async_track_state_change_event


class HomeAssistantHeatingSwitch:
    """Adapter for a single configured switch; no background startup."""

    def __init__(self, hass: HomeAssistant, entity_id: str) -> None:
        if not entity_id.startswith("switch."):
            raise ValueError("Heating target must be a switch entity")
        self.hass = hass
        self.entity_id = entity_id

    async def is_off(self) -> bool:
        """Unknown/unavailable is not an acceptable OFF state."""
        state = self.hass.states.get(self.entity_id)
        return state is not None and state.state == STATE_OFF

    async def turn_on(self) -> None:
        await self.hass.services.async_call(
            "switch", "turn_on", {"entity_id": self.entity_id}, blocking=True
        )

    async def wait_until_on(self, timeout: float) -> bool:
        """Await ON state, including the race between state read and subscription."""
        if (state := self.hass.states.get(self.entity_id)) is not None and state.state == STATE_ON:
            return True
        future = self.hass.loop.create_future()

        def state_changed(event) -> None:
            new = event.data.get("new_state")
            if new is not None and new.state == STATE_ON and not future.done():
                future.set_result(True)

        unsubscribe = async_track_state_change_event(
            self.hass, [self.entity_id], state_changed
        )
        try:
            if (state := self.hass.states.get(self.entity_id)) is not None and state.state == STATE_ON:
                return True
            try:
                await asyncio.wait_for(future, timeout=timeout)
                return True
            except asyncio.TimeoutError:
                return False
        finally:
            unsubscribe()

    async def turn_off(self) -> None:
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": self.entity_id}, blocking=True
        )
