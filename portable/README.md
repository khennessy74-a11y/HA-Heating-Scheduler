# Portable Heating Scheduler — YAML candidate

This folder contains the complete **YAML-first portable candidate**. It is separate from the experimental Python integration in `custom_components/`.

## Status

<badge-placeholder>

The package and all three dashboard pop-ups are included and pass the repository's automated YAML, structure, packaging and representative mobile-layout checks. They have **not** yet been installed and exercised in a second running Home Assistant instance. Treat this as a test candidate, not a stable release for a live heater.

## Contents

- `packages/heating_scheduler.yaml` — backend helpers, six scripts, four automations and template validation sensor.
- `dashboard/heating-control.yaml` — Heating Control pop-up (`#heatpop`).
- `dashboard/add-edit-schedule.yaml` — shared Add/Edit pop-up (`#addheat`).
- `dashboard/manage-schedules.yaml` — Manage Schedules pop-up (`#manageheat`).
- `INSTALL.md` — full manual installation, test and rollback instructions.
- `RELEASE_CANDIDATE.md` — evidence and remaining release gates.

## Install

Follow **[INSTALL.md](INSTALL.md)** from beginning to end. In brief:

1. Back up Home Assistant and install the separate [Scheduler Component](https://github.com/nielsfaber/scheduler-component).
2. Use a disposable Home Assistant instance and a spare test switch. Map every `switch.heating` reference in the package to that test switch if necessary.
3. Create `timer.heating_display_timer` once, unless it already exists.
4. Copy the package to `/config/packages/heating_scheduler.yaml`, enable packages, validate and restart.
5. Add all three dashboard YAML files as manual cards in the same view, keeping their popup hashes unchanged.
6. Test creation, editing, renaming, deletion, schedule filtering, switch acknowledgement, timer expiry and restart behaviour before considering live use.

This is a **manual YAML installation**, not a HACS custom integration. Do not install the experimental Python integration as well, and never let both controllers operate the same physical outlet.

## Dashboard dependencies

The dashboard YAML uses these custom cards:

- [Bubble Card](https://github.com/Clooos/Bubble-Card) — pop-ups.
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — `mushroom-legacy-template-card`.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) — filtered schedule lists.
- [Button Card](https://github.com/custom-cards/button-card) — schedule rows and actions.
- [Super Text Input](https://github.com/skavan/super-text-input) — `custom:super-text-input`.
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) — form styling.
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) — responsive Manage layout.

These are frontend dependencies; they are not needed for backend-only YAML checks.

## Safety and validation limits

- Do not point the candidate at a live heater until it has passed the separate-instance test plan.
- Do not run the legacy YAML scheduler and experimental Python integration against the same physical switch.
- Keep independent thermostat, over-temperature and electrical protections in place.
- The Chromium check uses a representative layout fixture; it is not a real Home Assistant frontend or iPhone test.
- The dashboard schedule filter depends on live Scheduler Component entity attributes and Auto-Entities behaviour that still need runtime verification.
