"""Static release blockers for the preview integration.

These structural checks intentionally require an explicit code review before
the release gates or hardware connections can be enabled.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"


class ReleaseGateTests(unittest.TestCase):
    def test_both_hardware_and_scheduler_release_flags_off(self):
        for filename, flag in (
            ("runtime.py", "HEATING_RUNTIME_RELEASED"),
            ("service_registration.py", "SCHEDULE_MUTATIONS_RELEASED"),
        ):
            with self.subTest(filename=filename):
                source = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
                found = [
                    node.value for node in source.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == flag
                            for t in node.targets)
                ]
                self.assertEqual(len(found), 1)
                self.assertIsInstance(found[0], ast.Constant)
                self.assertIs(found[0].value, False)

    def test_integration_setup_does_not_import_hardware_runtime(self):
        source = ast.parse((ROOT / "__init__.py").read_text(encoding="utf-8"))
        imports = [
            node.module for node in ast.walk(source)
            if isinstance(node, ast.ImportFrom)
        ]
        self.assertNotIn("runtime", imports)
        self.assertNotIn("ha_switch", imports)
        self.assertNotIn("scheduler_bridge", imports)

    def test_no_heating_start_or_stop_services_registered(self):
        source = (ROOT / "service_registration.py").read_text(encoding="utf-8")
        self.assertNotIn('"start": vol.Schema', source)
        self.assertNotIn('"stop": vol.Schema', source)


if __name__ == "__main__":
    unittest.main()
