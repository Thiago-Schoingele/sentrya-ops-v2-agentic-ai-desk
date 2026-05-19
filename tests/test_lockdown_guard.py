import tempfile
import unittest
from pathlib import Path

from src.lockdown_guard import (
    build_lockdown_block_response,
    enforce_lockdown_or_none,
    is_agent_execution_allowed,
)
from src.security_state import SecurityStateManager, SecuritySystemState


class TestLockdownGuard(unittest.TestCase):
    def create_manager(self) -> SecurityStateManager:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        base = Path(temp_dir.name)

        return SecurityStateManager(
            state_file=base / "security_state.json",
            events_file=base / "security_events.jsonl",
        )

    def test_01_allows_agent_execution_in_normal_state(self):
        manager = self.create_manager()

        self.assertEqual(manager.state.current_state, SecuritySystemState.NORMAL.value)
        self.assertTrue(is_agent_execution_allowed(manager=manager))

    def test_02_blocks_agent_execution_in_lockdown(self):
        manager = self.create_manager()
        manager.activate_lockdown("Security incident.")

        self.assertFalse(is_agent_execution_allowed(manager=manager))

    def test_03_enforce_lockdown_returns_response_when_blocked(self):
        manager = self.create_manager()
        manager.activate_lockdown("Security incident.")

        response = enforce_lockdown_or_none(manager=manager)

        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["intent"], "system_lockdown")
        self.assertEqual(response["selected_route"], "security")
        self.assertEqual(response["model_used"], "security_state_manager")
        self.assertTrue(response["requires_human_review"])

    def test_04_enforce_lockdown_returns_none_when_normal(self):
        manager = self.create_manager()

        response = enforce_lockdown_or_none(manager=manager)

        self.assertIsNone(response)

    def test_05_blocks_staff_active_state(self):
        manager = self.create_manager()
        manager.activate_staff("STAFF active.")

        self.assertFalse(is_agent_execution_allowed(manager=manager))

    def test_06_allows_released_monitoring_state(self):
        manager = self.create_manager()
        manager.activate_lockdown("Security incident.")
        manager.force_release(operator_authenticated=True)

        self.assertEqual(manager.state.current_state, SecuritySystemState.RELEASED_MONITORING.value)
        self.assertTrue(is_agent_execution_allowed(manager=manager))

    def test_07_lockdown_response_does_not_expose_raw_payload(self):
        response = build_lockdown_block_response(
            snapshot={
                "system": {
                    "security_state": "LOCKDOWN",
                    "lockdown_active": True,
                    "staff_active": False,
                },
                "incident": {
                    "last_event_type": "input_blocked",
                    "last_event_severity": "HIGH",
                },
                "recovery": {
                    "can_release_after_validation": False,
                },
            }
        )

        serialized = str(response)

        self.assertNotIn("DROP TABLE", serialized)
        self.assertNotIn("gsk_", serialized)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", serialized)


if __name__ == "__main__":
    unittest.main()