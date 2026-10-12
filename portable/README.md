# Portable dashboard source (work in progress)

This folder is the **YAML-first compatibility track**, separate from the experimental Python integration under `custom_components/`.

## Status

- `add-edit-schedule.yaml`: imported from the user's tested `#addheat` pop-up. The redundant `icon_tap_action` has been removed so tapping the icon no longer bypasses Edit mode and calls `script.heating_create_schedule`. YAML was parsed locally. **Device testing is still required.**
- `heating-control.yaml`: **not yet imported**. Source was shared in the conversation, but it must be carried over without changing action/delimiter levels for nested button cards.
- `manage-schedules.yaml`: **not yet imported**. Source was shared; iPhone layout must be checked.
- `packages/heating_scheduler.yaml`: **not yet imported**. Use the tested Home Assistant package, not an invented rewrite.

## Installation is not yet supported

**Do not install only `add-edit-schedule.yaml`**: it references many helpers and scripts provided by the legacy package and requires the other pop-ups (`#heatpop` and `#manageheat`).

The eventual portable archive will contain the package, three pop-ups, timer setup instructions and dependency list. It will not silently replace another instance's device entity. The default `switch.heating` must be mapped to the target smart outlet or relay.

Do not run the old YAML controller and the new Python integration against the same real heater. An independent thermostat / thermal safety cutout is still required where applicable.

## Next validation

1. Bring over the remaining two pop-ups and backend YAML.
2. Parse all YAML files without modifying JavaScript template delimiters.
3. Add mobile-specific label/action positioning that avoids overlay on narrow screens.
4. Test schedule Create, Edit, Rename, Delete and automatic OFF on a separate HA test instance.
5. Export an annotated ZIP with installation and rollback instructions.
