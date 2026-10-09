"""Unit tests for the isolated session policy without Home Assistant installed."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "custom_components" / "heating_scheduler" / "session.py"
spec = importlib.util.spec_from_file_location("heating_scheduler_session_policy", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

SessionDecision = module.SessionDecision
evaluate_start = module.evaluate_start
make_request = module.make_request


class SessionPolicyTests(unittest.TestCase):
    def test_valid_minutes(self):
        for minutes in (1, 15, 60, 240):
            with self.subTest(minutes=minutes):
                request = make_request(minutes, timer_active=False, switch_off=True)
                self.assertEqual(request.seconds, minutes * 60)

    def test_bad_duration(self):
        for value in (0, -1, 241, "60", None, True, 12.5):
            with self.subTest(value=value):
                self.assertEqual(
                    evaluate_start(value, timer_active=False, switch_off=True),
                    SessionDecision.INVALID_DURATION,
                )

    def test_active_session_rejected(self):
        self.assertEqual(
            evaluate_start(30, timer_active=True, switch_off=True),
            SessionDecision.ALREADY_RUNNING,
        )

    def test_on_switch_rejected(self):
        self.assertEqual(
            evaluate_start(30, timer_active=False, switch_off=False),
            SessionDecision.SWITCH_NOT_OFF,
        )

    def test_no_control_side_effect(self):
        with self.assertRaises(ValueError):
            make_request(30, timer_active=True, switch_off=True)


if __name__ == "__main__":
    unittest.main()
