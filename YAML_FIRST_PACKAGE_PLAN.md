# YAML-first simplification / packaging gate

Status: **proposal on a separate branch**. No production integration code or existing Home Assistant configuration is changed by this document.

## Decision

The **tested legacy YAML heating scheduler and its three Lovelace pop-ups** are the reference behaviour. Scheduler Component remains the recurring scheduler. Avoid rewriting Scheduler's recurrence engine or recreating working YAML helpers without a demonstrated need.

Two supported distribution paths are distinct:

1. **Portable YAML bundle (fastest, least risk)** — ship an annotated Home Assistant package, three dashboard YAML files, and setup instructions. Copying these into a second HA instance is manual; this is *not* a custom integration and HACS will not automatically deploy the package or dashboards.
2. **Optional HACS custom integration (later)** — provide a real `custom_components/heating_scheduler` integration with a config flow, user-selectable target switch, and native runtime services. It can use Scheduler Component, but its own scripts/entities/dashboard must be tested independently. HACS installs the integration files, not arbitrary Lovelace YAML or `packages/` configuration.

## Proven legacy behaviour to preserve

- Add and edit names, start time, duration, weekdays; preserve enabled/disabled states.
- Duplicate-name validation and guarded deletion of disabled schedules.
- Confirm switch ON before starting a display timer; switch OFF after timer finishes.
- On HA startup request OFF and cancel the timer; manual OFF cancels active timer.
- Shared `#addheat` editor, `#heatpop` control pop-up, `#manageheat` management pop-up.
- Mobile layout: no pencil/bin overlap, no inaccessible touch target.
- **Never** automatically migrate, delete, disable or rename legacy schedules.

## Packaging checklist (YAML path)

- [ ] Commit a clean **source-of-truth** version of `packages/heating_scheduler.yaml`; review against the user's currently tested file, not a reconstructed approximation.
- [ ] Commit the three **exact working** dashboard definitions separately, preserving nested button-card JavaScript templates.
- [ ] Include `timer.heating_display_timer` definition or clear UI Helper instructions; avoid defining it twice.
- [ ] Document how to map `switch.heating` to a destination smart outlet or relay; no hardware IDs, keys or secrets.
- [ ] Document Scheduler Component and dashboard-card dependencies, including exact frontend resource names.
- [ ] Correct separately handled icon taps: the Add/Edit Save button's `icon_tap_action` must not always call the create script.
- [ ] Document dynamic `switch.schedule_*` filter's potential to include unrelated schedules.
- [ ] Validate YAML structure and documented installation on a **disposable HA instance**.
- [ ] Test a disposable schedule end-to-end, including an iPhone-width dashboard.
- [ ] Package ZIP with installation/rollback steps and a clear version number.

## HACS integration scope (minimum useful product)

- [ ] Select target `switch.*` entity through HA config flow; default name `switch.heating` is illustrative only.
- [ ] Integrate with installed Scheduler Component without duplicating recurrence logic.
- [ ] Provide session countdown and safe OFF/restart handling with tested ownership rules.
- [ ] Offer supported schedule Create/Edit/Delete flow, preserve disabled state and guard duplicate names.
- [ ] Provide user-facing dashboard installation instructions or a dedicated frontend distribution method; **do not** assert that HACS automatically installs the three pop-ups.
- [ ] Test coexistence **only with a spare test switch**. Never run legacy and new controllers on the same physical output at once.
- [ ] Complete actual HA runtime tests before calling anything production-ready.

## Release gate

Do not merge or label v1 stable until the install path, timed heating, state confirmation, restart safety, Scheduler API compatibility, editor, and mobile layout have passed in a spare HA environment. CI-only mock tests are insufficient.

## Non-goals now

- A new recurrence engine.
- Generic `climate.*` thermostat support (separate semantics from a switch).
- Auto-migration of old Scheduler entities.
- Refactoring the legacy production package purely to make the Python integration cleaner.
