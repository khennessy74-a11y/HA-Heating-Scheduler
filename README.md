# HA Heating Scheduler

A community Home Assistant heating scheduler project, developed on GitHub.

> **Status: published and working.** The portable YAML package has been confirmed working by the project maintainer.

## Portable YAML package

The `portable/` folder contains the ready-to-install manual YAML package:

- A Home Assistant package with helpers, six scheduler scripts, four manual boost scripts, automations and timer handling.
- The complete main Heating Control dashboard section, including four boost tiles, the Heating Schedules launcher, direct Heating switch and remaining-time timer.
- Three scheduler pop-ups: Heating Control, Add/Edit and Manage Schedules.
- Dependency-first installation, backup and rollback instructions.

Start with **[portable/INSTALL.md](portable/INSTALL.md)**. Install the required HACS integration and frontend cards listed below before importing the package or dashboard YAML.

## Required HACS Marketplace prerequisites

Install **all** items below before adding the Heating Scheduler YAML. The links open the matching repository in your own Home Assistant HACS/Marketplace installation. You must be logged in to Home Assistant with HACS installed.

### Backend integration

| Requirement | Install | Purpose |
|---|---|---|
| **Scheduler Component** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=nielsfaber&repository=scheduler-component&category=integration) · [Source](https://github.com/nielsfaber/scheduler-component) | Required backend integration. Provides the scheduler entities and `scheduler.add`, `scheduler.edit` and `scheduler.remove` actions used by the package. |

After installing Scheduler Component, restart Home Assistant, then go to **Settings → Devices & services → Add integration** and add **Scheduler**. Confirm the Scheduler actions/services are available before continuing.

### Dashboard cards (HACS → Dashboard)

| Required card | Install | Used for |
|---|---|---|
| **Expander Card** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=Alia5&repository=lovelace-expander-card&category=plugin) · [Source](https://github.com/Alia5/lovelace-expander-card) | Expandable manual boost controls |
| **Bubble Card** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=Clooos&repository=Bubble-Card&category=plugin) · [Source](https://github.com/Clooos/Bubble-Card) | Schedule launcher and pop-ups |
| **Mushroom Cards** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=piitaya&repository=lovelace-mushroom&category=plugin) · [Source](https://github.com/piitaya/lovelace-mushroom) | Template cards in the pop-ups |
| **Auto-Entities** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-auto-entities&category=plugin) · [Source](https://github.com/thomasloven/lovelace-auto-entities) | Dynamic schedule lists |
| **Button Card** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=custom-cards&repository=button-card&category=plugin) · [Source](https://github.com/custom-cards/button-card) | Schedule rows and actions |
| **Super Text Input** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=skavan&repository=super-text-input&category=plugin) · [Source](https://github.com/skavan/super-text-input) | Add/Edit schedule form |
| **Card Mod** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-card-mod&category=plugin) · [Source](https://github.com/thomasloven/lovelace-card-mod) | Form styling |
| **Layout Card** | [Open in HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-layout-card&category=plugin) · [Source](https://github.com/thomasloven/lovelace-layout-card) | Responsive Manage Schedules layout |

If a Marketplace link does not find a card, open HACS → Dashboard → ⋮ → **Custom repositories**, paste that card's GitHub source URL, select **Dashboard** as the category, and add/install it. Some repositories may already be listed in the default Marketplace catalogue.

### Other Home Assistant prerequisites

- Home Assistant packages, scripts, automations, timers and template entities enabled.
- A target `switch.*` entity (the package defaults to `switch.heating`).
- The `timer.heating_display_timer` helper/entity. Create it once if it does not already exist; do not create a duplicate.

## Installation

Follow **[portable/INSTALL.md](portable/INSTALL.md)** in order:

1. Install HACS if it is not already installed.
2. Install Scheduler Component and add the Scheduler integration.
3. Install all eight required dashboard cards from HACS Marketplace.
4. Restart Home Assistant / refresh frontend resources as instructed and confirm the dependencies are loaded.
5. Back up Home Assistant, prepare the target switch and timer, then install the package YAML.
6. Add the supplied dashboard cards and verify the controls.

The portable package is a **manual YAML installation**, not a HACS custom integration. HACS is used to install its backend integration and frontend card dependencies; the package YAML and supplied dashboard card YAML are copied into Home Assistant manually.

## Experimental Python integration

The `custom_components/` tree is a separate, experimental integration track. It is not included in the portable YAML package and must not be installed alongside the YAML controller on the same physical switch.

## Validation and safety

The repository includes automated YAML, structure and representative browser-layout checks. The maintainer has also confirmed the portable package working. Always back up your configuration and verify operation with a safe test load before relying on it for heating.

Do not operate the YAML scheduler and experimental Python integration against the same physical switch. Keep independent thermostat, over-temperature and electrical protections in place, and use appropriately rated switching hardware.

See [portable/README.md](portable/README.md) for the package overview and [ROADMAP.md](ROADMAP.md) for planned work.

## Support the project ☕

If this project is useful and you'd like to support its development, [buy me a coffee](https://buymeacoffee.com/khennessy74). Contributions are entirely optional.
