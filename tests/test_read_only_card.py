"""Static guarantees for the read-only mobile Lovelace card."""
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "dashboard" / "heating-scheduler-read-only-card.js"


class ReadOnlyCardContract(unittest.TestCase):
    def test_expected_service_only(self):
        js = FILE.read_text()
        self.assertIn('service: "list_schedules"', js)
        self.assertIn("return_response: true", js)
        self.assertIn("textContent", js)

    def test_no_mutating_services(self):
        js = FILE.read_text()
        for forbidden in ('service: "turn_on"', 'service: "turn_off"',
                          'service: "add_schedule"', 'service: "edit_schedule"',
                          'service: "remove_schedule"', 'service: "start"',
                          "innerHTML", "setInterval("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, js)
