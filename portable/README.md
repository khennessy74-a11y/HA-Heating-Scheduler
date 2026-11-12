# Portable Heating Scheduler — YAML candidate

This folder contains the complete **YAML-first portable candidate**. It is separate from the experimental Python integration in `custom_components/`.

## Status

The YAML and package checks pass in CI, but the candidate has **not** yet been installed and exercised in a second running Home Assistant instance. Treat it as a test candidate, not a stable release for a live heater.

## Contents

- `packages/heating_scheduler.yaml` — helpers, four manual boost scripts, six scheduler scripts, four automations and template validation sensor.
- `dashboard/main-heating-section.yaml` — complete main dashboard section: four boost tiles, schedule launcher, Heating switch and remaining-time timer.
- `dashboard/heating-control.yaml` — Heating Control pop-up (`#heatpop`).
- `dashboard/add-edit-schedule.yaml` — Add/Edit pop-up (`#addheat`).
- `dashboard/manage-schedules.yaml` — Manage Schedules pop-up (`#manageheat`).
- `INSTALL.md` — dependency-first manual installation, test and rollback instructions.
- `RELEASE_CANDIDATE.md` — evidence and remaining release gates.

## Install

Follow **[INSTALL.md](INSTALL.md)** from beginning to end. The required order is:

1. Install the backend Scheduler Component and all listed Lovelace custom cards first.
2. Restart / refresh Home Assistant as required and confirm the dependencies are loaded.
3. Back up Home Assistant; use a disposable instance and spare test switch.
4. Create `timer.heating_display_timer` once if it does not already exist.
5. Install the package, enable packages, validate and restart.
6. Confirm all ten `script.*` entities and the validation sensor exist.
7. Add the main dashboard section and all three pop-ups as Manual cards in the same view.
8. Test all four boosts, schedule actions, timer/switch safety and phone layout before considering live use.

This is a **manual YAML installation**, not a HACS custom integration. Do not install the experimental Python integration as well, and never let both controllers operate the same physical outlet.

## Dashboard dependencies

- [Expander Card](https://github.com/Alia5/lovelace-expander-card) — main dashboard expandable boost section.
- [Bubble Card](https://github.com/Clooos/Bubble-Card) — schedule launcher and pop-ups.
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — `mushroom-legacy-template-card`.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) — filtered schedule lists.
- [Button Card](https://github.com/custom-cards/button-card) — schedule rows and actions.
- [Super Text Input](https://github.com/skavan/super-text-input) — Add/Edit form.
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) — form styling.
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) — responsive Manage layout.

Install all frontend dependencies before importing the dashboard YAML. They are frontend custom cards, not Home Assistant OS add-ons.

## Safety and validation limits

- Do not point the candidate at a live heater until it has passed the separate-instance test plan.
- Do not run the legacy YAML scheduler and experimental Python integration against the same physical switch.
- Keep independent thermostat, over-temperature and electrical protections in place.
- CI parsing and representative Chromium layout checks are not a real Home Assistant frontend test or a phone test.
- The schedule filter depends on live Scheduler Component entity attributes and Auto-Entities behaviour that still need runtime verification.
