"""Static safety contract for read-only mobile workflow prototype."""
from pathlib import Path
import unittest

CARD = Path(__file__).resolve().parents[1] / "dashboard" / "heating-scheduler-workflow-preview.js"


class PreviewTests(unittest.TestCase):
    def test_navigation_views_and_fields(self):
        content = CARD.read_text()
        for field in ("Heating Control", "Manage Schedules", "Add Schedule", "Edit Schedule",
                      "Schedule name", "Start time", "Duration", "Weekdays", "Enabled"):
            self.assertIn(field, content)
        self.assertIn("return_response: true", content)
        self.assertIn('service: "list_schedules"', content)

    def test_form_and_delete_are_disabled(self):
        content = CARD.read_text()
        self.assertIn("input.disabled = true", content)
        self.assertIn('"Save — unavailable", () => {}, true', content)
        self.assertIn('"Delete (disabled)", () => {}, true', content)

    def test_no_mutating_calls_or_unsafe_dom(self):
        content = CARD.read_text()
        for forbidden in ("innerHTML", "insertAdjacentHTML", 'service: "turn_on"',
                          'service: "turn_off"', 'service: "start"',
                          'service: "edit_schedule"', 'service: "add_schedule"',
                          'service: "remove_schedule"'):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)

    def test_weekday_duration_time_and_enabled_controls_are_disabled(self):
        content = CARD.read_text()
        for expected in (
            'time.type = "time"', 'duration = this._node("select")',
            'weekdaySection.disabled = true', 'checkbox.disabled = true',
            'toggle.disabled = true', 'toggle.checked = selected ? selected.enabled === true : true',
            '["mon", "Mon"]', '["sun", "Sun"]',
            'durations = [15, 30, 45, 60, 90, 120, 180, 240]',
            'time.value = selected?.start || ""',
        ):
            self.assertIn(expected, content)
