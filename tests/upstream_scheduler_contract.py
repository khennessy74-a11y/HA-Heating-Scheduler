"""Fail-closed upstream contract verification: NO live HA services called.

Usage: python tests/upstream_scheduler_contract.py /tmp/scheduler-component/custom_components/scheduler/const.py
"""
from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys

import voluptuous as vol

# Running this file as a script places tests/ first on sys.path, not repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.heating_scheduler.scheduler_bridge import (
    ScheduleError,
    SchedulerBridge,
    schedule_action,
)

assert len(sys.argv) == 2, "Provide the cloned Scheduler Component const.py path"
source = Path(sys.argv[1])
assert source.name == "const.py" and source.exists()
spec = importlib.util.spec_from_file_location("scheduler_upstream_schema_contract", source)
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)


async def validate_schema_payloads():
    """Capture service calls without ever executing an actual integration."""
    calls = []
    owned = {}

    async def record(domain, name, payload):
        calls.append((domain, name, payload))
        if (domain, name) == ("scheduler", "add"):
            upstream.ADD_SCHEDULE_SCHEMA(payload)
            # The real scheduler would create a switch; deliberately do NOT
            # simulate one, so resolve_new fails closed without assuming IDs.
        elif (domain, name) == ("scheduler", "edit"):
            upstream.EDIT_SCHEDULE_SCHEMA({
                key: val for key, val in payload.items() if key != "entity_id"
            })
        elif domain == "switch":
            assert name in ("turn_on", "turn_off")

    bridge = SchedulerBridge(record, lambda: owned)
    try:
        await bridge.add(
            entry_id="isolated_contract", name="Morning",
            start="06:30", weekdays=["mon", "wed"], minutes=60,
            enabled=True,
        )
    except ScheduleError as err:
        assert "cannot be identified" in str(err), str(err)
    else:
        raise AssertionError("No entity was created; add must fail closed")
    assert len(calls) == 1 and calls[0][:2] == ("scheduler", "add")
    action = calls[0][2]["timeslots"][0]["actions"][0]
    assert upstream.ACTION_SCHEMA(action)["service"] == "heating_scheduler.start"
    assert action["service_data"] == {"entry_id": "isolated_contract", "minutes": 60}

    # Scheduler Component lacks an enabled property in add schema. A create
    # disabled request must fail *before* touching any upstream service.
    before = len(calls)
    try:
        await bridge.add(
            entry_id="isolated_contract", name="Disabled",
            start="07:00", weekdays=["sun"], minutes=15,
            enabled=False,
        )
    except ScheduleError as err:
        assert "Creating disabled schedules" in str(err)
    else:
        raise AssertionError("Unsafe initially-disabled creation accepted")
    assert len(calls) == before, "Disabled request unexpectedly made a service call"

    owned["switch.schedule_morning"] = {
        "friendly_name": "Scheduler Morning",
        "state": "off",
        "actions": [schedule_action("isolated_contract", 60)],
        "timeslots": ["06:30"],
        "weekdays": ["mon", "wed"],
    }
    # Edit, with unchanged name, must pass upstream's edit payload schema.
    # New fake snapshot remains unchanged and the method can resolve.
    resolved = await bridge.edit(
        entry_id="isolated_contract", entity_id="switch.schedule_morning",
        name="Morning", start="07:30", weekdays=["tue"], minutes=90,
        enabled=False,
    )
    assert resolved == "switch.schedule_morning"
    edit = next(p for d, n, p in calls if (d, n) == ("scheduler", "edit"))
    assert edit["entity_id"] == "switch.schedule_morning"
    assert upstream.EDIT_SCHEDULE_SCHEMA({
        k: v for k, v in edit.items() if k != "entity_id"
    })["timeslots"][0]["start"] == "07:30"

    # Deletion of enabled schedules must be denied before invoking scheduler.
    owned["switch.schedule_morning"]["state"] = "on"
    before = len(calls)
    try:
        await bridge.remove(
            entry_id="isolated_contract", entity_id="switch.schedule_morning"
        )
    except ScheduleError as err:
        assert "Disable schedule" in str(err)
    else:
        raise AssertionError("Enabled deletion was accepted")
    assert len(calls) == before
    print("PASS: upstream add/edit schemas, ownership, disabled-create and delete gates")
    print("PASS: all upstream service calls captured in memory; no HA server used")


asyncio.run(validate_schema_payloads())
