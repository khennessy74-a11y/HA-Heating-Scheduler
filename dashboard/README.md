# Dashboard integration status

The approved mobile dashboard from the legacy YAML implementation is **not yet connected** to the GitHub integration. The integration does not create the legacy input helpers and scripts. Do not paste old dashboard YAML into a fresh installation expecting it to work.

**Approved UX baseline:**
- `#heatpop` — single-column cards; tapping a schedule opens the edit form, never toggles the schedule.
- `#manageheat` — single-column management list; pencil edits, bin appears only for disabled schedules with confirmation.
- `#addheat` — shared Add/Edit form, seven weekdays, enabled toggle default ON for new schedules; edit loads current state.

The production legacy scheduler and this development integration must never control the same heating outlet simultaneously.
