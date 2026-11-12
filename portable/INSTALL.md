# Heating Scheduler — portable YAML installation

**Status:** Published and confirmed working by the project maintainer. This is a **manual YAML installation**, not a HACS integration. HACS is required to install the Scheduler backend integration and the dashboard-card dependencies. Install and verify every dependency **before** importing any Heating Scheduler YAML.

The bundle contains one backend package, the complete main dashboard section, and three scheduler pop-ups.

## 1. Install HACS prerequisites first

If HACS is not installed, follow the [official HACS installation guide](https://www.hacs.xyz/docs/use/). Complete its setup and make sure the HACS Marketplace is available before continuing.

### 1.1 Required backend integration — HACS → Integrations

Install:

- **[Scheduler Component — open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=nielsfaber&repository=scheduler-component&category=integration)** · [GitHub source](https://github.com/nielsfaber/scheduler-component)

This is a required backend integration. It creates the scheduler entities and provides the `scheduler.add`, `scheduler.edit` and `scheduler.remove` actions used by this package.

After installation:

1. Restart Home Assistant.
2. Open **Settings → Devices & services → Add integration**.
3. Search for and add **Scheduler**.
4. Open **Developer Tools → Actions** and confirm the Scheduler actions are available before proceeding.

### 1.2 Required dashboard cards — HACS → Dashboard

Install **all eight** cards below. The links open the repository in your Home Assistant Marketplace; select Download/Install and follow any resource reload prompts.

| Card | HACS Marketplace install link | Used for |
|---|---|---|
| **Expander Card** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=Alia5&repository=lovelace-expander-card&category=plugin) · [Source](https://github.com/Alia5/lovelace-expander-card) | Expandable manual boost controls |
| **Bubble Card** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=Clooos&repository=Bubble-Card&category=plugin) · [Source](https://github.com/Clooos/Bubble-Card) | Schedule launcher and pop-ups |
| **Mushroom Cards** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=piitaya&repository=lovelace-mushroom&category=plugin) · [Source](https://github.com/piitaya/lovelace-mushroom) | Template cards in the pop-ups |
| **Auto-Entities** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-auto-entities&category=plugin) · [Source](https://github.com/thomasloven/lovelace-auto-entities) | Dynamic schedule lists |
| **Button Card** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=custom-cards&repository=button-card&category=plugin) · [Source](https://github.com/custom-cards/button-card) | Schedule rows and actions |
| **Super Text Input** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=skavan&repository=super-text-input&category=plugin) · [Source](https://github.com/skavan/super-text-input) | Add/Edit schedule form |
| **Card Mod** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-card-mod&category=plugin) · [Source](https://github.com/thomasloven/lovelace-card-mod) | Form styling |
| **Layout Card** | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-layout-card&category=plugin) · [Source](https://github.com/thomasloven/lovelace-layout-card) | Responsive Manage Schedules layout |

**If a Marketplace link cannot find a card:** in HACS open **Dashboard → ⋮ → Custom repositories**, paste the matching GitHub Source URL from the table, choose **Dashboard** as the category, add it, then install the repository. Some cards may already be available in the default Marketplace catalogue.

After installing all eight cards, follow HACS prompts to reload resources or restart Home Assistant. Hard-refresh your browser / Home Assistant app. Do not continue until the custom cards load without “Custom element doesn't exist” errors.

These are Lovelace dashboard cards, not Home Assistant OS add-ons.

### 1.3 Home Assistant prerequisites

- Home Assistant packages, scripts, automations, timers and template entities enabled.
- A target `switch.*` entity. The package defaults to `switch.heating`; use a safe test switch for initial verification.
- `timer.heating_display_timer`. Create it once as a UI Helper or in YAML if it does not already exist. Do not create a duplicate.

## 2. Prepare the installation

1. Back up your Home Assistant configuration.
2. Confirm Scheduler Component is loaded and all eight frontend cards are installed.
3. Choose the target `switch.*` entity. If it is not `switch.heating`, replace **every** `switch.heating` reference in `packages/heating_scheduler.yaml` with your chosen entity ID before installing. This package controls a `switch.*` entity; it does not directly control a `climate.*` entity.
4. Create `timer.heating_display_timer` once, with restore enabled, unless it already exists.

## 3. Install the backend package

1. Copy `packages/heating_scheduler.yaml` to `/config/packages/heating_scheduler.yaml`.
2. Enable packages in `/config/configuration.yaml` using this stanza:

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

## 5. Verify operation

- Run each of the four manual boost scripts and confirm the switch turns on, the timer shows the matching duration, and the switch turns off at expiry.
- Test direct manual OFF and confirm the timer is cancelled.
- Create, enable, disable, edit, rename and delete disposable schedules.
- Confirm schedules cannot be deleted while enabled.
- Test switch-ON acknowledgement, timer expiry, Home Assistant restart behaviour and dashboard navigation.
- Check the layout on desktop and a real phone.

Use appropriately rated switching hardware and retain independent thermostat, over-temperature and electrical protections. Never run this YAML controller and the experimental Python integration against the same physical switch; both could independently control it.

## 6. Rollback

Disable disposable schedules, remove the new dashboard cards, remove the new package file and restart Home Assistant. Do not remove a timer or Scheduler Component that other automations use.

## Why this is not a HACS YAML install

HACS installs custom integrations and frontend cards; it does not automatically install arbitrary package YAML or Lovelace card YAML. This project package is installed manually. The separate experimental Python integration under `custom_components/` is not part of this portable package.

## Download and verify the package (Windows)

1. Open the latest successful **Portable YAML bundle** workflow run in GitHub Actions. Download its artifact and extract the GitHub artifact wrapper. It contains the candidate installer ZIP and its `.sha256` checksum.
2. In PowerShell, run `Get-FileHash -Algorithm SHA256 .\HA-Heating-Scheduler-portable-YAML-candidate.zip` and compare the hash to the first hexadecimal value in the matching `.sha256` file.
3. Extract the candidate installer ZIP only after the hashes match.
