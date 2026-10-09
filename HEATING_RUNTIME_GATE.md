# Heating runtime release gate

The isolated `HeatingRuntimeCoordinator` is a **development-only module**.

- The `HEATING_RUNTIME_RELEASED` constant is `False`.
- Start and stop reject requests **before creating a Home Assistant switch adapter**.
- No HA services or state-change listeners have been registered for timed heating.
- The scheduler mutation gate remains separately closed.
- Mocked controller tests are not proof of recovery behaviour after a Home Assistant restart.

## Before enabling hardware operation

1. Prove that a supervised, disposable Home Assistant runtime can create and unload the integration safely.
2. Add an entry-bound switch adapter, state-change subscription and explicit service registration only for a non-heating test entity.
3. Define a shutdown/restart strategy that does not accidentally switch off a device operated by another integration.
4. Exercise service call failure, delayed confirmation, unavailability, manual-off, reload and timer expiry.
5. Verify these tests with actual Home Assistant dependencies, not only fakes.

Until then, **do not connect the new integration to the production heater**.

## Controller cancellation race review (2026-10-09)

A race existed where a stray manual-OFF callback could write the controller's cancellation flag when no session was running. Manual-OFF and stop transitions now acquire the same controller lock used by start and snapshot the task before cancelling it. Offline regression cases cover idle callbacks, concurrent starts, and repeated stop calls. These tests do not prove correct behaviour under all physical-switch or Home Assistant restart races; keep runtime release gates closed.
