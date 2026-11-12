# HA Heating Scheduler

A community Home Assistant heating scheduler project, developed on GitHub.

> **Status: pre-release.** The portable YAML candidate is for isolated testing only. It is not approved for controlling a live heating system.

## Two development tracks

### Portable YAML candidate

The `portable/` folder contains a manual-install candidate:

- A Home Assistant package with helpers, six scheduler scripts, four manual boost scripts, automations and timer handling.
- The complete main Heating Control dashboard section, including four boost tiles, the Heating Schedules launcher, direct Heating switch and remaining-time timer.
- Three scheduler pop-ups: Heating Control, Add/Edit and Manage Schedules.
- Dependency-first installation, rollback and release-gate documentation.

Start with **[portable/INSTALL.md](portable/INSTALL.md)**. Install the Scheduler Component and every required Lovelace custom card before importing the package or dashboard YAML. The candidate is distributed as a ZIP by the **Portable YAML bundle** GitHub Actions workflow. It is a manual YAML installation, not a HACS custom integration.

### Experimental Python integration

The `custom_components/` tree is a separate, experimental integration track. It is not included in the portable YAML ZIP and must not be installed alongside the YAML controller on the same physical switch.

## Portable candidate dependencies

**Backend first:** Home Assistant packages/scripts/automations/timer/template support; [Scheduler Component](https://github.com/nielsfaber/scheduler-component); a test `switch.*` entity; and `timer.heating_display_timer`.

**Frontend cards first:** [Expander Card](https://github.com/Alia5/lovelace-expander-card), [Bubble Card](https://github.com/Clooos/Bubble-Card), [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom), [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities), [Button Card](https://github.com/custom-cards/button-card), [Super Text Input](https://github.com/skavan/super-text-input), [Card Mod](https://github.com/thomasloven/lovelace-card-mod), and [Layout Card](https://github.com/thomasloven/lovelace-layout-card).

Follow the ordered checklist in [portable/INSTALL.md](portable/INSTALL.md); do not import Heating Scheduler YAML until the dependencies are installed and loaded.

## What is covered by the checks

The portable workflow parses and packages the YAML, runs structural/in-memory checks and checks representative mobile grid positioning in Chromium. These checks do **not** run scripts inside Home Assistant, load the actual custom frontend cards, or replace testing on a real phone.

Remaining runtime gates include verifying the four boost scripts and timer behaviour, Scheduler Component services and entity attributes, schedule filtering, Add/Edit/Delete actions, switch acknowledgement, restart behaviour and mobile presentation in a disposable Home Assistant instance.

## Safety / coexistence

Do not operate the YAML scheduler and experimental Python integration against the same physical switch. Both systems could independently turn it OFF. Keep the working Home Assistant configuration unchanged while testing the candidate on a separate instance and spare switch.

Heating control is not a substitute for electrical, over-temperature or hardware protection. Use appropriately rated switches and heaters, with independent safety controls.

See [portable/README.md](portable/README.md) for the YAML candidate overview and [ROADMAP.md](ROADMAP.md) for planned work.

## Support the project ☕

If this project is useful and you'd like to support its development, [buy me a coffee](https://buymeacoffee.com/khennessy74). Contributions are entirely optional.
