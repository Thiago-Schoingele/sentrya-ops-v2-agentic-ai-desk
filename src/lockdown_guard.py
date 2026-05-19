from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.security_state import (
    SecurityStateManager,
    SecuritySystemState,
    create_security_state_manager,
)


# =========================
# LOCKDOWN CONFIGURATION / CONFIGURAÇÃO DE LOCKDOWN
# =========================

BLOCKING_SECURITY_STATES = {
    SecuritySystemState.LOCKDOWN.value,
    SecuritySystemState.STAFF_ACTIVE.value,
    SecuritySystemState.RECOVERY_PENDING.value,
    SecuritySystemState.RECOVERY_VALIDATION.value,
}


# =========================
# LOCKDOWN CHECKS / VERIFICAÇÕES DE LOCKDOWN
# =========================

def is_agent_execution_allowed(
    manager: Optional[SecurityStateManager] = None,
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
) -> bool:
    # Check if operational agent execution is allowed / Verifica se a execução operacional do agente é permitida
    security_manager = manager or create_security_state_manager(
        state_file=state_file,
        events_file=events_file,
    )

    current_state = security_manager.state.current_state

    if security_manager.state.lockdown_active:
        return False

    if current_state in BLOCKING_SECURITY_STATES:
        return False

    return True


def get_security_runtime_snapshot(
    manager: Optional[SecurityStateManager] = None,
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
) -> Dict[str, Any]:
    # Return public-safe runtime security snapshot / Retorna snapshot público e seguro do estado de segurança
    security_manager = manager or create_security_state_manager(
        state_file=state_file,
        events_file=events_file,
    )

    return security_manager.get_dashboard_snapshot()


# =========================
# PUBLIC RESPONSES / RESPOSTAS PÚBLICAS
# =========================

def build_lockdown_block_response(
    snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    # Build public-safe response when system is in lockdown / Cria resposta pública segura quando o sistema está em lockdown
    snapshot = snapshot or {}

    system = snapshot.get("system", {})
    incident = snapshot.get("incident", {})
    recovery = snapshot.get("recovery", {})

    return {
        "status": "blocked",
        "intent": "system_lockdown",
        "priority": "high",
        "confidence": "high",
        "selected_route": "security",
        "model_used": "security_state_manager",
        "requires_human_review": True,
        "recommended_action": "Operator review required before processing new operational requests.",
        "summary": "Sentrya Ops V2 is currently in security lockdown.",
        "final_response": (
            "Sentrya Ops V2 is currently in security lockdown. "
            "Operational requests are temporarily blocked until the operator completes the recovery or release process."
        ),
        "security": {
            "status": "lockdown_active",
            "security_state": system.get("security_state"),
            "lockdown_active": system.get("lockdown_active"),
            "staff_active": system.get("staff_active"),
            "last_event_type": incident.get("last_event_type"),
            "last_event_severity": incident.get("last_event_severity"),
            "can_release_after_validation": recovery.get("can_release_after_validation"),
        },
    }


def enforce_lockdown_or_none(
    manager: Optional[SecurityStateManager] = None,
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
) -> Optional[Dict[str, Any]]:
    # Return lockdown response if execution is blocked, otherwise None / Retorna resposta de lockdown se bloqueado, senão None
    security_manager = manager or create_security_state_manager(
        state_file=state_file,
        events_file=events_file,
    )

    if is_agent_execution_allowed(manager=security_manager):
        return None

    snapshot = security_manager.get_dashboard_snapshot()
    return build_lockdown_block_response(snapshot)