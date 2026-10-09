# Disposable HA lifecycle test coverage

The runtime test job now checks more than one setup/unload call:

- An entry is set up and unloaded three times, with services still fail-closed.
- Manually opting into writes cannot enable schedule mutation.
- Two loaded entries remain isolated during unload.
- Simulated switch entities stay OFF without service calls to physical devices.

These tests execute Home Assistant's test fixture, **not** a production HA server.
They do not prove restart recovery or Scheduler Component compatibility with
real schedules. Hardware release flags remain disabled.
