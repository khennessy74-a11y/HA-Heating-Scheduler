# Heating Scheduler — complete portable YAML candidate

**Status:** YAML syntax checked and package contents verified. Not yet tested on a second running Home Assistant instance. **Do not deploy to a live heater without independent safety controls and a successful test run.**

This is a **manual YAML installation**, not a HACS integration. The bundle contains one backend package, the complete main dashboard section, and three scheduler pop-ups. Install and verify every dependency **before** importing any Heating Scheduler YAML.

## 1. Install all dependencies first

Do not start by copying the package. First install the prerequisites below, then confirm Home Assistant has loaded them.

### 1.1 Backend dependency

- [Scheduler Component](https://github.com/nielsfaber/scheduler-component) — install as a Home Assistant custom integration (HACS if available, otherwise follow its repository installation instructions). Restart Home Assistant after installing it. Confirm the `scheduler.add`, `scheduler.edit` and `scheduler.remove` services are available in Developer Tools → Actions.

### 1.2 Lovelace / frontend dependencies

Install all of these through HACS → Frontend (or the repository's documented HACS custom-repository method where needed):

- [Expander Card](https://github.com/Alia5/lovelace-expander-card) — required by the main dashboard section (`custom:expander-card`). If it is not listed in HACS, add `https://github.com/Alia5/lovelace-expander-card` as a **Dashboard** custom repository, then install it.
- [Bubble Card](https://github.com/Clooos/Bubble-Card) — main section and scheduler pop-ups.
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — pop-ups use `mushroom-legacy-template-card`.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) — schedule lists.
- [Button Card](https://github.com/custom-cards/button-card) — schedule controls and actions.
- [Super Text Input](https://github.com/skavan/super-text-input) — Add/Edit form (`custom:super-text-input`).
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) — form styling.
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) — responsive Manage Schedules layout.

After installing the frontend cards, restart Home Assistant if HACS requests it, then hard-refresh the browser / Home Assistant app so the Lovelace resources load. Confirm the cards are available before continuing. These are frontend custom cards, not Home Assistant OS add-ons.

### 1.3 Home Assistant prerequisites

- Home Assistant with packages, scripts, automations, timers and template entities enabled.
- A spare **test** `switch.*` entity. The default is `switch.heating`; do not connect this test candidate to a live heater.
- A timer entity `timer.heating_display_timer`. You can create it as a UI Helper or define it once in YAML. Do not create a duplicate if it already exists.

## 2. Prepare a safe test installation

1. Back up your Home Assistant configuration.
2. Use a separate/disposable Home Assistant instance for first installation. Keep your working Home Assistant heating configuration unchanged.
3. Select a spare test switch. If it is not `switch.heating`, replace **every** `switch.heating` reference in `packages/heating_scheduler.yaml` with that test entity ID before installing. This candidate controls a `switch.*` entity; it does not directly control a `climate.*` entity.
4. Create `timer.heating_display_timer` once, with restore enabled, unless it already exists.

## 3. Install the backend package

1. Copy `packages/heating_scheduler.yaml` to `/config/packages/heating_scheduler.yaml`.
2. Enable packages in `/config/configuration.yaml` using the following stanza:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   Merge this into your existing top-level `homeassistant:` section. Do **not** add a second `homeassistant:` key. The folder name in the include must match the actual folder name exactly; this example uses lowercase `packages`.
3. Run Home Assistant's configuration check. Resolve errors before restarting.
4. Restart Home Assistant (or reload the relevant scripts, automations and template entities if your version supports all of those reloads).
5. Confirm these entities exist:
   - `script.15_minute_boost`
   - `script.30_minute_boost`
   - `script.1_hour_boost`
   - `script.2_hour_boost`
   - `script.heating_scheduled_run`
   - `script.heating_cancel_schedule`
   - `script.heating_load_schedule_for_edit`
   - `script.heating_create_schedule`
   - `script.heating_delete_schedule`
   - `script.heating_update_schedule`
   - `timer.heating_display_timer`
   - `binary_sensor.heating_schedule_form_valid`

If any entity is missing, stop and inspect the configuration / startup logs. Do not continue to dashboard import until the backend entities exist.

## 4. Add the dashboard cards

In Dashboard → Edit dashboard, add each supplied YAML file as a **Manual** card. Add them to the same dashboard view so the Bubble Card navigation hashes work. Keep the hashes unchanged.

1. `dashboard/main-heating-section.yaml` — add this to the desired position in your dashboard. It supplies the Heating Control heading, expandable manual boost buttons, Heating Schedules launcher, direct Heating switch tile and timer remaining-time tile.
2. `dashboard/heating-control.yaml` — scheduler pop-up (`#heatpop`).
3. `dashboard/add-edit-schedule.yaml` — Add/Edit pop-up (`#addheat`).
4. `dashboard/manage-schedules.yaml` — Manage pop-up (`#manageheat`).

The main section and pop-ups must be in the same view. Do not replace your existing dashboard or create a second `homeassistant:` configuration block. The dashboard files are card YAML, not full dashboard configuration files.

## 5. Test before live use

Use only the spare test switch / safe test load:

- Run each of the four manual boost scripts and confirm the switch turns on, the timer shows the matching duration, and the switch turns off at expiry.
- Test direct manual OFF and confirm the timer is cancelled.
- Create, enable, disable, edit, rename and delete disposable schedules.
- Confirm schedules cannot be deleted while enabled.
- Test switch-ON acknowledgement, timer expiry, Home Assistant restart behaviour and dashboard navigation.
- Check the layout on a real phone as well as desktop.

The automated checks do not run the scripts inside Home Assistant, load the actual custom frontend cards, or replace testing on a real phone. Do not use a live heater until the separate-instance test plan passes and independent thermostat, over-temperature and electrical protections are in place.

## 6. Rollback

Disable disposable schedules, remove the new dashboard cards, remove the new package file and restart Home Assistant. Do not remove a timer or Scheduler Component that other automations use.

## Why this is not a HACS YAML install

HACS installs custom integrations and frontend cards; it does not automatically install arbitrary package YAML or Lovelace cards. This project bundle is manually installed YAML. The separate experimental Python integration under `custom_components/` is not part of this portable package. Never run both controllers against the same physical outlet.

## Download and verify the candidate (Windows)

1. Open the latest successful **Portable YAML bundle** workflow run in GitHub Actions. Download its artifact and extract the GitHub artifact wrapper. It contains the candidate installer ZIP and its `.sha256` checksum.
2. In PowerShell, run `Get-FileHash -Algorithm SHA256 .\HA-Heating-Scheduler-portable-YAML-candidate.zip` and compare the hash to the first hexadecimal value in the matching `.sha256` file.
3. Extract the candidate installer ZIP only after the hashes match. Keep the production installation unchanged until the separate Home Assistant test gate passes.
