# State-change event integration milestone

The disposable Home Assistant test job now exercises an actual Home Assistant
state event using a listener attached **explicitly from the test**.

- Detects ON-to-OFF for a disposable switch, routing to an injected recorder.
- Ignores repeated OFF events.
- Cleanup unsubscribes, and repeated cleanup is safe.
- Explicitly rejects the known production heater entity `switch.heating`.
- No listener is registered from integration setup, and no physical switch
  service is invoked.

This is not production ready: a different physical switch could still be given
to this test helper, so **never attach it outside the test runner**. Before
connecting a production listener, validate ownership, controller-initiated OFF
versus manual OFF, restart recovery and error handling against a disposable
running Home Assistant server.
