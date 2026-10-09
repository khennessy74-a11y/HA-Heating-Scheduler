# Restart and reload decision model

This batch defines a *pure policy*, **not** a working Home Assistant restart handler.

- Restart never restores a timer or switches heating ON automatically.
- A persisted session marker is treated as requiring human or dedicated runtime reconciliation; it is not authorization to resume.
- Active-session unload is blocked in the policy model, not yet enforced in `async_unload_entry`.
- Unknown, unavailable or ON observed state requires review rather than an automatic OFF that might interfere with another heating controller.
- No persistent session storage is implemented. Actual restart recovery is a release blocker.

### Remaining integration work

Bind the policy to Home Assistant startup, shutdown and unload semantics in a disposable instance; verify behaviour for power loss, stale persisted markers, failed service calls and external/manual changes. Define explicitly whether turning OFF on shutdown is permitted and how to avoid leaving a heater ON when the process crashes. Keep the controller release and schedule-mutation gates closed in production until then.

## CI timing regression (2026-10-09)

A controller test unintentionally used the production-duration sleep and stalled the offline test suite until the 10-minute job timeout. The test now injects an immediate fake sleep and has an explicit short wait timeout. The CI unittest step has a 120-second cap to surface future blocked tests promptly.
