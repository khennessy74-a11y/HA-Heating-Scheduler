"""In-memory execution tests for the portable YAML session sequence.

Exercises actual Jinja templates and YAML action ordering against fake switch,
timer and service states. Not a substitute for Home Assistant runtime testing.
No physical switch, network connection or HA instance is used.
"""
from __future__ import annotations

import pathlib
import unittest

import jinja2
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = yaml.safe_load((ROOT / "packages/heating_scheduler.yaml").read_text())


class Stopped(Exception):
    pass


class FakeHeating:
    def __init__(self, confirms_on=True, initial_switch="off", initial_timer="idle"):
        self.switch = initial_switch
        self.timer = initial_timer
        self.confirms_on = confirms_on
        self.calls = []
        self.env = jinja2.Environment()
        self.env.filters["int"] = lambda value, default=0: int(value or default)
        self.env.globals.update(
            is_state=self.is_state,
            states=self.states,
        )
        self.vars = {}

    def is_state(self, entity, value):
        return self.states(entity) == value

    def states(self, entity):
        if entity == "switch.heating":
            return self.switch
        if entity == "timer.heating_display_timer":
            return self.timer
        return "unknown"

    def render(self, template):
        if not isinstance(template, str) or "{{" not in template and "{%" not in template:
            return template
        return self.env.from_string(template).render(**self.vars).strip()

    def evaluate(self, expression):
        return self.render("{{ " + expression + " }}") in ("True", "true", "1")

    def execute(self, steps):
        for step in steps:
            if "condition" in step:
                value = self.render(step["value_template"])
                if value not in ("True", "true", "1"):
                    raise Stopped("Condition false")
            elif "variables" in step:
                self.vars.update({k: self.render(v) for k, v in step["variables"].items()})
            elif "wait_template" in step:
                complete = self.render(step["wait_template"]) in ("True", "true", "1")
                self.vars["wait"] = {"completed": complete}
                # HA wait.completed uses property syntax; simulation uses a simple proxy.
                self.vars["wait"] = type("Wait", (), {"completed": complete})()
            elif "if" in step:
                cond = step["if"][0]
                expr = cond.get("value_template", "")
                if self.render(expr) in ("True", "true", "1"):
                    self.execute(step.get("then", []))
                else:
                    self.execute(step.get("else", []))
            elif "stop" in step:
                raise Stopped(step["stop"])
            elif "action" in step:
                action = step["action"]
                payload = step.get("data", {})
                self.calls.append(action)
                if action == "switch.turn_on":
                    if self.confirms_on:
                        self.switch = "on"
                elif action == "switch.turn_off":
                    self.switch = "off"
                elif action == "timer.start":
                    self.timer = "active"
                    self.duration = self.render(payload.get("duration"))
                elif action == "timer.cancel":
                    self.timer = "idle"
                else:
                    raise AssertionError("Unexpected action: " + action)
            else:
                raise AssertionError("Unsupported session step: " + str(step))

    def start(self, minutes):
        self.vars["minutes"] = minutes
        try:
            self.execute(PACKAGE["script"]["heating_scheduled_run"]["sequence"])
        except Stopped:
            return False
        return True


class PortableExecutionTests(unittest.TestCase):
    def test_confirmed_on_starts_timer(self):
        fake = FakeHeating()
        self.assertTrue(fake.start(15))
        self.assertEqual(fake.calls, ["switch.turn_on", "timer.start"])
        self.assertEqual(fake.duration, "00:15:00")
        self.assertEqual(fake.timer, "active")

    def test_one_hour_formats_as_full_hour(self):
        fake = FakeHeating()
        self.assertTrue(fake.start(60))
        self.assertEqual(fake.duration, "01:00:00")

    def test_no_confirmation_cannot_start_timer(self):
        fake = FakeHeating(confirms_on=False)
        self.assertFalse(fake.start(15))
        self.assertIn("switch.turn_off", fake.calls)
        self.assertNotIn("timer.start", fake.calls)
        self.assertEqual(fake.switch, "off")

    def test_session_already_active_does_not_restart(self):
        for switch, timer in (("on", "idle"), ("off", "active")):
            with self.subTest(switch=switch, timer=timer):
                fake = FakeHeating(initial_switch=switch, initial_timer=timer)
                self.assertFalse(fake.start(15))
                self.assertEqual(fake.calls, [])

    def test_invalid_duration_does_not_operate_switch(self):
        for duration in (0, -1, 241, "not-a-number"):
            with self.subTest(minutes=duration):
                fake = FakeHeating()
                self.assertFalse(fake.start(duration))
                self.assertEqual(fake.calls, [])

    def test_timer_finished_requests_off(self):
        fake = FakeHeating(initial_switch="on", initial_timer="active")
        automation = next(x for x in PACKAGE["automation"]
                          if x["id"] == "heating_scheduler_timer_finished")
        fake.execute(automation["actions"])
        self.assertEqual(fake.calls, ["switch.turn_off"])
        self.assertEqual(fake.switch, "off")

    def test_restart_requests_off_and_cancels_timer(self):
        fake = FakeHeating(initial_switch="on", initial_timer="active")
        automation = next(x for x in PACKAGE["automation"]
                          if x["id"] == "heating_scheduler_restart_safety")
        fake.execute(automation["actions"])
        self.assertEqual(fake.calls, ["switch.turn_off", "timer.cancel"])
        self.assertEqual((fake.switch, fake.timer), ("off", "idle"))


if __name__ == "__main__":
    unittest.main()
