from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


SENTRYA_SCOPE_GUARDRAIL = (
    "This model may operate only inside the Sentrya Ops V2 Security and AI Operations Command Center scope."
)

TELEGRAM_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━"


@dataclass(frozen=True)
class LlmRole:
    role_id: str
    model_name: str
    operational_role: str
    primary_function: str
    use_when: str
    must_not_do: str
    scope_guardrail: str


LLM_ROLE_REGISTRY: dict[str, LlmRole] = {
    "fast": LlmRole(
        role_id="fast",
        model_name="llama-3.1-8b-instant",
        operational_role="FAST MODEL",
        primary_function=(
            "Fast classification, lightweight triage, preprocessing, simple validation, "
            "and low-latency intent detection."
        ),
        use_when=(
            "Use when the request is simple, direct, repetitive, low-risk, "
            "or only needs quick classification."
        ),
        must_not_do=(
            "Must not perform deep reasoning, critical security analysis, final strategic decisions, "
            "or anything outside Sentrya Ops V2."
        ),
        scope_guardrail=SENTRYA_SCOPE_GUARDRAIL,
    ),
    "agent": LlmRole(
        role_id="agent",
        model_name="openai/gpt-oss-20b",
        operational_role="AGENT MODEL",
        primary_function=(
            "Main orchestration, route selection, structured JSON, tool/API/webhook planning, "
            "and operational decision-making."
        ),
        use_when=(
            "Use when the system needs to choose the next operational step, coordinate tools, "
            "generate structured output, or control the LangGraph workflow."
        ),
        must_not_do=(
            "Must not replace the reasoning model for complex or high-impact cases, bypass security controls, "
            "or act outside Sentrya Ops V2."
        ),
        scope_guardrail=SENTRYA_SCOPE_GUARDRAIL,
    ),
    "reasoning": LlmRole(
        role_id="reasoning",
        model_name="openai/gpt-oss-120b",
        operational_role="REASONING MODEL",
        primary_function=(
            "Deep analysis, ambiguity resolution, critical review, risk analysis, "
            "security-sensitive reasoning, and complex decision support."
        ),
        use_when=(
            "Use when the request is complex, ambiguous, high-impact, low-confidence, "
            "or involves architecture, security, or recovery decisions."
        ),
        must_not_do=(
            "Must not handle simple requests by default, replace the general model for final user-facing synthesis, "
            "or act outside Sentrya Ops V2."
        ),
        scope_guardrail=SENTRYA_SCOPE_GUARDRAIL,
    ),
    "general": LlmRole(
        role_id="general",
        model_name="llama-3.3-70b-versatile",
        operational_role="GENERAL MODEL",
        primary_function=(
            "Natural language response, final explanation, synthesis, summary, executive communication, "
            "and user-facing answer refinement."
        ),
        use_when=(
            "Use when the system already has the technical decision and needs a clear, natural, "
            "user-facing answer."
        ),
        must_not_do=(
            "Must not make main routing decisions, perform security-critical analysis alone, replace the agent model "
            "for JSON/tool orchestration, or act outside Sentrya Ops V2."
        ),
        scope_guardrail=SENTRYA_SCOPE_GUARDRAIL,
    ),
}

DETAILED_ROLE_FORMATTING: dict[str, dict[str, list[str]]] = {
    "fast": {
        "use_when": [
            "The request is simple, direct, repetitive, or low-risk.",
            "The system only needs quick classification.",
            "A fast first-pass routing decision is required.",
        ],
        "must_not_do": [
            "Deep reasoning.",
            "Critical security analysis.",
            "Final strategic decisions.",
            "Anything outside Sentrya Ops V2.",
        ],
    },
    "agent": {
        "use_when": [
            "The system needs to choose the next operational step.",
            "Tools, APIs, or webhooks need coordination.",
            "Structured JSON or LangGraph workflow control is required.",
        ],
        "must_not_do": [
            "Replace the reasoning model for complex or high-impact cases.",
            "Bypass security controls.",
            "Act outside Sentrya Ops V2.",
        ],
    },
    "reasoning": {
        "use_when": [
            "The request is complex, ambiguous, high-impact, or low-confidence.",
            "Architecture, security, or recovery decisions are involved.",
            "Critical review or risk analysis is required.",
        ],
        "must_not_do": [
            "Handle simple requests by default.",
            "Replace the general model for final user-facing synthesis.",
            "Act outside Sentrya Ops V2.",
        ],
    },
    "general": {
        "use_when": [
            "The technical decision is already available.",
            "The system needs a clear natural-language answer.",
            "Executive communication, summary, or final response refinement is required.",
        ],
        "must_not_do": [
            "Make main routing decisions.",
            "Perform security-critical analysis alone.",
            "Replace the agent model for JSON or tool orchestration.",
            "Act outside Sentrya Ops V2.",
        ],
    },
}

CAPABILITY_LINES_PT: dict[str, list[str]] = {
    "fast": [
        "Classificação rápida",
        "Triagem leve",
        "Validação simples",
        "Detecção de intenção com baixa latência",
    ],
    "agent": [
        "Orquestração principal",
        "Escolha de rotas",
        "JSON estruturado",
        "Planejamento com ferramentas, APIs e webhooks",
    ],
    "reasoning": [
        "Análise profunda",
        "Resolução de ambiguidades",
        "Revisão crítica",
        "Análise de risco e decisões complexas",
    ],
    "general": [
        "Resposta natural",
        "Síntese",
        "Resumo executivo",
        "Refinamento da comunicação final",
    ],
}

CAPABILITY_LINES_EN: dict[str, list[str]] = {
    "fast": [
        "Fast classification",
        "Lightweight triage",
        "Simple validation",
        "Low-latency intent detection",
    ],
    "agent": [
        "Main orchestration",
        "Route selection",
        "Structured JSON",
        "Tool, API, and webhook planning",
    ],
    "reasoning": [
        "Deep analysis",
        "Ambiguity resolution",
        "Critical review",
        "Risk analysis and complex decision support",
    ],
    "general": [
        "Natural response",
        "Synthesis",
        "Executive summary",
        "Final communication refinement",
    ],
}


def get_llm_roles() -> dict[str, LlmRole]:
    return dict(LLM_ROLE_REGISTRY)


def get_llm_role(role_id: str) -> LlmRole:
    normalized_role_id = (role_id or "").strip().lower()

    try:
        return LLM_ROLE_REGISTRY[normalized_role_id]
    except KeyError as error:
        raise ValueError(f"Unknown LLM role: {role_id}") from error


def get_llm_role_summary_lines() -> list[str]:
    lines: list[str] = []

    for role in LLM_ROLE_REGISTRY.values():
        lines.extend(
            [
                f"{role.operational_role} — {role.model_name}",
                f"Function: {role.primary_function}",
                f"Use when: {role.use_when}",
                f"Must not do: {role.must_not_do}",
                f"Scope guardrail: {role.scope_guardrail}",
            ]
        )

    return lines


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"• {item}" for item in items]


def format_llm_roles_for_telegram() -> str:
    sections = [
        "Sentrya Ops V2 — LLM Role Registry",
        "",
        "Each model is restricted to its assigned operational role.",
        "Each model may operate only inside Sentrya Ops V2.",
    ]

    for index, role in enumerate(LLM_ROLE_REGISTRY.values(), start=1):
        formatting = DETAILED_ROLE_FORMATTING[role.role_id]
        sections.extend(
            [
                "",
                TELEGRAM_SEPARATOR,
                "",
                f"{index}. {role.operational_role}",
                f"Model: {role.model_name}",
                "",
                "Function:",
                role.primary_function,
                "",
                "Use when:",
                *_bullet_lines(formatting["use_when"]),
                "",
                "Must not do:",
                *_bullet_lines(formatting["must_not_do"]),
                "",
                "Scope guardrail:",
                role.scope_guardrail,
            ]
        )

    return "\n".join(sections)


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


def is_llm_capability_question(user_text: str) -> bool:
    normalized = _normalize_text(user_text)

    if not normalized:
        return False

    capability_patterns = (
        r"\bqual (e|eh|é)? ?a sua habilidade\b",
        r"\bquais (sao|são) suas habilidades\b",
        r"\bo que voce sabe fazer\b",
        r"\bo que você sabe fazer\b",
        r"\bqual sua funcao\b",
        r"\bwhat can you do\b",
        r"\bwhat are your capabilities\b",
        r"\bwhat are your skills\b",
        r"\bwhat is your role\b",
        r"\byour capabilities\b",
    )

    return any(re.search(pattern, normalized) for pattern in capability_patterns)


def detect_capability_answer_language(user_text: str, detected_language: str | None = None) -> str:
    normalized = _normalize_text(user_text)

    english_patterns = (
        r"\bwhat can you do\b",
        r"\bwhat are your capabilities\b",
        r"\bwhat are your skills\b",
        r"\bwhat is your role\b",
        r"\byour capabilities\b",
    )
    portuguese_patterns = (
        r"\bqual (e|eh|é)? ?a sua habilidade\b",
        r"\bquais (sao|são) suas habilidades\b",
        r"\bo que voce sabe fazer\b",
        r"\bo que você sabe fazer\b",
        r"\bqual sua funcao\b",
    )

    if any(re.search(pattern, normalized) for pattern in english_patterns):
        return "en"

    if any(re.search(pattern, normalized) for pattern in portuguese_patterns):
        return "pt"

    return "en" if detected_language == "en" else "pt"


def _format_capability_role(index: int, role: LlmRole, lines: list[str]) -> list[str]:
    return [
        f"{index}. {role.operational_role}",
        role.model_name,
        *_bullet_lines(lines),
    ]


def format_capability_answer(language: str = "pt") -> str:
    if language == "en":
        sections = [
            "My capabilities are limited to the operational scope of Sentrya Ops V2.",
            "",
            "I use each LLM only according to its assigned function:",
        ]

        capability_lines = CAPABILITY_LINES_EN
        scope_lines = [
            "Scope rule:",
            "I must not operate outside these roles or outside the Sentrya Ops V2 scope.",
        ]
    else:
        sections = [
            "Minhas habilidades são limitadas ao escopo operacional do Sentrya Ops V2.",
            "",
            "Eu uso cada LLM apenas conforme sua função definida:",
        ]

        capability_lines = CAPABILITY_LINES_PT
        scope_lines = [
            "Regra de escopo:",
            "Eu não devo atuar fora dessas funções nem fora do escopo do Sentrya Ops V2.",
        ]

    for index, role in enumerate(LLM_ROLE_REGISTRY.values(), start=1):
        sections.extend(
            [
                "",
                *_format_capability_role(index, role, capability_lines[role.role_id]),
            ]
        )

    sections.extend(["", *scope_lines])

    return "\n".join(sections)
