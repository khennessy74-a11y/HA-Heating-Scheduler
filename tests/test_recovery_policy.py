"""Pure lifecycle recovery policy tests; no HA and no real switches."""
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler" / "recovery_policy.py"
spec = importlib.util.spec_from_file_location("recovery_policy_isolated", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RecoveryTests(unittest.TestCase):
    def test_no_automatic_heating_resume_on_startup(self):
        for state in ("on", "off", "unavailable", "unknown", None):
            with self.subTest(state=state):
                result = module.on_startup(
                    observed_state=state, persisted_session=True,
                )
                self.assertEqual(result.action, module.RecoveryAction.REVIEW_REQUIRED)

    def test_no_automatic_action_if_switch_observed_on(self):
        decision = module.on_startup(
            observed_state="on", persisted_session=False
        )
        self.assertEqual(decision.action, module.RecoveryAction.REVIEW_REQUIRED)

    def test_idle_off_startup_never_toggles_switch(self):
        result = module.on_startup(
            observed_state="off", persisted_session=False
        )
        self.assertEqual(result.action, module.RecoveryAction.LEAVE_OFF)

    def test_active_unload_always_blocked(self):
        for state in ("on", "off", "unavailable", None):
            with self.subTest(state=state):
                result = module.on_unload(
                    active_session=True, observed_state=state
                )
                self.assertEqual(result.action, module.RecoveryAction.BLOCK_UNLOAD)

    def test_idle_unload_only_accepts_observed_off(self):
        result = module.on_unload(active_session=False, observed_state="off")
        self.assertEqual(result.action, module.RecoveryAction.LEAVE_OFF)
        for state in ("on", "unavailable", "unknown", None):
            with self.subTest(state=state):
                result = module.on_unload(
                    active_session=False, observed_state=state,
                )
                self.assertEqual(result.action, module.RecoveryAction.REVIEW_REQUIRED)


if __name__ == "__main__":
    unittest.main()
