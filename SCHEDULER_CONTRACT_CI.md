# Upstream Scheduler Component compatibility milestone

The new `scheduler-upstream` GitHub Actions job clones the current public
Scheduler Component source into a disposable runner and loads its real
`custom_components/scheduler/const.py` Voluptuous schemas. Our bridge's
captured add/edit payloads are validated against those exact schemas.

Tests also assert:
- `heating_scheduler.start` action carries the expected entry ID and duration
- no guessed schedule entity ID when add has no matching new switch
- disabled-on-create is rejected **before** calling the Scheduler API
- enabled-schedule deletion is rejected **before** calling the Scheduler API

This tests source/schema compatibility only. It does **not** instantiate
Scheduler Component, register heating start actions or create schedules in HA.
The test fails if a future upstream change breaks our assumptions.

Remaining for an operational beta: isolated true Scheduler Component
integration, verified state transitions, safe disabled-first creation,
heating runtime service and recovery, and frontend wiring. Both hard release
flags remain false in the integration.
