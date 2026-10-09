"""Real HA event bus tests without live entities or switch service calls."""
import asyncio

import pytest

from custom_components.heating_scheduler.runtime_events import StateEventRouter
from custom_components.heating_scheduler.ha_state_listener import attach_test_state_listener


class Recorder:
    def __init__(self):
        self.calls = []

    async def manual_off(self, entry_id):
        self.calls.append(entry_id)


@pytest.mark.asyncio
async def test_disposable_manual_off_event(hass, enable_custom_integrations):
    recorder = Recorder()
    router = StateEventRouter(recorder, {"test": "switch.disposable_sensor"})
    cleanup = attach_test_state_listener(hass, router, "switch.disposable_sensor")
    try:
        hass.states.async_set("switch.disposable_sensor", "on")
        await hass.async_block_till_done()
        hass.states.async_set("switch.disposable_sensor", "off")
        await hass.async_block_till_done()
        assert recorder.calls == ["test"]
        hass.states.async_set("switch.disposable_sensor", "off")
        await hass.async_block_till_done()
        assert recorder.calls == ["test"]
    finally:
        cleanup()


@pytest.mark.asyncio
async def test_listener_cleanup_unsubscribes(hass, enable_custom_integrations):
    recorder = Recorder()
    router = StateEventRouter(recorder, {"test": "switch.disposable_cleanup"})
    cleanup = attach_test_state_listener(hass, router, "switch.disposable_cleanup")
    hass.states.async_set("switch.disposable_cleanup", "on")
    await hass.async_block_till_done()
    cleanup()
    cleanup()
    hass.states.async_set("switch.disposable_cleanup", "off")
    await hass.async_block_till_done()
    assert recorder.calls == []


@pytest.mark.asyncio
async def test_listener_rejects_production_heater(hass, enable_custom_integrations):
    recorder = Recorder()
    router = StateEventRouter(recorder, {"a": "switch.heating"})
    with pytest.raises(ValueError):
        attach_test_state_listener(hass, router, "switch.heating")
    with pytest.raises(ValueError):
        attach_test_state_listener(hass, router, "light.disposable_test")
