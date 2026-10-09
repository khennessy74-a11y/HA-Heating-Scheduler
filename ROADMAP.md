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

## Release
- [ ] Python / YAML / JSON CI
- [ ] Home Assistant runtime tests on **separate hardware**
- [ ] Manual GitHub installation documentation (no HACS requirement)
- [ ] Beta release, then v1.0 after testing

**Do not alter the production YAML or schedule entities during development.**
