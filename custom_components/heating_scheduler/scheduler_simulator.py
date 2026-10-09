"""Isolated scheduler lifecycle simulation: never touches a Home Assistant server."""
from __future__ import annotations
from collections.abc import Callable

class SimulatedScheduler:
    def __init__(self):
        self.entities = {}
        self.calls = []
        self.fail = set()
        self.skip_state = set()
        self.next_id = 0

    def snapshot(self):
        return self.entities

    async def call(self, domain, name, data):
        self.calls.append((domain, name, dict(data)))
        key = f"{domain}.{name}"
        if key in self.fail:
            raise RuntimeError(f"Simulated service failure: {key}")
        if key in self.skip_state:
            return
        if domain == "scheduler" and name == "add":
            self.next_id += 1
            eid = f"switch.schedule_sim_{self.next_id}"
            self.entities[eid] = {
                "friendly_name": f"Scheduler {data['name']}",
                "state": "on",
                "actions": list(data["timeslots"][0]["actions"]),
                "timeslots": [data["timeslots"][0]["start"]],
                "weekdays": list(data["weekdays"]),
            }
        elif domain == "scheduler" and name == "edit":
            original = data["entity_id"]
            entity = self.entities[original]
            # Upstream may change entity_id on rename; simulate either case.
            new_name = data.get("name")
            if new_name:
                entity["friendly_name"] = f"Scheduler {new_name}"
                if "rename_id" in self.fail:
                    self.next_id += 1
                    new_id = f"switch.schedule_sim_{self.next_id}"
                    self.entities[new_id] = self.entities.pop(original)
                    original = new_id
            entity["actions"] = list(data["timeslots"][0]["actions"])
            entity["timeslots"] = [data["timeslots"][0]["start"]]
            entity["weekdays"] = list(data["weekdays"])
        elif domain == "scheduler" and name == "remove":
            self.entities.pop(data["entity_id"], None)
        elif domain == "switch" and name in ("turn_on", "turn_off"):
            self.entities[data["entity_id"]]["state"] = (
                "on" if name == "turn_on" else "off"
            )
        else:
            raise AssertionError(f"Unknown fake service: {domain}.{name}")
