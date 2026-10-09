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
