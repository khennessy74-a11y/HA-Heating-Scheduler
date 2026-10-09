# Read-only Home Assistant schedule list

The preview integration registers a response-returning service:

`heating_scheduler.list_schedules`

Supply `entry_id` and request a response. The service requires a loaded
Heating Scheduler config entry and reads Scheduler Component switch state
attributes, displaying only entries whose `heating_scheduler.start` action
carries the matching entry ID.

The returned data follows `mobile_list.mobile_schedule_list` and contains
`read_only: true`. Edit and delete actions are null. There are **no writes**.

A disposable Home Assistant test fixture verifies:
- The owned row is returned; a foreign schedule is filtered out.
- A dummy switch stays OFF.
- The service is rejected after the entry unloads.
- Setup is idempotent and the service requires a response.

The earlier static Lovelace preview does **not** automatically call this
service; connecting response data to an actual UI is a separate milestone.

Do not install over or modify the working legacy Heating Scheduler.
