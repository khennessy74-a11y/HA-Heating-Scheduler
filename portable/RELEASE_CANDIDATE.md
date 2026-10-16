# Portable Heating Scheduler — v1.0 Release Candidate Gate

**Status: release-candidate source, NOT validated on an installed Home Assistant instance.**

## Build evidence

- The portable YAML packaging workflow parses the package and all three dashboard pop-ups and produces a downloadable ZIP.
- 17 structural and in-memory session tests exercise script shape, state gates, duration validation, confirmation-before-timer ordering, and timer/restart OFF actions. They do not run inside Home Assistant.
- Chromium tests inspect YAML-derived grid positioning at mobile widths; they do not load Home Assistant, Bubble Card, or a real iPhone.
- GitHub Actions green run: https://github.com/khennessy74-a11y/HA-Heating-Scheduler/actions/runs/38636653445

## Contents

- `packages/heating_scheduler.yaml`: the legacy-style backend (six scripts, four automations and input helpers).
- `dashboard/heating-control.yaml`: Heating Control pop-up.
- `dashboard/add-edit-schedule.yaml`: shared creation/edit form.
- `dashboard/manage-schedules.yaml`: schedule management.
- `INSTALL.md`: manual setup and rollback steps.

This ZIP is a **manual YAML installation candidate**; it is not itself a HACS custom integration. The experimental Python custom integration elsewhere in the repository remains a separate effort.

## Release blockers requiring a disposable HA instance

1. Install and load Scheduler Component; verify its actual service contract with the packaged scripts.
2. Create a separate timer helper and map `switch.heating` to a spare test switch.
3. Import all three pop-ups and verify Add, Edit, Rename, Save/Cancel, enable/disable and guarded Delete.
4. Verify phone layout and pencil/delete taps on an actual Home Assistant frontend.
5. Confirm start/stop, switch acknowledgement failure, timeout, Home Assistant restart and timer completion with a safe load.
6. Verify heating-only schedule filtering on a running Home Assistant instance. Both dashboard lists now require the Scheduler entity's `entities` attribute to contain `script.heating_scheduled_run` (using Auto-Entities `$` JSON string matching), but this has not been tested against live Scheduler attributes or the actual installed Auto-Entities version.
7. Prevent simultaneous control by the legacy YAML and new Python integration over the same physical outlet.

**Do not advertise v1.0 stable, merge the draft PR, or control a live heater based only on automated checks.**

## Installation path

See [INSTALL.md](INSTALL.md). Make a full backup, keep the tested production configuration untouched, and use a separate test environment when one becomes available.

## Release artifact

The `Portable YAML bundle` GitHub Actions workflow exports a minimal candidate ZIP with the backend YAML, three dashboard pop-ups and installation/release notes. Test source files are intentionally excluded. The workflow also publishes a matching `.sha256` file in the same Actions artifact. Download both files and verify the ZIP checksum before extracting. The candidate remains untested in an installed Home Assistant environment.
