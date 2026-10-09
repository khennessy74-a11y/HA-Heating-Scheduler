# Mobile workflow preview (read-only)

`heating-scheduler-workflow-preview.js` provides a **functional navigation
prototype**, not a functioning schedule editor. It uses only the approved
`heating_scheduler.list_schedules` read-only response service.

- Heating Control lists owned schedules and opens an editing **preview** on row tap.
- Manage Schedules provides an Edit navigation button per schedule. Delete is
  visibly disabled, irrespective of schedule enabled state.
- Add/Edit shows the planned fields (name, time, duration, weekdays, enabled).
  All inputs and Save are disabled. Existing structured timings are not yet
  available and are **not** guessed or loaded into an editable form.
- Enabled/Disabled status is descriptive; taps never toggle a schedule.

All returned text uses DOM `textContent`. The card has no call to heater,
Scheduler Component write services, or integration mutations.

## Disposable instance example

Copy JavaScript into `/config/www/`, register Lovelace resource
`/local/heating-scheduler-workflow-preview.js`, then use:

```yaml
type: custom:heating-scheduler-workflow-preview
entry_id: YOUR_DISPOSABLE_TEST_ENTRY_ID
```

Use only in a disposable test installation. It is **not** a replacement for
the working legacy dashboard and is not the final Bubble/Mushroom popup UI.
Actual browser and Scheduler Component integration tests remain outstanding.

## Verified display fields (upstream Scheduler Component switch.py)

Scheduler Component exposes `weekdays`, `actions` and `timeslots` as switch state attributes. For a single start-only timeslot, it exposes an `HH:MM` string, so the read-only mobile response now carries validated `start`, `minutes`, `weekdays` and `enabled` fields into the disabled Add/Edit preview. More complex or incomplete timeslots show `Unavailable`. Nothing becomes editable. This is **not** a complete structured Scheduler editor integration.

## Form controls upgrade

The disabled Add/Edit preview now uses a time input, duration dropdown with the eight approved durations, seven weekday checkboxes, and an Enabled checkbox. The enabled checkbox defaults checked on new schedule previews and reads the known state on edit. All fields remain disabled. No Save action or backend write path has been added. Unknown start times remain blank, and unknown enabled state is labelled separately.

## Manage and confirmation preview

In the Manage Schedules screen, an enabled or unknown-state schedule has **no delete button**. A disabled schedule marked deletion-eligible by the read-only response has a **Review** button which opens a confirmation-preview screen. Cancel returns to Manage Schedules. **Confirm deletion remains disabled and no delete service is invoked**, regardless of state. This allows us to validate the mobile safety workflow without exposing schedule mutation.
