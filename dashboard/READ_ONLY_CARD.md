# Read-only Lovelace card — development preview

The repository now includes `dashboard/heating-scheduler-read-only-card.js`,
a self-contained, single-column custom card. It requests the response of
`heating_scheduler.list_schedules` using the Home Assistant WebSocket
`call_service` command with `return_response: true`. It shows the schedule
name, time/duration/weekdays subtitle and Enabled/Disabled/Unknown status.

It has **only a Refresh button**. There are no edit, delete, schedule toggle,
heater ON/OFF or other mutating actions. All schedule text uses `textContent`
rather than HTML injection. It loads on first display and refreshes only on
explicit request; no aggressive polling.

## Development usage on a disposable Home Assistant instance ONLY

1. Install the unreleased integration on a disposable HA instance, **not** on
   the working home-heating system.
2. Copy `heating-scheduler-read-only-card.js` to its local
   `/config/www/` folder.
3. Add a dashboard resource `/local/heating-scheduler-read-only-card.js`
   as JavaScript module.
4. Supply a valid, loaded Heating Scheduler config entry ID:

```yaml
type: custom:heating-scheduler-read-only-card
entry_id: YOUR_DISPOSABLE_TEST_ENTRY_ID
title: Heating Control
```

The older `mobile-preview.yaml` remains an example static layout. This card
is the first functional read-only display, not the final Bubble/Mushroom-based
three-popup interface. Browser and actual Scheduler Component compatibility
still require separate testing. Never replace the existing working dashboard.
