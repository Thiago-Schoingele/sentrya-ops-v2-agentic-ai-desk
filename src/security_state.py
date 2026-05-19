from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =========================
# SECURITY STATE ENUMS / ENUMS DE ESTADO DE SEGURANÇA
# =========================


class SecuritySystemState(str, Enum):
    # Normal operating mode / Modo normal de operação
    NORMAL = "NORMAL"

    # Suspicious activity observed, system still operational / Atividade suspeita observada, sistema ainda operacional
    WATCH = "WATCH"

    # System contained due to high or critical risk / Sistema contido por risco alto ou crítico
    LOCKDOWN = "LOCKDOWN"

    # Reinforced incident handling mode / Modo reforçado de resposta a incidente
    STAFF_ACTIVE = "STAFF_ACTIVE"

    # Recovery has been requested but not started / Recuperação solicitada, mas ainda não iniciada
    RECOVERY_PENDING = "RECOVERY_PENDING"

    # System is waiting for a safe validation window / Sistema aguardando janela segura de validação
    RECOVERY_VALIDATION = "RECOVERY_VALIDATION"

    # System released and under reinforced monitoring / Sistema liberado e em monitoramento reforçado
    RELEASED_MONITORING = "RELEASED_MONITORING"


class SecuritySeverity(str, Enum):
    # Informational event / Evento informativo
    INFO = "INFO"

    # Low risk event / Evento de baixo risco
    LOW = "LOW"

    # Medium risk event / Evento de risco médio
    MEDIUM = "MEDIUM"

    # High risk event / Evento de alto risco
    HIGH = "HIGH"

    # Critical risk event / Evento crítico
    CRITICAL = "CRITICAL"


class SecurityEventType(str, Enum):
    # Generic security event / Evento genérico de segurança
    GENERIC = "generic"

    # Input blocked by Security Gate / Input bloqueado pelo Security Gate
    INPUT_BLOCKED = "input_blocked"

    # Rate limit exceeded / Limite de taxa excedido
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Authentication event / Evento de autenticação
    AUTH = "auth"

    # Manual admin command / Comando administrativo manual
    ADMIN_COMMAND = "admin_command"

    # Lockdown state change / Alteração de estado Lockdown
    LOCKDOWN = "lockdown"

    # STAFF state change / Alteração de estado STAFF
    STAFF = "staff"

    # Recovery state change / Alteração de estado Recovery
    RECOVERY = "recovery"

    # Monitoring state change / Alteração de estado Monitoring
    MONITORING = "monitoring"


# =========================
# DATA MODELS / MODELOS DE DADOS
# =========================


@dataclass
class SecurityEvent:
    # Security event stored for audit and dashboard / Evento de segurança salvo para auditoria e dashboard
    event_id: str
    timestamp_utc: str
    event_type: str
    severity: str
    source: str
    message: str
    actor_id: Optional[str] = None
    public_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityStateSnapshot:
    # Current security state snapshot / Snapshot do estado atual de segurança
    current_state: str = SecuritySystemState.NORMAL.value
    lockdown_active: bool = False
    lockdown_reason: Optional[str] = None
    staff_active: bool = False
    recovery_requested_at_utc: Optional[str] = None
    recovery_validation_started_at_utc: Optional[str] = None
    recovery_validation_until_utc: Optional[str] = None
    released_monitoring_until_utc: Optional[str] = None
    last_event_id: Optional[str] = None
    last_event_type: Optional[str] = None
    last_event_severity: Optional[str] = None
    last_event_at_utc: Optional[str] = None
    last_high_or_critical_at_utc: Optional[str] = None
    total_events: int = 0
    total_blocked_events: int = 0
    total_high_or_critical_events: int = 0


# =========================
# TIME HELPERS / FUNÇÕES DE TEMPO
# =========================


def utc_now() -> datetime:
    # Return timezone-aware UTC now / Retorna data/hora UTC com timezone
    return datetime.now(timezone.utc)


def to_iso_utc(value: datetime) -> str:
    # Convert datetime to ISO UTC string / Converte datetime para string ISO UTC
    return value.astimezone(timezone.utc).isoformat()


def parse_iso_utc(value: Optional[str]) -> Optional[datetime]:
    # Parse ISO UTC string safely / Interpreta string ISO UTC com segurança
    if not value:
        return None

    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


# =========================
# STATE MANAGER / GERENCIADOR DE ESTADO
# =========================


class SecurityStateManager:
    # Security state machine for Sentrya Ops V2 / Máquina de estados de segurança do Sentrya Ops V2

    def __init__(
        self,
        state_file: str | Path = "data/security_state.json",
        events_file: str | Path = "data/security_events.jsonl",
        recovery_validation_minutes: int = 60,
        released_monitoring_hours: int = 24,
    ) -> None:
        self.state_file = Path(state_file)
        self.events_file = Path(events_file)
        self.recovery_validation_minutes = recovery_validation_minutes
        self.released_monitoring_hours = released_monitoring_hours
        self.state = self._load_state()

    # -------------------------
    # Persistence / Persistência
    # -------------------------

    def _load_state(self) -> SecurityStateSnapshot:
        # Load state from disk or create default / Carrega estado do disco ou cria padrão
        if not self.state_file.exists():
            return SecurityStateSnapshot()

        raw = json.loads(self.state_file.read_text(encoding="utf-8"))
        return SecurityStateSnapshot(**raw)

    def save_state(self) -> None:
        # Save current state to disk / Salva o estado atual no disco
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(asdict(self.state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _append_event(self, event: SecurityEvent) -> None:
        # Append event as JSONL / Adiciona evento como JSONL
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

        with self.events_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    # -------------------------
    # Event creation / Criação de eventos
    # -------------------------

    def create_event(
        self,
        event_type: str | SecurityEventType,
        severity: str | SecuritySeverity,
        source: str,
        message: str,
        actor_id: Optional[str] = None,
        public_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        # Create a normalized security event / Cria evento de segurança normalizado
        event_type_value = event_type.value if isinstance(event_type, SecurityEventType) else str(event_type)
        severity_value = severity.value if isinstance(severity, SecuritySeverity) else str(severity)

        return SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp_utc=to_iso_utc(utc_now()),
            event_type=event_type_value,
            severity=severity_value,
            source=source,
            message=message,
            actor_id=actor_id,
            public_reason=public_reason,
            metadata=metadata or {},
        )

    def record_event(self, event: SecurityEvent) -> SecurityStateSnapshot:
        # Record event and apply state transition / Registra evento e aplica transição de estado
        self._append_event(event)

        self.state.total_events += 1
        self.state.last_event_id = event.event_id
        self.state.last_event_type = event.event_type
        self.state.last_event_severity = event.severity
        self.state.last_event_at_utc = event.timestamp_utc

        if event.event_type == SecurityEventType.INPUT_BLOCKED.value:
            self.state.total_blocked_events += 1

        if event.severity in {SecuritySeverity.HIGH.value, SecuritySeverity.CRITICAL.value}:
            self.state.total_high_or_critical_events += 1
            self.state.last_high_or_critical_at_utc = event.timestamp_utc

            self.activate_lockdown(
                reason=event.public_reason or event.message,
                event_id=event.event_id,
                save=False,
            )

        elif event.severity == SecuritySeverity.MEDIUM.value:
            if self.state.current_state == SecuritySystemState.NORMAL.value:
                self.state.current_state = SecuritySystemState.WATCH.value

        self.save_state()
        return self.state

    # -------------------------
    # Lockdown / Lockdown
    # -------------------------

    def activate_lockdown(
        self,
        reason: str,
        event_id: Optional[str] = None,
        save: bool = True,
    ) -> SecurityStateSnapshot:
        # Activate lockdown mode / Ativa modo lockdown
        self.state.current_state = SecuritySystemState.LOCKDOWN.value
        self.state.lockdown_active = True
        self.state.lockdown_reason = reason
        self.state.staff_active = False

        if event_id:
            self.state.last_event_id = event_id

        if save:
            self.save_state()

        return self.state

    def activate_staff(self, reason: str = "STAFF protocol activated by operator.") -> SecurityStateSnapshot:
        # Activate STAFF reinforced response / Ativa resposta reforçada STAFF
        if self.state.current_state not in {
            SecuritySystemState.LOCKDOWN.value,
            SecuritySystemState.WATCH.value,
            SecuritySystemState.STAFF_ACTIVE.value,
        }:
            self.activate_lockdown(reason=reason, save=False)

        self.state.current_state = SecuritySystemState.STAFF_ACTIVE.value
        self.state.lockdown_active = True
        self.state.staff_active = True
        self.state.lockdown_reason = reason
        self.save_state()

        return self.state

    # -------------------------
    # Recovery / Recuperação
    # -------------------------

    def request_recovery(self) -> SecurityStateSnapshot:
        # Request normal recovery flow / Solicita fluxo normal de recuperação
        self.state.current_state = SecuritySystemState.RECOVERY_PENDING.value
        self.state.lockdown_active = True
        self.state.staff_active = True
        self.state.recovery_requested_at_utc = to_iso_utc(utc_now())
        self.save_state()

        return self.state

    def start_recovery_validation(self) -> SecurityStateSnapshot:
        # Start safe validation window / Inicia janela segura de validação
        now = utc_now()
        until = now + timedelta(minutes=self.recovery_validation_minutes)

        self.state.current_state = SecuritySystemState.RECOVERY_VALIDATION.value
        self.state.lockdown_active = True
        self.state.staff_active = True
        self.state.recovery_validation_started_at_utc = to_iso_utc(now)
        self.state.recovery_validation_until_utc = to_iso_utc(until)
        self.save_state()

        return self.state

    def can_release_after_validation(self) -> bool:
        # Check if normal recovery validation can release system / Verifica se a validação normal pode liberar o sistema
        if self.state.current_state != SecuritySystemState.RECOVERY_VALIDATION.value:
            return False

        validation_started_at = parse_iso_utc(self.state.recovery_validation_started_at_utc)
        validation_until = parse_iso_utc(self.state.recovery_validation_until_utc)
        last_high_or_critical = parse_iso_utc(self.state.last_high_or_critical_at_utc)

        if validation_started_at is None or validation_until is None:
            return False

        if utc_now() < validation_until:
            return False

        if last_high_or_critical and last_high_or_critical > validation_started_at:
            return False

        return True

    def release_after_validation(self) -> SecurityStateSnapshot:
        # Release after successful validation window / Libera após janela de validação bem-sucedida
        if not self.can_release_after_validation():
            raise RuntimeError(
                "Recovery validation window is not complete or a new high-risk event was detected."
            )

        return self._release_to_monitoring()

    def force_release(self, operator_authenticated: bool) -> SecurityStateSnapshot:
        # Force release with Operator Auth already validated / Liberação imediata com Operator Auth já validado
        if not operator_authenticated:
            raise PermissionError("Operator authentication is required for force release.")

        return self._release_to_monitoring()

    def _release_to_monitoring(self) -> SecurityStateSnapshot:
        # Release system and keep reinforced monitoring / Libera sistema e mantém monitoramento reforçado
        now = utc_now()
        monitoring_until = now + timedelta(hours=self.released_monitoring_hours)

        self.state.current_state = SecuritySystemState.RELEASED_MONITORING.value
        self.state.lockdown_active = False
        self.state.lockdown_reason = None
        self.state.staff_active = True
        self.state.released_monitoring_until_utc = to_iso_utc(monitoring_until)
        self.save_state()

        return self.state

    def complete_released_monitoring_if_expired(self) -> SecurityStateSnapshot:
        # Return to normal after monitoring window expires / Retorna ao normal após expirar janela de monitoramento
        monitoring_until = parse_iso_utc(self.state.released_monitoring_until_utc)

        if (
            self.state.current_state == SecuritySystemState.RELEASED_MONITORING.value
            and monitoring_until is not None
            and utc_now() >= monitoring_until
        ):
            self.state.current_state = SecuritySystemState.NORMAL.value
            self.state.staff_active = False
            self.state.released_monitoring_until_utc = None
            self.save_state()

        return self.state

    # -------------------------
    # Dashboard contract / Contrato para dashboard
    # -------------------------

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        # Return dashboard-safe state snapshot / Retorna snapshot seguro para dashboard
        state = asdict(self.state)

        return {
            "system": {
                "name": "Sentrya Ops V2",
                "security_state": state["current_state"],
                "lockdown_active": state["lockdown_active"],
                "staff_active": state["staff_active"],
            },
            "incident": {
                "last_event_id": state["last_event_id"],
                "last_event_type": state["last_event_type"],
                "last_event_severity": state["last_event_severity"],
                "last_event_at_utc": state["last_event_at_utc"],
                "last_high_or_critical_at_utc": state["last_high_or_critical_at_utc"],
                "lockdown_reason": state["lockdown_reason"],
            },
            "recovery": {
                "requested_at_utc": state["recovery_requested_at_utc"],
                "validation_started_at_utc": state["recovery_validation_started_at_utc"],
                "validation_until_utc": state["recovery_validation_until_utc"],
                "released_monitoring_until_utc": state["released_monitoring_until_utc"],
                "can_release_after_validation": self.can_release_after_validation(),
            },
            "metrics": {
                "total_events": state["total_events"],
                "total_blocked_events": state["total_blocked_events"],
                "total_high_or_critical_events": state["total_high_or_critical_events"],
            },
            "allowed_admin_actions": self.get_allowed_admin_actions(),
        }

    def get_allowed_admin_actions(self) -> List[str]:
        # Return allowed dashboard/admin actions for current state / Retorna ações administrativas permitidas no estado atual
        current_state = self.state.current_state

        if current_state == SecuritySystemState.NORMAL.value:
            return ["view_status", "activate_staff", "activate_lockdown"]

        if current_state == SecuritySystemState.WATCH.value:
            return ["view_status", "activate_staff", "activate_lockdown"]

        if current_state == SecuritySystemState.LOCKDOWN.value:
            return ["view_status", "activate_staff", "request_recovery", "force_release"]

        if current_state == SecuritySystemState.STAFF_ACTIVE.value:
            return ["view_status", "request_recovery", "force_release"]

        if current_state == SecuritySystemState.RECOVERY_PENDING.value:
            return ["view_status", "start_recovery_validation", "force_release"]

        if current_state == SecuritySystemState.RECOVERY_VALIDATION.value:
            return ["view_status", "release_after_validation", "force_release"]

        if current_state == SecuritySystemState.RELEASED_MONITORING.value:
            return ["view_status", "activate_lockdown"]

        return ["view_status"]


# =========================
# FACTORY / FÁBRICA
# =========================


def create_security_state_manager(
    state_file: str | Path = "data/security_state.json",
    events_file: str | Path = "data/security_events.jsonl",
) -> SecurityStateManager:
    # Create default manager / Cria gerenciador padrão
    return SecurityStateManager(
        state_file=state_file,
        events_file=events_file,
    )