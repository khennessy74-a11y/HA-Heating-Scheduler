# Offline compatibility review

This is a development pre-release. Do **not** install it in the Home Assistant instance currently operating the working legacy heating scheduler.

## What CI currently proves

- Python / JSON / YAML structure and isolated unittest suite.
- Hassfest checks for integration metadata.
- Imports and a default-deny registration test against installed Home Assistant Python libraries.
- Mocked Scheduler Component mutation, ownership and concurrency rules.

## What CI does **not** prove yet

- That Scheduler Component accepts these exact `scheduler.add` / `scheduler.edit` / `scheduler.remove` payloads on a current Home Assistant installation.
- That Scheduler's generated schedule entities include the assumed `actions`, `friendly_name`, or state attributes.
- That a newly created schedule requested as disabled never briefly starts as enabled while the bridge resolves and turns it off.
- That a successful `switch.turn_on` or `switch.turn_off` service call means the schedule entity actually changed state.
- That a power interruption, reload or shutdown always leaves a physical heater in a safe state.
- That the approved dashboard works against integration-native entities and actions.

## Release gate

Do not enable physical heating service registrations or schedule-write opt-in until the above cases have been demonstrated in a **disposable** Home Assistant instance using a non-heating test switch.

The existing production YAML must remain unchanged. No automatic migration or recovery action may affect legacy schedules.

## Verified safety blocker: disabled-on-create (2026-10-09)

Upstream `custom_components/scheduler/store.py` declares `ScheduleEntry.enabled` with `default=True`. Upstream `const.py` `ADD_SCHEDULE_SCHEMA` does **not** accept an `enabled` field. Therefore `scheduler.add` cannot atomically create a disabled schedule via its public service, and calling `switch.turn_off` afterwards creates an activation window.

**Fail-closed mitigation:** Our Scheduler bridge now rejects `enabled=False` at creation *before* calling any Home Assistant service. This temporarily removes a reference-YAML feature from the integration preview. It is an intentional safety restriction until a safe, verified backend design exists.

Source: https://github.com/nielsfaber/scheduler-component/blob/main/custom_components/scheduler/store.py and https://github.com/nielsfaber/scheduler-component/blob/main/custom_components/scheduler/const.py

## Hard release gate: service-target dependency (2026-10-09)

Upstream Scheduler Component actions require a service name, and the preview bridge generates `heating_scheduler.start` actions. The Heating Scheduler integration has not yet registered `heating_scheduler.start`. Consequently, schedule writes MUST NOT be enabled even by manually adding the `enable_schedule_writes` option. `SCHEDULE_MUTATIONS_RELEASED = False` in `service_registration.py` now blocks all add/edit/remove requests until a future reviewed release explicitly changes the code. Creating schedules is not yet supported.

This is separate from the disabled-on-create risk, which remains blocked.
