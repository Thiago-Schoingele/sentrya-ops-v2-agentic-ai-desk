from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.security_state import (
    SecurityEventType,
    SecuritySeverity,
    SecurityStateManager,
    create_security_state_manager,
)


# =========================
# SEVERITY MAPPING / MAPEAMENTO DE SEVERIDADE
# =========================

CRITICAL_FLAGS = {
    "command_injection",
    "windows_command",
    "linux_shell_command",
    "sensitive_file_access",
    "internal_url_or_ssrf",
    "encoded_base64_payload",
    "encoded_hex_payload",
    "xml_xxe_payload",
}

HIGH_FLAGS = {
    "prompt_injection",
    "sql_injection",
    "html_script_injection",
    "template_injection",
    "sensitive_file_extension",
    "ldap_injection",
    "nosql_injection",
    "output_schema_manipulation",
}

MEDIUM_FLAGS = {
    "rate_limit_exceeded",
    "input_too_long",
    "too_many_lines",
    "excessive_repetition",
}


def map_validation_to_security_severity(validation: Dict[str, Any]) -> SecuritySeverity:
    # Map Security Gate validation result to security state severity / Mapeia validação do Security Gate para severidade da máquina de estados
    flags = set(validation.get("flags", []))
    risk_level = str(validation.get("risk_level", "")).lower()

    if flags.intersection(CRITICAL_FLAGS):
        return SecuritySeverity.CRITICAL

    if flags.intersection(HIGH_FLAGS):
        return SecuritySeverity.HIGH

    if risk_level == "high":
        return SecuritySeverity.HIGH

    if flags.intersection(MEDIUM_FLAGS):
        return SecuritySeverity.MEDIUM

    if risk_level == "medium":
        return SecuritySeverity.MEDIUM

    return SecuritySeverity.LOW


def build_public_security_event_message(validation: Dict[str, Any]) -> str:
    # Build public-safe event message / Cria mensagem pública segura do evento
    if validation.get("allowed") is False:
        return "Security Gate blocked an unsafe input before agent execution."

    return "Security Gate processed an input."


def record_blocked_security_event(
    validation: Dict[str, Any],
    actor_id: Optional[str] = None,
    source: str = "sentrya_agent",
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
    manager: Optional[SecurityStateManager] = None,
) -> Dict[str, Any]:
    # Record blocked input into SecurityStateManager / Registra input bloqueado no SecurityStateManager
    security_manager = manager or create_security_state_manager(
        state_file=state_file,
        events_file=events_file,
    )

    severity = map_validation_to_security_severity(validation)

    event = security_manager.create_event(
        event_type=SecurityEventType.INPUT_BLOCKED,
        severity=severity,
        source=source,
        message=build_public_security_event_message(validation),
        actor_id=actor_id,
        public_reason="security_policy_triggered",
        metadata={
            "risk_level": validation.get("risk_level"),
            "flags_count": len(validation.get("flags", [])),
            "input_length": validation.get("metadata", {}).get("input_length"),
        },
    )

    security_manager.record_event(event)

    return security_manager.get_dashboard_snapshot()