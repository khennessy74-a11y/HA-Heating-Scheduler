# Home Assistant library lifecycle smoke test

GitHub CI now executes the integration's real `async_setup`, `async_setup_entry`, and `async_unload_entry` coroutines with imported Home Assistant libraries and an in-memory simulated Home Assistant object.

The test checks that:

- Loading stores only the configured switch entity ID.
- Unloading removes the entry, with no hardware operations.
- Disabled add/edit/remove services remain denied after unload.

**Limitations:** this is not a complete running Home Assistant Core instance, does not verify config-entry forwarding, event-bus subscriptions, physical switch behaviour, or real Scheduler Component service calls. Those require a separately provisioned disposable Home Assistant runtime. Current integration remains pre-release and production-inert.
