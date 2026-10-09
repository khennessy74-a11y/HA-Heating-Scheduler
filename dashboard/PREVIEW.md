# Mobile dashboard development milestone — safe visual scaffold

`mobile-preview.yaml` contains the approved mobile information architecture:

1. One-column Heating Control, with an enable/disable status shown on the right in the eventual interactive design; tapping the schedule should **edit**, never toggle.
2. Manage Schedules, with pencil edit and deletion only when disabled, after confirmation.
3. Shared Add/Edit form with name, start, duration, seven weekdays and an enabled switch that defaults to ON for newly created schedules.

**This file is an intentionally static Lovelace layout scaffold.**
It uses built-in Markdown and Heading cards, with example schedules and no real entity or service references. It is suitable for source review, **not** as an operational dashboard. The colour and edit affordances in the example are labels, not functioning controls.

The integration does not yet expose a list entity or native form helpers. Its schedule-write and heating-runtime services are still hard-gated. The future interactive dashboard needs a verified data contract and disabled-on-create design before wiring any actions.

Do not install the preview over your existing working Heating Control dashboard.
