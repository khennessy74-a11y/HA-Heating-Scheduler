# HA Heating Scheduler

A community Home Assistant heating scheduler project, developed on GitHub.

> **Status: development / pre-release. Not ready to control a live heating system.**

## Goal

A GitHub-distributed custom integration for timed heating, using [Scheduler Component](https://github.com/nielsfaber/scheduler-component) as the recurring scheduling engine. **HACS is not required to install this project** (although Scheduler Component is a separately installed dependency).

## Prerequisites

**Heating Scheduler integration (backend):**
- Home Assistant with an available `switch.*` entity for the device you eventually plan to control.
- [Scheduler Component](https://github.com/nielsfaber/scheduler-component) for recurring schedules (separate custom integration).
- Manual installation from GitHub is supported; **HACS is not required to install Heating Scheduler itself**. HACS is a convenient way to install/manage some optional custom dependencies.

**Approved Lovelace mobile dashboard (additional frontend prerequisites):**
- [Bubble Card](https://github.com/Clooos/Bubble-Card) — popup interface.
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — dashboard controls/cards.
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) — dynamic schedule lists.
- [Button Card](https://github.com/custom-cards/button-card) — schedule rows and actions.
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) — appearance and spacing.
- [Super Text Inputs](https://github.com/iantrich/text-input-row) — **verify the exact custom text-input card used by the final dashboard YAML before publishing a dependency link**.

These frontend components are required **only if the finished dashboard actually uses them**. They are not needed for backend-only setup or GitHub CI checks. The integration-native dashboard is still being developed; we will verify the exact dependency list against its final YAML before release.

## Tested reference implementation

The existing YAML-package-based scheduler is the functional reference. Its tested features include:

- Create schedules with an **Enabled by default** toggle, or save disabled.
- Edit schedule name, start time, duration, weekdays, and enabled state together.
- Prevent duplicate names and require confirmation before deleting disabled schedules.
- Time-limited heating with switch confirmation and automatic OFF.
- iPhone-friendly one-column Heating Control and Manage dashboards.
- Tap a schedule in Heating Control to **edit** (not toggle); enable/disable within the edit form.

**Important:** Those features are tested in the existing YAML implementation, **not yet verified in this custom integration**. The working Home Assistant configuration must remain unchanged.

## Repository development plan

1. Import and review the beta integration source on a development branch.
2. Add automated Python, YAML, JSON and package structure checks.
3. Integrate the approved dashboard workflow.
4. Validate Scheduler Component services against a test Home Assistant instance and a **separate test switch**.
5. Publish a GitHub release with manual installation instructions.

## Safety / coexistence

Do not operate the new integration and the legacy YAML scheduler against the same physical switch at the same time. Both systems could independently turn it OFF. The integration must not migrate, disable or delete existing schedules automatically.

The target v1 switch types are smart power outlets, relays, Zigbee/Z-Wave and ESPHome devices exposed as `switch.*`. Thermostat `climate.*` entities need separate logic and are out of scope for v1.

Heating control must not be treated as a substitute for electrical, overtemperature, or hardware protection. Use appropriately rated switches and heaters.

See [ROADMAP.md](ROADMAP.md) for planned work.

## Support the project ☕

If this Heating Scheduler is useful and you'd like to support its development, [buy me a coffee](https://buymeacoffee.com/khennessy74). Contributions are entirely optional.
