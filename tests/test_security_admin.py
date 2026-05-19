import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from src.security_admin import (
    execute_security_admin_command,
    format_security_admin_result_for_telegram,
    is_known_admin_command,
    is_read_only_command,
    is_state_changing_command,
    normalize_admin_command,
)
from src.security_state import (
    SecurityStateManager,
    SecuritySystemState,
    to_iso_utc,
    utc_now,
)


class TestSecurityAdminCommandLayer(unittest.TestCase):
    def create_manager(self) -> SecurityStateManager:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        base = Path(temp_dir.name)

        return SecurityStateManager(
            state_file=base / "security_state.json",
            events_file=base / "security_events.jsonl",
            recovery_validation_minutes=60,
            released_monitoring_hours=24,
        )

    def test_01_normalize_admin_command(self):
        self.assertEqual(normalize_admin_command("/status"), "status")
        self.assertEqual(normalize_admin_command(" FORCE_RELEASE "), "force_release")

    def test_02_command_classification(self):
        self.assertTrue(is_known_admin_command("status"))
        self.assertTrue(is_read_only_command("status"))
        self.assertTrue(is_state_changing_command("force_release"))
        self.assertFalse(is_known_admin_command("delete_everything"))

    def test_03_status_does_not_require_operator_auth(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="status",
            manager=manager,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["command"], "status")
        self.assertFalse(result["requires_operator_auth"])
        self.assertEqual(result["snapshot"]["system"]["security_state"], SecuritySystemState.NORMAL.value)

    def test_04_state_changing_command_requires_auth(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=False,
        )

        self.assertEqual(result["status"], "denied")
        self.assertTrue(result["requires_operator_auth"])
        self.assertEqual(result["public_error"], "operator_auth_required")
        self.assertEqual(manager.state.current_state, SecuritySystemState.NORMAL.value)

    def test_05_activate_lockdown_with_auth(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=True,
            reason="Manual test lockdown.",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.LOCKDOWN.value)
        self.assertTrue(manager.state.lockdown_active)

    def test_06_activate_staff_with_auth(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="activate_staff",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.STAFF_ACTIVE.value)
        self.assertTrue(manager.state.staff_active)

    def test_07_request_and_start_recovery_with_auth(self):
        manager = self.create_manager()

        execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=True,
        )
        execute_security_admin_command(
            command="activate_staff",
            manager=manager,
            operator_authenticated=True,
        )

        recovery_result = execute_security_admin_command(
            command="request_recovery",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(recovery_result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.RECOVERY_PENDING.value)

        validation_result = execute_security_admin_command(
            command="start_recovery_validation",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(validation_result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.RECOVERY_VALIDATION.value)

    def test_08_release_after_validation_before_window_returns_error(self):
        manager = self.create_manager()

        execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=True,
        )
        execute_security_admin_command(
            command="activate_staff",
            manager=manager,
            operator_authenticated=True,
        )
        execute_security_admin_command(
            command="request_recovery",
            manager=manager,
            operator_authenticated=True,
        )
        execute_security_admin_command(
            command="start_recovery_validation",
            manager=manager,
            operator_authenticated=True,
        )

        result = execute_security_admin_command(
            command="release_after_validation",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["public_error"], "admin_command_failed")
        self.assertEqual(manager.state.current_state, SecuritySystemState.RECOVERY_VALIDATION.value)

    def test_09_force_release_with_auth(self):
        manager = self.create_manager()

        execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=True,
        )

        result = execute_security_admin_command(
            command="force_release",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.RELEASED_MONITORING.value)
        self.assertFalse(manager.state.lockdown_active)

    def test_10_complete_monitoring_after_expired_window(self):
        manager = self.create_manager()

        execute_security_admin_command(
            command="activate_lockdown",
            manager=manager,
            operator_authenticated=True,
        )
        execute_security_admin_command(
            command="force_release",
            manager=manager,
            operator_authenticated=True,
        )

        manager.state.released_monitoring_until_utc = to_iso_utc(utc_now() - timedelta(minutes=1))
        manager.save_state()

        result = execute_security_admin_command(
            command="complete_monitoring",
            manager=manager,
            operator_authenticated=True,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(manager.state.current_state, SecuritySystemState.NORMAL.value)

    def test_11_unknown_command_returns_safe_error(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="delete_everything",
            manager=manager,
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["public_error"], "unknown_admin_command")

    def test_12_telegram_formatter_does_not_expose_secrets(self):
        manager = self.create_manager()

        result = execute_security_admin_command(
            command="status",
            manager=manager,
        )

        formatted = format_security_admin_result_for_telegram(result)

        self.assertIn("Sentrya Ops V2 — Security Admin", formatted)
        self.assertNotIn("gsk_", formatted)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", formatted)
        self.assertNotIn("PASSWORD_HASH", formatted)
        self.assertNotIn("PASSWORD_SALT", formatted)


if __name__ == "__main__":
    unittest.main()