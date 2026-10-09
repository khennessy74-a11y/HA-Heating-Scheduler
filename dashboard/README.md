# Dashboard integration status

The approved mobile dashboard from the legacy YAML implementation is **not yet connected** to the GitHub integration. The integration does not create the legacy input helpers and scripts. Do not paste old dashboard YAML into a fresh installation expecting it to work.

## Lovelace prerequisites for the planned dashboard

- [Bubble Card](https://github.com/Clooos/Bubble-Card) — popups
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) — controls
- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) — automatic schedule lists
- [Button Card](https://github.com/custom-cards/button-card) — interactive schedule rows
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) — styling
- Custom text-input card: confirm its exact repository from the final form configuration before release

[Scheduler Component](https://github.com/nielsfaber/scheduler-component) is a separate backend requirement. Custom Lovelace cards are not needed for backend-only testing. Verify the final dashboard YAML before treating this as a definitive install list.

**Approved UX baseline:**
- `#heatpop` — single-column cards; tapping a schedule opens the edit form, never toggles the schedule.
- `#manageheat` — single-column management list; pencil edits, bin appears only for disabled schedules with confirmation.
- `#addheat` — shared Add/Edit form, seven weekdays, enabled toggle default ON for new schedules; edit loads current state.

The production legacy scheduler and this development integration must never control the same heating outlet simultaneously.
