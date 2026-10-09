# Mobile interface regression milestone

The dashboard JavaScript runtime test suite now verifies responses with missing
read-only guarantees, empty schedule lists, navigation into the disabled edit
form, and config-entry switches during an outstanding asynchronous response.

A config entry switch invalidates any stale response. The mobile preview keeps
all input controls disabled and never invokes a schedule or heater write
service. These tests use a lightweight DOM model and do not yet prove mobile
browser layout or Home Assistant frontend compatibility.
