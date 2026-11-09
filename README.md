# HA Heating Scheduler

A community Home Assistant heating scheduler project, developed on GitHub.

> **Status: pre-release. The portable YAML candidate is available for isolated testing; neither track is approved for controlling a live heating system.**

## Two development tracks

### Portable YAML candidate

The `portable/` folder contains a complete manual-install candidate:

- A Home Assistant package with helpers, scripts, automations and timer handling.
- Three Lovelace pop-ups for Heating Control, Add/Edit and Manage Schedules.
- Installation, rollback and release-gate documentation.

Start with **[portable/INSTALL.md](portable/INSTALL.md)**. The candidate is distributed as a ZIP by the **Portable YAML bundle** GitHub Actions workflow. It is not a HACS custom integration.

### Experimental Python integration

The `custom_components/` tree is a separate, experimental integration track. It is not included in the portable YAML ZIP and should not be installed alongside the YAML controller on the same physical switch.

## Portable YAML prerequisites

**Backend:**
- Home Assistant with packages, scripts, automations, timers and template entities.
- [Scheduler Component](https://github.com/nielsfaber/scheduler-component), installed separately, with its `scheduler.add`, `scheduler.edit` and `scheduler.remove` services available.
- A test `switch.*` entity. The default package entity is `switch.heating`; map it to a spare test outlet or relay before testing.
- A `timer.heating_display_timer` helper, created once.

**Dashboard (only if using the supplied pop-ups):**
- [Bubble Card](https://github.com/Clooos/Bubble-Card)
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — the YAML uses `mushroom-legacy-template-card`.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities)
- [Button Card](https://github.com/custom-cards/button-card)
- [Super Text Input](https://github.com/skavan/super-text-input)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card)

## What is covered by the checks

The portable workflow parses and packages the YAML, runs structural/in-memory checks and checks representative mobile grid positioning in Chromium. These checks do **not** run the scripts inside Home Assistant, load the actual custom frontend cards, or replace testing on a real phone.

Remaining runtime gates include validating Scheduler Component services and entity attributes, schedule filtering, Add/Edit/Delete actions, timer expiry, switch acknowledgement, restart behaviour and mobile presentation in a disposable Home Assistant instance.

## Safety / coexistence

Do not operate the YAML scheduler and experimental Python integration against the same physical switch. Both systems could independently turn it OFF. Keep the working Home Assistant configuration unchanged while testing the candidate on a separate instance and spare switch.

Heating control is not a substitute for electrical, over-temperature or hardware protection. Use appropriately rated switches and heaters, with independent safety controls.

See [portable/README.md](portable/README.md) for the YAML candidate overview and [ROADMAP.md](ROADMAP.md) for planned work.

## Support the project ☕

If this project is useful and you'd like to support its development, [buy me a coffee](https://buymeacoffee.com/khennessy74). Contributions are entirely optional.
