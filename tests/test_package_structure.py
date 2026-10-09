"""Dependency-light checks for GitHub package structure."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "custom_components" / "heating_scheduler"


class PackageStructureTests(unittest.TestCase):
    def test_manifest_and_core_files(self):
        manifest = json.loads((COMP / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["domain"], "heating_scheduler")
        self.assertTrue(manifest["config_flow"])
        for name in ("__init__.py", "config_flow.py", "const.py", "services.yaml"):
            with self.subTest(name=name):
                self.assertTrue((COMP / name).is_file())


if __name__ == "__main__":
    unittest.main()
