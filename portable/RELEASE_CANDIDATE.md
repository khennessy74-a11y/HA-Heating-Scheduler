# Portable Heating Scheduler — v1.0 Release Candidate Gate

**Status: complete YAML candidate, NOT validated on an installed Home Assistant instance.**

## Build evidence

- The portable YAML packaging workflow parses the package, main dashboard section and all three scheduler pop-ups and produces a downloadable ZIP.
- 19 structural and in-memory session tests exercise script shape, state gates, duration validation, confirmation-before-timer ordering, and timer/restart OFF actions. They do not run inside Home Assistant.
- Chromium tests inspect YAML-derived grid positioning at mobile widths; they do not load Home Assistant, Bubble Card, or a real phone.
- CI must pass on the current branch head before this candidate is considered packaged. A previous green run does not validate these new boost scripts or dashboard additions.

## Contents

- `packages/heating_scheduler.yaml`: the backend (four manual boost scripts, six scheduler scripts, four automations and input helpers).
- `dashboard/main-heating-section.yaml`: complete main dashboard section with four boost tiles, Heating switch, timer and schedule launcher.
- `dashboard/heating-control.yaml`: Heating Control pop-up.
- `dashboard/add-edit-schedule.yaml`: shared creation/edit form.
- `dashboard/manage-schedules.yaml`: schedule management.
- `INSTALL.md`: manual setup and rollback steps.

This ZIP is a **manual YAML installation candidate**; it is not a HACS custom integration. The experimental Python custom integration elsewhere in the repository remains a separate effort.

## Release blockers requiring a disposable HA instance

1. Install and load Scheduler Component; verify its actual service contract with the packaged scripts.
2. Create a separate timer helper and map `switch.heating` to a spare test switch.
3. Import the main dashboard section and all three pop-ups and verify Add, Edit, Rename, Save/Cancel, enable/disable and guarded Delete.
4. Verify phone layout and pencil/delete taps on an actual Home Assistant frontend.
5. Confirm start/stop, switch acknowledgement failure, timeout, Home Assistant restart and timer completion with a safe load.
6. Verify heating-only schedule filtering on a running Home Assistant instance. Both dashboard lists require the Scheduler entity's `entities` attribute to contain `script.heating_scheduled_run`, using Auto-Entities JSON-string matching; this has not been tested against live Scheduler attributes or the installed Auto-Entities version.
7. Prevent simultaneous control by the legacy YAML and new Python integration over the same physical outlet.

**Do not advertise v1.0 stable, merge the draft PR, or control a live heater based only on automated checks.**

## Installation path

See [INSTALL.md](INSTALL.md). Make a full backup, keep the tested production configuration untouched, and use a separate HA test environment when one becomes available.

## Release artifact

The **Portable YAML bundle** GitHub Actions workflow exports a minimal candidate ZIP with the backend YAML, three dashboard pop-ups and installation/release notes. Test source files are intentionally excluded. The workflow also publishes a matching `.sha256` file in the same Actions artifact. Download both files and verify the ZIP checksum before extracting. The candidate remains untested in an installed Home Assistant environment.
