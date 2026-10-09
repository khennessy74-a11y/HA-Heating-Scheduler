# Disposable Home Assistant runtime verification

The `homeassistant-runtime` GitHub Actions job installs
`pytest-homeassistant-custom-component` and runs a real in-memory Home
Assistant test fixture against the integration's setup, service registration
and unload functions. It uses the fake entity `switch.disposable_test` and
never calls heating hardware. The existing offline tests remain separate and
run quickly.

## Pass criteria

- Setup registers the three write-service endpoints.
- All three remain denied by the hard release gate even with a manual opt-in.
- The dummy switch remains OFF.
- Unload removes integration storage without touching the dummy switch.

This is a **first HA runtime smoke test**, not a full Scheduler Component
installation. Runtime switch tracking, restart recovery and schedule service
compatibility remain explicitly out of scope. Only CI runners are used; the
user's Home Assistant installation and legacy YAML are untouched.
