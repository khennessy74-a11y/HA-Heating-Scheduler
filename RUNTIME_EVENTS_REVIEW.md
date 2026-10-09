# Runtime state monitoring — offline preparation

The `runtime_events.py` router is a pure, isolated preparation module.

- Detects only `on → off` changes for one uniquely configured `switch.*`.
- Ignores other switches and `unknown` / `unavailable` transitions.
- Refuses ambiguous mappings where multiple configuration entries claim the same switch.
- Fails closed if a running session is passively unloaded without a validated shutdown procedure.

## Still blocked

This is **not** a live Home Assistant listener. A future implementation must differentiate user/manual OFF from the controller's own requested OFF; otherwise state callbacks could race with timer expiry. Restart recovery also needs a persisted session policy, error handling and disposable runtime testing. Do not enable any heating service or schedule mutations yet.

No changes to legacy production YAML, switches or integrations are required.
