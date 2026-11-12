# Portable Heating Scheduler — YAML package

This folder contains the complete **YAML-first portable package**. It is separate from the experimental Python integration in `custom_components/`.

## Status

**Published and confirmed working by the project maintainer.** This is a manual YAML package. HACS is used to install the required backend integration and frontend cards; the package and dashboard YAML are then installed manually.

## Contents

- `packages/heating_scheduler.yaml` — helpers, four manual boost scripts, six scheduler scripts, four automations and template validation sensor.
- `dashboard/main-heating-section.yaml` — complete main dashboard section: four boost tiles, schedule launcher, Heating switch and remaining-time timer.
- `dashboard/heating-control.yaml` — Heating Control pop-up (`#heatpop`).
- `dashboard/add-edit-schedule.yaml` — Add/Edit pop-up (`#addheat`).
- `dashboard/manage-schedules.yaml` — Manage Schedules pop-up (`#manageheat`).
- `INSTALL.md` — HACS prerequisites, Marketplace install links, manual installation, verification and rollback instructions.
- `RELEASE_CANDIDATE.md` — package validation notes and release information.

## Required HACS Marketplace dependencies

Install these before importing the package or dashboard YAML.

### Backend integration — HACS → Integrations

- **[Scheduler Component — install via HACS Marketplace](https://my.home-assistant.io/redirect/hacs_repository/?owner=nielsfaber&repository=scheduler-component&category=integration)** · [GitHub source](https://github.com/nielsfaber/scheduler-component)

After installing, restart Home Assistant and add **Scheduler** from **Settings → Devices & services → Add integration**. Confirm its Scheduler actions/services are available.

### Frontend cards — HACS → Dashboard

| Card | HACS install link | Purpose |
|---|---|---|
| Expander Card | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=Alia5&repository=lovelace-expander-card&category=plugin) · [Source](https://github.com/Alia5/lovelace-expander-card) | Expandable boost section |
| Bubble Card | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=Clooos&repository=Bubble-Card&category=plugin) · [Source](https://github.com/Clooos/Bubble-Card) | Schedule launcher and pop-ups |
| Mushroom Cards | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=piitaya&repository=lovelace-mushroom&category=plugin) · [Source](https://github.com/piitaya/lovelace-mushroom) | Template cards |
| Auto-Entities | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-auto-entities&category=plugin) · [Source](https://github.com/thomasloven/lovelace-auto-entities) | Dynamic schedule lists |
| Button Card | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=custom-cards&repository=button-card&category=plugin) · [Source](https://github.com/custom-cards/button-card) | Schedule rows and actions |
| Super Text Input | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=skavan&repository=super-text-input&category=plugin) · [Source](https://github.com/skavan/super-text-input) | Add/Edit form |
| Card Mod | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-card-mod&category=plugin) · [Source](https://github.com/thomasloven/lovelace-card-mod) | Form styling |
| Layout Card | [Install](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomasloven&repository=lovelace-layout-card&category=plugin) · [Source](https://github.com/thomasloven/lovelace-layout-card) | Responsive Manage layout |

If a card is not found through its Marketplace link, add its GitHub Source URL under **HACS → Dashboard → ⋮ → Custom repositories**, choose **Dashboard** as the category, then install it. Follow HACS prompts to reload frontend resources or restart Home Assistant, and refresh your browser/app.

## Install

Follow **[INSTALL.md](INSTALL.md)** from beginning to end. The required order is:

1. Install HACS if it is not already installed.
2. Install Scheduler Component from HACS Integrations, restart Home Assistant, and add the Scheduler integration.
3. Install all eight dashboard cards from HACS Dashboard/Marketplace.
4. Reload frontend resources / restart as requested, then confirm the custom cards load.
5. Back up Home Assistant and prepare the target switch and `timer.heating_display_timer`.
6. Install the package, enable packages, validate configuration and restart.
7. Confirm all ten `script.*` entities and the validation sensor exist.
8. Add the main dashboard section and all three pop-ups as Manual cards in the same view.
9. Verify the boost scripts, scheduler actions, timer/switch behaviour and phone layout.

The package requires a target `switch.*` entity (default `switch.heating`) and `timer.heating_display_timer`. Create the timer once if it does not already exist.

## Safety and coexistence

- Back up Home Assistant before installation and test the target switch safely.
- Do not run the YAML scheduler and experimental Python integration against the same physical switch.
- Keep independent thermostat, over-temperature and electrical protections in place.
- HACS dependencies are separate from the manual YAML package; installing the cards does not import the package YAML.
