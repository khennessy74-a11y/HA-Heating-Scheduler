# Read-only schedule projection contract

`schedule_projection.schedule_rows(schedules, entry_id)` converts a snapshot
of Scheduler Component switch attributes into **display-only** rows.

Fields: `entity_id`, `name`, `start`, `minutes`, `weekdays`,
`enabled` (true / false / unknown), `can_delete` (informational only),
and `editable=False` while mutation services are gated.

Only schedules containing an action for `heating_scheduler.start` with the
exact entry ID appear. Foreign schedules are omitted. Unknown data is `None`
rather than invented. The projection does not register a service, sensor or
dashboard action, and does not touch production schedules.

**Important limitation:** Upstream Scheduler Component switch attributes may
not expose editable structured timing information. A display `timeslots`
string like `06:30 - 07:30` is deliberately not guessed as an editable
start time. The eventual Add/Edit workflow needs a verified structured
schedule source. The existing static Lovelace preview remains static.
