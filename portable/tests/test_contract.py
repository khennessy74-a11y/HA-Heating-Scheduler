"""Structural safety contract for the YAML-first portable Heating Scheduler.

This is deliberately a static contract test, NOT a Home Assistant runtime
simulator. It makes no claims about actual switch or timer behaviour.
"""
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(relative):
    return yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))


def find_actions(items, action):
    return [x for x in items if isinstance(x, dict) and x.get("action") == action]


class PortableContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = load("packages/heating_scheduler.yaml")
        cls.heat = load("dashboard/heating-control.yaml")
        cls.form = load("dashboard/add-edit-schedule.yaml")
        cls.manage = load("dashboard/manage-schedules.yaml")
        cls.scripts = cls.backend["script"]

    def test_script_and_popup_inventory(self):
        self.assertEqual(set(self.scripts), {
            "heating_scheduled_run", "heating_cancel_schedule",
            "heating_load_schedule_for_edit", "heating_create_schedule",
            "heating_update_schedule", "heating_delete_schedule",
        })
        self.assertEqual(len(self.backend["automation"]), 4)
        self.assertEqual([x["hash"] for x in (self.heat, self.form, self.manage)],
                         ["#heatpop", "#addheat", "#manageheat"])

    def test_start_session_confirms_on_before_starting_timer(self):
        steps = self.scripts["heating_scheduled_run"]["sequence"]
        self.assertIn("timer.heating_display_timer", steps[0]["value_template"])
        self.assertIn("switch.heating", steps[0]["value_template"])
        index_on = next(i for i, s in enumerate(steps) if s.get("action") == "switch.turn_on")
        index_wait = next(i for i, s in enumerate(steps) if "wait_template" in s)
        index_fail = next(i for i, s in enumerate(steps) if "if" in s)
        index_timer = next(i for i, s in enumerate(steps) if s.get("action") == "timer.start")
        self.assertTrue(index_on < index_wait < index_fail < index_timer)
        fail_actions = steps[index_fail]["then"]
        self.assertTrue(find_actions(fail_actions, "switch.turn_off"))
        self.assertTrue(any("stop" in s for s in fail_actions))

    def test_delete_restricted_to_existing_disabled_heating_schedules(self):
        steps = self.scripts["heating_delete_schedule"]["sequence"]
        expressions = [x["value_template"] for x in steps if x.get("condition") == "template"]
        self.assertTrue(any("script.heating_scheduled_run" in x and "switch.schedule_" in x
                            for x in expressions))
        self.assertTrue(any("is_state(selected_schedule, 'off')" in x for x in expressions))
        self.assertEqual(steps[-1]["action"], "scheduler.remove")

    def test_create_does_not_run_while_editing(self):
        steps = self.scripts["heating_create_schedule"]["sequence"]
        self.assertIn("heating_edit_selected", steps[0]["value_template"])
        self.assertTrue(any(x.get("action") == "scheduler.add" for x in steps))

    def test_update_uses_scheduler_edit_and_duplicate_guard(self):
        steps = self.scripts["heating_update_schedule"]["sequence"]
        assert any("duplicate_name" in str(x) for x in steps)
        choices = [x["choose"] for x in steps if "choose" in x]
        self.assertEqual(len(choices), 1)
        self.assertIn("scheduler.edit", str(choices[0]))
        self.assertFalse(any(x.get("action") == "scheduler.add" for x in steps))

    def test_timer_finished_and_restart_request_off(self):
        automations = {x["id"]: x for x in self.backend["automation"]}
        self.assertTrue(find_actions(automations["heating_scheduler_timer_finished"]["actions"],
                                     "switch.turn_off"))
        restart = automations["heating_scheduler_restart_safety"]["actions"]
        self.assertTrue(find_actions(restart, "switch.turn_off"))
        self.assertTrue(find_actions(restart, "timer.cancel"))
        manual = automations["heating_scheduler_manual_off"]
        self.assertTrue(find_actions(manual["actions"], "timer.cancel"))

    def test_cancel_clears_edit_selection(self):
        steps = self.scripts["heating_cancel_schedule"]["sequence"]
        self.assertTrue(any(x.get("action") == "input_text.set_value"
                            and x.get("target", {}).get("entity_id") == "input_text.heating_edit_selected"
                            and x.get("data", {}).get("value") == ""
                            for x in steps))

    def test_mobile_actions_have_dedicated_grid_rows(self):
        for dashboard, field in ((self.heat, "delete"), (self.manage, "edit")):
            auto = next(x for x in dashboard["cards"] if x["type"] == "custom:auto-entities")
            styles = auto["filter"]["include"][0]["options"]["styles"]
            areas = styles["grid"][0]["grid-template-areas"]
            self.assertIn('"l l"', areas)
            self.assertIn(f'". {field}"', areas)
            self.assertIn({"grid-area": field}, styles["custom_fields"][field])
        manage_card = next(x for x in self.manage["cards"] if x["type"] == "custom:auto-entities")
        self.assertEqual(manage_card["card"]["layout"]["mediaquery"]["(max-width: 600px)"]
                         ["grid-template-columns"], "1fr")

    def test_editor_has_single_save_action_path(self):
        # Every part of the Save button should select Add versus Edit mode.
        stack = next(x for x in self.form["cards"] if x["type"] == "horizontal-stack")
        save = stack["cards"][-1]
        self.assertNotIn("icon_tap_action", save)
        self.assertIn("heating_update_schedule", save["tap_action"])
        self.assertIn("heating_create_schedule", save["tap_action"])

    def test_no_duplicated_timer_helper_in_package(self):
        self.assertNotIn("timer", self.backend)


if __name__ == "__main__":
    unittest.main()
