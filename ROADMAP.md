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
- [x] Add a non-interactive mobile Lovelace preview and static safety tests
- [x] Define read-only owned schedule list data with unknown-safe UI state fields
- [x] Build a dynamic read-only mobile list presentation contract
- [x] Expose list through a read-only Home Assistant response service
- [x] Implement read-only Lovelace card fetching response-service data
- [x] Run real Chromium mobile UI checks with a fake Home Assistant client
- [ ] Test actual Scheduler Component in a disposable Home Assistant installation
- [ ] Verify structured Scheduler Component timing source before enabling an edit form
- [x] Read-only mobile navigation prototype for Heating Control, Manage and Add/Edit
- [ ] One-column Heating Control schedule rows (final Bubble/Mushroom integration)
- [ ] Tap row to load Add/Edit (not enable/disable)
- [ ] Enable/disable control inside edit
- [ ] Manage-only deletion with confirmation and disabled-only guard

## Offline validation and blockers
- [x] GitHub Actions validation, Hassfest, real-library import checks
- [x] Isolated mock tests for ownership, concurrency, ambiguous rename and service denials
- [x] Test failed Scheduler API calls and unavailable schedule-state deletion
- [x] Check upstream Scheduler add/edit schema and one current version in CI
- [ ] Check older supported Scheduler versions and real schedule identity lifecycle
- [x] Hard-block schedule mutations pending registration and testing of heating_scheduler.start
- [ ] Implement and validate heating_scheduler.start before considering removal of the write hard gate
- [ ] Test the **initially disabled** schedule-create path for any activation window between add and turn_off; block release until verified
- [x] Confirm state changes after switch enable/disable in isolated lifecycle simulation
- [ ] Confirm those states using actual Scheduler Component in disposable HA
- [ ] Ensure entry ownership is robust for all Scheduler action representations
- [ ] Test a disposable Home Assistant runtime and Scheduler Component end-to-end, **not** the production instance

## Release
- [ ] Python / YAML / JSON CI
- [ ] Home Assistant runtime tests on **separate hardware**
- [ ] Manual GitHub installation documentation (no HACS requirement)
- [ ] Beta release, then v1.0 after testing

**Do not alter the production YAML or schedule entities during development.**
