# Batch 2 — Scheduler Component lifecycle and compatibility

This milestone bundles the upstream schema contract and an isolated lifecycle
simulator covering create, edit, rename, switch state, ownership, disabled-state
deletion, error propagation, and concurrent creates.

The bridge **waits for confirmation** that `switch.schedule_*` reflects its
requested ON/OFF state and that removed schedules actually disappear. A service
call returning successfully is not enough to claim success. Failed confirmation
leads to an explicit error, not a retry that could duplicate schedules.

Safety restrictions remain:
- `SCHEDULE_MUTATIONS_RELEASED=False`
- `HEATING_RUNTIME_RELEASED=False`
- creating a disabled schedule remains rejected, because upstream add
  initially enables the schedule and does not expose an atomic disabled option
- the `heating_scheduler.start` action is not available in production
- the simulator and upstream-schema CI do not install or invoke actual Scheduler
  Component services

**Not yet a complete operational integration.** We still require isolated
Home Assistant + actual Scheduler Component end-to-end testing and an atomic
disabled-on-create solution, or a documented feature restriction accepted for
beta. No live Home Assistant heater or existing YAML is altered.
