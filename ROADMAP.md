# Development roadmap

## Baseline
- [x] Create public GitHub repository
- [x] Record approved legacy YAML functionality and non-destructive test policy
- [ ] Import reviewed beta integration code
- [ ] Import final tested legacy YAML as an **unchanged reference snapshot**
- [ ] Add all three approved pop-up dashboard YAML files as reference and adapt for the new integration

## Integration
- [ ] Select a heating `switch.*` via configuration flow
- [ ] Start/stop with timer, switch confirmation and manual-OFF cancellation
- [ ] Scheduler Component add/edit/remove with ownership checks
- [ ] Default schedule state enabled; optionally create disabled
- [ ] Rename and enabled state change in a single edit
- [ ] Protect against duplicate names and ambiguous entity identification
- [ ] Restart behavior, concurrent actions and error reporting tests

## Mobile dashboard
- [ ] One-column Heating Control schedule rows
- [ ] Tap row to load Add/Edit (not enable/disable)
- [ ] Enable/disable control inside edit
- [ ] Manage-only deletion with confirmation and disabled-only guard

## Offline validation and blockers
- [x] GitHub Actions validation, Hassfest, real-library import checks
- [x] Isolated mock tests for ownership, concurrency, ambiguous rename and service denials
- [x] Test failed Scheduler API calls and unavailable schedule-state deletion
- [ ] Confirm Scheduler Component's actual service payload shape, action attribute shape and entity naming across supported versions
- [x] Hard-block schedule mutations pending registration and testing of heating_scheduler.start
- [ ] Implement and validate heating_scheduler.start before considering removal of the write hard gate
- [ ] Test the **initially disabled** schedule-create path for any activation window between add and turn_off; block release until verified
- [ ] Confirm state changes after switch enable/disable, not merely successful service calls
- [ ] Ensure entry ownership is robust for all Scheduler action representations
- [ ] Test a disposable Home Assistant runtime and Scheduler Component end-to-end, **not** the production instance

## Release
- [ ] Python / YAML / JSON CI
- [ ] Home Assistant runtime tests on **separate hardware**
- [ ] Manual GitHub installation documentation (no HACS requirement)
- [ ] Beta release, then v1.0 after testing

**Do not alter the production YAML or schedule entities during development.**
