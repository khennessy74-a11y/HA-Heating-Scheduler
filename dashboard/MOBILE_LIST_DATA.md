# Dynamic mobile schedule list: read-only data model

`mobile_list.mobile_schedule_list(snapshots, entry_id)` provides a normalized
mobile one-column list of exactly the schedules owned by a configuration entry.
It includes the title, subtitle (time, duration, weekdays), Enabled / Disabled /
Unknown status and colour hints.

**Deliberate limits:** both `edit_action` and `delete_action` are null and
`read_only` is true. `can_delete_after_confirmation` is merely informational,
not permission to delete anything. This is not yet connected to a Lovelace card,
websocket API or HA sensor. The earlier static preview remains a preview.

Before rendering live cards: add a read-only HA-facing schedule source and
verify Scheduler Component's structured time data. Do not expose writes, connect
to the production heater, or alter the legacy dashboard.
