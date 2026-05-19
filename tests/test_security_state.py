import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from src.security_state import (
    SecurityEventType,
    SecuritySeverity,
    SecurityStateManager,
    SecuritySystemState,
    to_iso_utc,
    utc_now,
)


class TestSecurityStateManager(unittest.TestCase):
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

    def test_01_default_state_is_normal(self):
        manager = self.create_manager()

        self.assertEqual(manager.state.current_state, SecuritySystemState.NORMAL.value)
        self.assertFalse(manager.state.lockdown_active)
        self.assertFalse(manager.state.staff_active)

    def test_02_medium_event_moves_normal_to_watch(self):
        manager = self.create_manager()

        event = manager.create_event(
            event_type=SecurityEventType.INPUT_BLOCKED,
            severity=SecuritySeverity.MEDIUM,
            source="telegram",
            message="Suspicious but non-critical event.",
            actor_id="telegram:123",
            public_reason="medium_risk_input",
        )

        manager.record_event(event)

        self.assertEqual(manager.state.current_state, SecuritySystemState.WATCH.value)
        self.assertFalse(manager.state.lockdown_active)

    def test_03_high_event_activates_lockdown(self):
        manager = self.create_manager()

        event = manager.create_event(
            event_type=SecurityEventType.INPUT_BLOCKED,
            severity=SecuritySeverity.HIGH,
            source="telegram",
            message="SQL injection blocked.",
            actor_id="telegram:123",
            public_reason="security_policy_triggered",
        )

        manager.record_event(event)

        self.assertEqual(manager.state.current_state, SecuritySystemState.LOCKDOWN.value)
        self.assertTrue(manager.state.lockdown_active)
        self.assertEqual(manager.state.total_high_or_critical_events, 1)

    def test_04_critical_event_activates_lockdown(self):
        manager = self.create_manager()

        event = manager.create_event(
            event_type=SecurityEventType.INPUT_BLOCKED,
            severity=SecuritySeverity.CRITICAL,
            source="telegram",
            message="Command injection blocked.",
            actor_id="telegram:123",
            public_reason="critical_security_policy_triggered",
        )

        manager.record_event(event)

        self.assertEqual(manager.state.current_state, SecuritySystemState.LOCKDOWN.value)
        self.assertTrue(manager.state.lockdown_active)

    def test_05_activate_staff_from_lockdown(self):
        manager = self.create_manager()

        manager.activate_lockdown("Manual lockdown.")
        manager.activate_staff("Operator activated STAFF.")

        self.assertEqual(manager.state.current_state, SecuritySystemState.STAFF_ACTIVE.value)
        self.assertTrue(manager.state.staff_active)
        self.assertTrue(manager.state.lockdown_active)

    def test_06_request_recovery_keeps_lockdown_active(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.activate_staff()
        manager.request_recovery()

        self.assertEqual(manager.state.current_state, SecuritySystemState.RECOVERY_PENDING.value)
        self.assertTrue(manager.state.lockdown_active)
        self.assertTrue(manager.state.staff_active)

    def test_07_start_recovery_validation_sets_window(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.activate_staff()
        manager.request_recovery()
        manager.start_recovery_validation()

        self.assertEqual(manager.state.current_state, SecuritySystemState.RECOVERY_VALIDATION.value)
        self.assertIsNotNone(manager.state.recovery_validation_started_at_utc)
        self.assertIsNotNone(manager.state.recovery_validation_until_utc)

    def test_08_cannot_release_before_validation_window(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.activate_staff()
        manager.request_recovery()
        manager.start_recovery_validation()

        self.assertFalse(manager.can_release_after_validation())

    def test_09_release_after_completed_validation_window(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.activate_staff()
        manager.request_recovery()
        manager.start_recovery_validation()

        started_at = utc_now() - timedelta(minutes=70)
        until = utc_now() - timedelta(minutes=10)

        manager.state.recovery_validation_started_at_utc = to_iso_utc(started_at)
        manager.state.recovery_validation_until_utc = to_iso_utc(until)
        manager.state.last_high_or_critical_at_utc = to_iso_utc(started_at - timedelta(minutes=5))
        manager.save_state()

        self.assertTrue(manager.can_release_after_validation())

        manager.release_after_validation()

        self.assertEqual(manager.state.current_state, SecuritySystemState.RELEASED_MONITORING.value)
        self.assertFalse(manager.state.lockdown_active)
        self.assertTrue(manager.state.staff_active)

    def test_10_new_high_event_during_validation_blocks_release(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.activate_staff()
        manager.request_recovery()
        manager.start_recovery_validation()

        started_at = utc_now() - timedelta(minutes=70)
        until = utc_now() - timedelta(minutes=10)
        new_threat = utc_now() - timedelta(minutes=5)

        manager.state.recovery_validation_started_at_utc = to_iso_utc(started_at)
        manager.state.recovery_validation_until_utc = to_iso_utc(until)
        manager.state.last_high_or_critical_at_utc = to_iso_utc(new_threat)
        manager.save_state()

        self.assertFalse(manager.can_release_after_validation())

    def test_11_force_release_requires_operator_auth(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")

        with self.assertRaises(PermissionError):
            manager.force_release(operator_authenticated=False)

    def test_12_force_release_moves_to_released_monitoring(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.force_release(operator_authenticated=True)

        self.assertEqual(manager.state.current_state, SecuritySystemState.RELEASED_MONITORING.value)
        self.assertFalse(manager.state.lockdown_active)
        self.assertTrue(manager.state.staff_active)

    def test_13_complete_monitoring_returns_to_normal_when_expired(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        manager.force_release(operator_authenticated=True)

        manager.state.released_monitoring_until_utc = to_iso_utc(utc_now() - timedelta(minutes=1))
        manager.save_state()

        manager.complete_released_monitoring_if_expired()

        self.assertEqual(manager.state.current_state, SecuritySystemState.NORMAL.value)
        self.assertFalse(manager.state.staff_active)

    def test_14_dashboard_snapshot_has_expected_sections(self):
        manager = self.create_manager()

        snapshot = manager.get_dashboard_snapshot()

        self.assertIn("system", snapshot)
        self.assertIn("incident", snapshot)
        self.assertIn("recovery", snapshot)
        self.assertIn("metrics", snapshot)
        self.assertIn("allowed_admin_actions", snapshot)

    def test_15_audit_event_is_written_as_jsonl(self):
        manager = self.create_manager()

        event = manager.create_event(
            event_type=SecurityEventType.INPUT_BLOCKED,
            severity=SecuritySeverity.HIGH,
            source="telegram",
            message="SQL injection blocked.",
        )

        manager.record_event(event)

        lines = manager.events_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)

        parsed = json.loads(lines[0])
        self.assertEqual(parsed["event_id"], event.event_id)
        self.assertEqual(parsed["severity"], SecuritySeverity.HIGH.value)

    def test_16_allowed_actions_for_lockdown_include_recovery(self):
        manager = self.create_manager()

        manager.activate_lockdown("Incident.")
        actions = manager.get_allowed_admin_actions()

        self.assertIn("request_recovery", actions)
        self.assertIn("force_release", actions)


if __name__ == "__main__":
    unittest.main()