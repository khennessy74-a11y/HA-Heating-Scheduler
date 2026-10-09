# Mobile UI specification — approved legacy behaviour

1. **Heating Control:** one schedule per row, left timer icon, title and duration/weekday line, right-aligned green **Enabled** / grey **Disabled**. Tap the row to **edit**. No delete or pencil here.
2. **Manage Schedules:** one schedule per row, same information, edit pencil on right, deletion bin shown only when schedule is disabled.
3. **Add/Edit:** one shared Bubble Card popup with schedule name, start time, duration, weekdays and enabled toggle.
4. **Enabled state:** ON by default for new schedules. On edit, reflect the existing schedule state. Save both name and state changes.
5. **Safety:** no single-tap schedule enable/disable in Heating Control. Delete must confirm and the backend must refuse enabled-schedule deletion.
6. **Portability:** replace hardcoded legacy helpers and scripts with integration-native services and entities before release.

These are requirements, NOT a currently working integration-native dashboard.
