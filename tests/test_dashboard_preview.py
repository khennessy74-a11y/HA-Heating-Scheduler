"""Preview-only dashboard contract; no legacy helper coupling."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "dashboard" / "mobile-preview.yaml"


class DashboardPreviewTests(unittest.TestCase):
    def test_mobile_preview_is_valid_lovelace_shape(self):
        doc = yaml.safe_load(PREVIEW.read_text(encoding="utf-8"))
        self.assertIsInstance(doc["views"], list)
        self.assertEqual(len(doc["views"]), 1)
        view = doc["views"][0]
        self.assertEqual(view["path"], "heating-preview")
        self.assertGreaterEqual(len(view["cards"]), 6)
        self.assertTrue(all("type" in card for card in view["cards"]))

    def test_preview_contains_no_action_or_legacy_entity_references(self):
        content = PREVIEW.read_text(encoding="utf-8")
        for forbidden in (
            "perform-action:", "call-service:", "service:",
            "script.heating_", "input_text.", "input_datetime.",
            "switch.heating", "timer.heating_",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)

    def test_approved_mobile_sections_present(self):
        content = PREVIEW.read_text(encoding="utf-8")
        for section in ("Heating Control", "Manage Schedules", "Add / Edit"):
            self.assertIn(section, content)


if __name__ == "__main__":
    unittest.main()
