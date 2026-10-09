# JavaScript execution checks in GitHub Actions

The dedicated `dashboard-js` job uses Node 24 to parse both Lovelace cards
and executes the mobile workflow preview inside a lightweight fake DOM.
It verifies list-service request arguments, read-only list rendering,
navigation to Manage Schedules, disabled-only deletion review, Cancel,
seven disabled weekday inputs, and disabled Save. It never starts HA,
accesses a heater or makes a schedule-writing request.

**Limitation:** This is a DOM-behaviour smoke test, **not** a browser or
Home Assistant frontend integration test. Browser/mobile visual layout and
upstream Scheduler Component compatibility are separate release blockers.
