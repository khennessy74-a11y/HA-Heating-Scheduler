"""Offline structural checks for test-only Home Assistant listener."""
import ast
from pathlib import Path
import unittest

COMP = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler"


class ListenerStructureTests(unittest.TestCase):
    def test_listener_never_imported_by_integration_setup(self):
        init = ast.parse((COMP / "__init__.py").read_text())
        names = [
            n.module for n in ast.walk(init) if isinstance(n, ast.ImportFrom)
        ]
        self.assertNotIn("ha_state_listener", names)
        self.assertNotIn("runtime_events", names)

    def test_listener_is_explicit_only(self):
        source = (COMP / "ha_state_listener.py").read_text()
        self.assertIn("def attach_test_state_listener(", source)
        self.assertIn("return cleanup", source)


if __name__ == "__main__":
    unittest.main()
