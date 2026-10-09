# Combined CI safety gate

The Home Assistant import-smoke job now tests setup and unload with a simulated
in-memory HA object using real imported Home Assistant libraries, *and* checks
that all hardware starts/stops and all schedule writes remain denied even when
the configuration entry's write option is manually enabled.

The dependency-light unittest suite also checks both release flags and that
the integration setup module does not import the heating runtime or switch
adapter.

**This is a pre-release guard, not an end-to-end HA runtime test.** The tests
intentionally fail if the release gates are changed. Only relax them alongside
reviewed, isolated HA runtime integration and physical-switch safety testing.

No production Home Assistant config, YAML packages, or schedules are altered.
