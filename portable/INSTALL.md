# Heating Scheduler — complete portable YAML candidate

**Status:** YAML syntax checked. Not yet tested on a second running Home Assistant instance. **Do not deploy to a live heater without independent safety controls and a test run.**

This bundle includes the backend package and **three** dashboard pop-ups (`heating-control.yaml`, `add-edit-schedule.yaml`, `manage-schedules.yaml`). Import all three as cards in the same Lovelace view, preferably at the end of that view. This is a **portable YAML candidate**, not a HACS-installable integration. It still requires a disposable Home Assistant test.

## Requirements
- Home Assistant supporting packages, scripts, timers, and recent automation YAML syntax.
- Scheduler Component installed as a separate custom integration and its `scheduler.add`, `scheduler.edit`, `scheduler.remove` services available.
- A `switch.heating` entity (or replace *all* package references to it with the destination entity ID).
- A timer entity `timer.heating_display_timer` (create as a UI Helper or define once via YAML).

## Setup
1. Back up your Home Assistant configuration.
2. Install Scheduler Component and confirm Scheduler actions exist.
3. Create a Timer helper called Heating Display Timer with the entity ID `timer.heating_display_timer`, restore enabled; **do not** create a duplicate if it exists.
4. Pick a **spare test** smart outlet/relay for trial operation. Do not use the existing heater until validated. If it is not `switch.heating`, replace `switch.heating` references throughout `packages/heating_scheduler.yaml` with your actual `switch.*` entity. Smart plugs, Zigbee/Z-Wave relays, ESPHome and Wi-Fi outlets are supported insofar as they expose a switch entity; `climate.*` is not supported by this release.
5. Copy `packages/heating_scheduler.yaml` to `/config/packages/heating_scheduler.yaml`, and enable packages in `/config/configuration.yaml`, for example:

    homeassistant:
      packages: !include_dir_named packages

   Merge that stanza into your **existing** `homeassistant:` section; do not duplicate a top-level section.
6. Check Home Assistant YAML configuration before restarting. Reload scripts, automations and template entities if available, or restart once.
7. Verify that all six `script.heating_*` entities and `binary_sensor.heating_schedule_form_valid` exist.
8. In Dashboard Edit mode, import each YAML file from `dashboard/` as one manual card in the **same dashboard view**, in the order Heating Control, Add/Edit, Manage. Keep their hash values (`#heatpop`, `#addheat`, `#manageheat`) unchanged. Add an ordinary dashboard button that navigates to `#heatpop`. Verify the popup dependencies have loaded before testing. Then test Add, Edit, Rename, Cancel, disabled-only Delete, enabled state and mobile layout on disposable schedules.
9. Test timer expiration and switch OFF, manual OFF, failed switch-ON confirmation, restart behaviour and schedule trigger using a **safe test load**, never a heater first.

## Why this isn't auto-installed through HACS
HACS custom integrations install `custom_components/` code; they don't automatically install arbitrary package YAML or Lovelace pop-ups. The separate Python integration under GitHub is experimental and should not run against the same outlet as this YAML controller.

## Rollback
Disable the schedule(s) created for testing, remove the new dashboard cards, remove this package from your configuration, and restart Home Assistant. Do not delete an existing timer or Scheduler Component if other automations still rely on them.

## Frontend dependencies for existing pop-ups
Bubble Card, Mushroom, Auto-Entities, Button Card, Super Text Input, Card Mod, and Layout Card (for responsive Manage pop-up). Verify installed versions and exact custom-card resource names.
## Known limits and release gate
- The dynamic `switch.schedule_*` filter can include unrelated Scheduler schedules in a shared HA instance. **Do not use deletion or editing controls on unrelated schedules.** A heating-only filtering mechanism is needed before general release.
- `#manageheat` uses `layout-card`; ensure its Lovelace resource is installed.
- The card structure and generated ZIP are CI-validated for YAML parsing, **not browser- or Home Assistant-runtime tested**. The iPhone layout and nested Button Card actions still require manual verification.
- Never activate this package and the experimental Python integration against the same physical outlet simultaneously.
