# Scheduler Component upstream contract review

Reference: [Scheduler Component](https://github.com/nielsfaber/scheduler-component), `main` branch, inspected 2026-10-09.

## Confirmed from source

- `custom_components/scheduler/services.yaml` declares `scheduler.add`, `scheduler.edit`, and `scheduler.remove`.
- Add accepts `weekdays`, `timeslots`, `repeat_type`, and optional `name`.
- Edit accepts `entity_id`, `weekdays`, `timeslots`, and optional `name`.
- Remove accepts `entity_id`.
- `switch.py` exposes an `actions` attribute containing `service` and, when present, `service_data`.
- `store.py` defines action storage with `service`, optional `entity_id`, and `service_data`.

## Not established from source inspection alone

1. Whether disabled-on-create is atomic. **Critical release blocker:** the current bridge calls `scheduler.add` then later `switch.turn_off`. A schedule might briefly be enabled.
2. Whether successful service calls imply confirmed state transitions.
3. Whether action attribute shape, storage names, and event propagation are stable across supported Scheduler Component releases.
4. Whether live update/rename results match simulated tests on an isolated running Home Assistant instance.

## Policy

Treat real-world heating actuation and schedule-write opt-in as **not release-ready** until verified in a disposable Home Assistant environment with a non-heating switch. The production YAML must not be modified or migrated.
