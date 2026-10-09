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
    with pytest.raises(ValueError):
        attach_test_state_listener(hass, router, "switch.other_device")


@pytest.mark.asyncio
async def test_unknown_and_unavailable_transitions_are_ignored(hass, enable_custom_integrations):
    recorder = Recorder()
    entity = "switch.disposable_unavailable"
    cleanup = attach_test_state_listener(hass, StateEventRouter(recorder, {"a": entity}), entity)
    try:
        for value in ("on", "unavailable", "off", "unknown", "on", "off"):
            hass.states.async_set(entity, value)
            await hass.async_block_till_done()
        assert recorder.calls == ["a"]
    finally:
        cleanup()


@pytest.mark.asyncio
async def test_duplicate_entry_ownership_does_not_cancel_either(hass, enable_custom_integrations):
    recorder = Recorder()
    entity = "switch.disposable_shared"
    router = StateEventRouter(recorder, {"first": entity, "second": entity})
    cleanup = attach_test_state_listener(hass, router, entity)
    try:
        hass.states.async_set(entity, "on")
        await hass.async_block_till_done()
        hass.states.async_set(entity, "off")
        await hass.async_block_till_done()
        assert recorder.calls == []
    finally:
        cleanup()


@pytest.mark.asyncio
async def test_listener_does_not_react_to_other_entity(hass, enable_custom_integrations):
    recorder = Recorder()
    entity = "switch.disposable_owned"
    cleanup = attach_test_state_listener(hass, StateEventRouter(recorder, {"a": entity}), entity)
    try:
        hass.states.async_set("switch.disposable_other", "on")
        await hass.async_block_till_done()
        hass.states.async_set("switch.disposable_other", "off")
        await hass.async_block_till_done()
        assert recorder.calls == []
    finally:
        cleanup()


@pytest.mark.asyncio
async def test_cleanup_cancels_pending_callback(hass, enable_custom_integrations):
    started = asyncio.Event()
    was_cancelled = asyncio.Event()

    class BlockingRuntime:
        async def manual_off(self, entry_id):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                was_cancelled.set()
                raise

    entity = "switch.disposable_pending"
    cleanup = attach_test_state_listener(
        hass, StateEventRouter(BlockingRuntime(), {"a": entity}), entity
    )
    try:
        hass.states.async_set(entity, "on")
        await hass.async_block_till_done()
        hass.states.async_set(entity, "off")
        await asyncio.wait_for(started.wait(), timeout=2)
        cleanup()
        await asyncio.wait_for(was_cancelled.wait(), timeout=2)
    finally:
        cleanup()
