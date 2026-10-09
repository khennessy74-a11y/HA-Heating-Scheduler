# Controlled Home Assistant installation test

**Development preview — do not connect to production heating.**

**Current testing preference:** do not install this into the existing Home Assistant instance. First pass GitHub Actions Hassfest, isolated mocked tests, and (later) tests against real Home Assistant Python libraries or a disposable instance. This file is reserved for a future, separately approved installation test.


## 1. Before installing

- Confirm the latest GitHub Actions validation passes.
- Back up your Home Assistant configuration.
- Keep the legacy heating package and `switch.heating` unchanged.
- Select a **separate, non-heating** test switch with an ordinary `switch.*` entity.
- Do not configure any heating automation to call `heating_scheduler.*` actions yet.
- This repository contains the GitHub-first custom integration. HACS is **not required** to install it, but Scheduler Component is a separate dependency.

## 2. Manual installation

1. Open GitHub repository **Code → Download ZIP**, and extract it locally.
2. From the ZIP, copy only `custom_components/heating_scheduler` into your Home Assistant `config/custom_components/` folder, so the final path is `config/custom_components/heating_scheduler/manifest.json`. Do not copy the repository root or tests into `custom_components`.
3. Restart Home Assistant.
4. In **Settings → Devices & services → Add integration**, search **Heating Scheduler**.
5. Select **only the separate test switch**, never the production heater.
6. Confirm the integration entry appears and Home Assistant has no related setup errors.

## 3. Read-only/disabled-service checks

- Verify the integration loads and the selected test switch remains unchanged.
- Verify the `heating_scheduler.add_schedule`, `edit_schedule`, and `remove_schedule` actions appear in Home Assistant's actions developer tool (names may be displayed in a translated format).
- The config entry does not expose an opt-in control yet: `enable_schedule_writes` is **not set** and the actions must reject execution. **Do not manually set this option.**
- Do **not** expect `heating_scheduler.start` or `heating_scheduler.stop`: heating runtime controls are not registered.
- Do **not** run schedule writes against actual schedules or use the existing `switch.heating` target.

## 4. Report results

Record:
- Home Assistant version.
- Whether **Heating Scheduler** appeared in Add integration.
- Whether the test switch was selectable.
- Whether the integration successfully configured.
- Whether the three schedule-management actions appeared.
- Any **Settings → System → Logs** errors mentioning `heating_scheduler`.

## Limits of this test

GitHub Actions checks source syntax and mocked unit tests, **not** compatibility with a real Home Assistant installation. A green build does not mean the integration is production ready. No live heating operation or Scheduler Component schedule mutation should be attempted in this phase.
