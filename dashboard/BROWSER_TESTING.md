# Browser milestone: real Chromium checks

CI now includes a separate real Chromium job, using Playwright in a disposable
GitHub Actions runner. The browser loads the actual Lovelace workflow JavaScript
with a fake Home Assistant WebSocket response. It checks:

- 375px mobile navigation from Heating Control to Manage and edit screens
- confirmation review only on disabled schedules and locked Confirm/Save
- weekday inputs and the absence of any enabled edit inputs
- read-only service calls only
- layout overflow at both 320px and 375px, including long schedule names
- unknown schedule state cannot reveal a Delete-review action

**Not a Home Assistant server test.** The fake HA client means the frontend
interaction and rendering are tested, but live Scheduler Component, HA
frontend integration, and hardware behaviour remain unverified. Production
YAML and heater are untouched.
