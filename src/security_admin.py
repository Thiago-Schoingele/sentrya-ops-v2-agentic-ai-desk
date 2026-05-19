from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.auth import authenticate_operator
from src.security_state import (
    SecurityStateManager,
    create_security_state_manager,
)


# =========================
# ADMIN COMMANDS / COMANDOS ADMINISTRATIVOS
# =========================

READ_ONLY_COMMANDS = {
    "status",
    "snapshot",
    "allowed_actions",
}

STATE_CHANGING_COMMANDS = {
    "activate_lockdown",
    "activate_staff",
    "request_recovery",
    "start_recovery_validation",
    "release_after_validation",
    "force_release",
    "complete_monitoring",
}

ALL_ADMIN_COMMANDS = READ_ONLY_COMMANDS.union(STATE_CHANGING_COMMANDS)


# =========================
# HELPERS / FUNÇÕES AUXILIARES
# =========================

def normalize_admin_command(command: str) -> str:
    # Normalize admin command from Telegram, dashboard or CLI / Normaliza comando administrativo vindo do Telegram, dashboard ou CLI
    return (command or "").strip().lower().replace("/", "")


def is_state_changing_command(command: str) -> bool:
    # Check if command changes runtime state / Verifica se o comando altera o estado de runtime
    return normalize_admin_command(command) in STATE_CHANGING_COMMANDS


def is_read_only_command(command: str) -> bool:
    # Check if command is read-only / Verifica se o comando é apenas leitura
    return normalize_admin_command(command) in READ_ONLY_COMMANDS


def is_known_admin_command(command: str) -> bool:
    # Check if command is supported / Verifica se o comando é suportado
    return normalize_admin_command(command) in ALL_ADMIN_COMMANDS


def operator_is_authorized(
    operator_authenticated: bool = False,
    operator_username: Optional[str] = None,
    operator_password: Optional[str] = None,
) -> bool:
    # Validate admin authorization using the same Operator Auth credentials / Valida autorização usando as mesmas credenciais do Operator Auth
    if operator_authenticated:
        return True

    if operator_username and operator_password:
        try:
            return authenticate_operator(
                username=operator_username,
                password=operator_password,
            )
        except Exception:
            return False

    return False


def build_admin_command_result(
    command: str,
    status: str,
    message: str,
    snapshot: Dict[str, Any],
    requires_operator_auth: bool = False,
    public_error: Optional[str] = None,
) -> Dict[str, Any]:
    # Build public-safe admin command result / Cria resultado público seguro para comando administrativo
    return {
        "status": status,
        "command": normalize_admin_command(command),
        "message": message,
        "requires_operator_auth": requires_operator_auth,
        "public_error": public_error,
        "snapshot": snapshot,
    }


# =========================
# ADMIN COMMAND EXECUTOR / EXECUTOR DE COMANDOS ADMINISTRATIVOS
# =========================

def execute_security_admin_command(
    command: str,
    reason: Optional[str] = None,
    operator_authenticated: bool = False,
    operator_username: Optional[str] = None,
    operator_password: Optional[str] = None,
    manager: Optional[SecurityStateManager] = None,
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
) -> Dict[str, Any]:
    # Execute security admin command / Executa comando administrativo de segurança
    normalized_command = normalize_admin_command(command)

    security_manager = manager or create_security_state_manager(
        state_file=state_file,
        events_file=events_file,
    )

    if not is_known_admin_command(normalized_command):
        return build_admin_command_result(
            command=normalized_command,
            status="error",
            message="Unknown security admin command.",
            snapshot=security_manager.get_dashboard_snapshot(),
            public_error="unknown_admin_command",
        )

    if is_state_changing_command(normalized_command):
        authorized = operator_is_authorized(
            operator_authenticated=operator_authenticated,
            operator_username=operator_username,
            operator_password=operator_password,
        )

        if not authorized:
            return build_admin_command_result(
                command=normalized_command,
                status="denied",
                message="Operator authentication is required for this security action.",
                snapshot=security_manager.get_dashboard_snapshot(),
                requires_operator_auth=True,
                public_error="operator_auth_required",
            )

    try:
        if normalized_command in {"status", "snapshot"}:
            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Security state snapshot returned.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "allowed_actions":
            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Allowed admin actions returned.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "activate_lockdown":
            security_manager.activate_lockdown(
                reason=reason or "Manual lockdown activated by operator.",
            )

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Lockdown activated.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "activate_staff":
            security_manager.activate_staff(
                reason=reason or "STAFF protocol activated by operator.",
            )

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="STAFF protocol activated.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "request_recovery":
            security_manager.request_recovery()

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Recovery requested.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "start_recovery_validation":
            security_manager.start_recovery_validation()

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Recovery validation window started.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "release_after_validation":
            security_manager.release_after_validation()

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="System released after successful recovery validation.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "force_release":
            security_manager.force_release(operator_authenticated=True)

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="System force released by authenticated operator.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

        if normalized_command == "complete_monitoring":
            security_manager.complete_released_monitoring_if_expired()

            return build_admin_command_result(
                command=normalized_command,
                status="success",
                message="Released monitoring checked.",
                snapshot=security_manager.get_dashboard_snapshot(),
            )

    except Exception:
        return build_admin_command_result(
            command=normalized_command,
            status="error",
            message="Security admin command could not be completed safely.",
            snapshot=security_manager.get_dashboard_snapshot(),
            public_error="admin_command_failed",
        )

    return build_admin_command_result(
        command=normalized_command,
        status="error",
        message="Security admin command was not executed.",
        snapshot=security_manager.get_dashboard_snapshot(),
        public_error="admin_command_not_executed",
    )


# =========================
# TELEGRAM FORMATTER / FORMATADOR PARA TELEGRAM
# =========================

def format_security_admin_result_for_telegram(result: Dict[str, Any]) -> str:
    # Format admin result for Telegram / Formata resultado administrativo para Telegram
    snapshot = result.get("snapshot", {})
    system = snapshot.get("system", {})
    incident = snapshot.get("incident", {})
    recovery = snapshot.get("recovery", {})
    metrics = snapshot.get("metrics", {})
    allowed_actions = snapshot.get("allowed_admin_actions", [])

    return (
        "Sentrya Ops V2 — Security Admin\n\n"
        f"Command: {result.get('command')}\n"
        f"Status: {result.get('status')}\n"
        f"Message: {result.get('message')}\n\n"
        f"Security State: {system.get('security_state')}\n"
        f"Lockdown Active: {system.get('lockdown_active')}\n"
        f"STAFF Active: {system.get('staff_active')}\n\n"
        f"Last Event Type: {incident.get('last_event_type')}\n"
        f"Last Event Severity: {incident.get('last_event_severity')}\n"
        f"Can Release After Validation: {recovery.get('can_release_after_validation')}\n\n"
        f"Total Events: {metrics.get('total_events')}\n"
        f"Blocked Events: {metrics.get('total_blocked_events')}\n"
        f"High/Critical Events: {metrics.get('total_high_or_critical_events')}\n\n"
        f"Allowed Actions: {', '.join(allowed_actions)}"
    )