# Heating Scheduler — complete portable YAML candidate

**Status:** YAML syntax checked and package contents verified. Not yet tested on a second running Home Assistant instance. **Do not deploy to a live heater without independent safety controls and a successful test run.**

This bundle includes the backend package and **three** dashboard pop-ups (`heating-control.yaml`, `add-edit-schedule.yaml`, `manage-schedules.yaml`). Import all three as cards in the same Lovelace view, preferably at the end of that view. This is a **portable YAML candidate for manual installation**, not a HACS-installable integration.

## Requirements

- Home Assistant supporting packages, scripts, timers, template entities and recent automation YAML syntax.
- [Scheduler Component](https://github.com/nielsfaber/scheduler-component) installed as a separate custom integration, with its `scheduler.add`, `scheduler.edit`, `scheduler.remove` services available.
- A `switch.heating` entity, or replace **all** package references to it with the destination test `switch.*` entity.
- A timer entity `timer.heating_display_timer` (create as a UI Helper or define once via YAML).

**Dashboard dependencies** (required only when importing the supplied pop-ups):
- [Bubble Card](https://github.com/Clooos/Bubble-Card)
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — this YAML uses `mushroom-legacy-template-card`.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities)
- [Button Card](https://github.com/custom-cards/button-card)
- [Super Text Input](https://github.com/skavan/super-text-input) — registers `custom:super-text-input`.
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) — used by the Manage pop-up.

Install the frontend cards and confirm their Lovelace resources are loaded before importing the pop-ups. Backend-only testing does not require these dashboard cards.

## Setup

1. Back up your Home Assistant configuration. Use a **separate/disposable Home Assistant instance** for the first installation; do not replace your working heating setup.
2. Install Scheduler Component and confirm its three Scheduler services exist.
3. Create a Timer helper called Heating Display Timer with entity ID `timer.heating_display_timer`, restore enabled; **do not create a duplicate if it already exists**.
4. Pick a **spare test** smart outlet/relay for trial operation. Do not use the existing heater. If the test entity is not `switch.heating`, replace every `switch.heating` reference in `packages/heating_scheduler.yaml` with the actual test `switch.*` entity. Smart plugs, Zigbee/Z-Wave relays, ESPHome and Wi-Fi outlets are supported insofar as they expose a switch entity; `climate.*` is not supported by this candidate.
5. Copy `packages/heating_scheduler.yaml` to `/config/packages/heating_scheduler.yaml`, and enable packages in `/config/configuration.yaml`, for example:

    ```yaml
    homeassistant:
      packages: !include_dir_named packages
    ```

   Merge that stanza into your **existing** `homeassistant:` section; do not duplicate a top-level section.
6. Check Home Assistant YAML configuration before restarting. Reload scripts, automations and template entities if available, or restart once.
7. Verify that all six `script.heating_*` entities and `binary_sensor.heating_schedule_form_valid` exist.
8. In Dashboard Edit mode, add each YAML file from `dashboard/` as one Manual card in the **same dashboard view**, in this order: Heating Control, Add/Edit, Manage. Keep the popup hashes (`#heatpop`, `#addheat`, `#manageheat`) unchanged. Add an ordinary dashboard button that navigates to `#heatpop`. Confirm the custom card resources have loaded before testing. Test Add, Edit, Rename, Cancel, disabled-only Delete, enabled state and mobile layout using disposable schedules.
9. Test timer expiration and switch OFF, manual OFF, failed switch-ON confirmation, restart behaviour and schedule trigger using a **safe test load**, never a heater first.

## Why this isn't auto-installed through HACS

HACS custom integrations install `custom_components/` code; they do not automatically install arbitrary package YAML or Lovelace pop-ups. This ZIP is a manual YAML package. The separate Python integration in the repository is experimental and must not run against the same outlet as this YAML controller.

## Rollback

Disable the schedules created for testing, remove the new dashboard cards, remove the new package from your configuration, and restart Home Assistant. Do not delete an existing timer or Scheduler Component if other automations still rely on them.

## Known limits and release gates

- Both schedule lists filter `switch.schedule_*` entities by a serialized `entities` attribute containing `script.heating_scheduled_run`. This still needs validation with the actual Scheduler Component and Auto-Entities versions before using editing or deletion on a shared installation.
- `#manageheat` uses `layout-card`; ensure its Lovelace resource is installed.
- The card structure and ZIP pass CI parsing and Chromium **representative-grid** layout checks. The actual Home Assistant frontend, custom-card resources and nested Button Card actions are not runtime tested; verify on a real Home Assistant test instance and phone before release.
- Never activate this package and the experimental Python integration against the same physical outlet simultaneously.

## Download and verify the candidate (Windows)

1. Open the latest successful **Portable YAML bundle** run under GitHub Actions. Download its artifact and extract the GitHub artifact wrapper. It contains the candidate installer ZIP and its `.sha256` checksum.
2. In PowerShell, run `Get-FileHash -Algorithm SHA256 .\HA-Heating-Scheduler-portable-YAML-candidate.zip` and compare the displayed hash to the first hexadecimal value in the matching `.sha256` file. The two values must agree.
3. Only then extract the candidate installer ZIP. Its `portable/` folder contains the files documented above. Keep the production installation unchanged until the separate HA test gate passes.
