from __future__ import annotations

import re
from typing import Any, Dict


# =========================
# LANGUAGE DETECTION / DETECÇÃO DE IDIOMA
# =========================

PORTUGUESE_HINTS = {
    "quero",
    "preciso",
    "automatizar",
    "atendimento",
    "integração",
    "integrar",
    "com",
    "para",
    "meu",
    "minha",
    "empresa",
    "cliente",
    "clientes",
    "resposta",
    "segurança",
    "liberar",
    "bloquear",
    "sistema",
    "agente",
    "crm",
    "ação",
    "recomendada",
    "não",
    "sim",
}

ENGLISH_HINTS = {
    "i",
    "want",
    "need",
    "automate",
    "automation",
    "customer",
    "support",
    "service",
    "integrate",
    "with",
    "for",
    "my",
    "company",
    "business",
    "client",
    "clients",
    "response",
    "security",
    "release",
    "block",
    "system",
    "agent",
    "crm",
    "recommended",
    "action",
    "yes",
    "no",
}


def normalize_for_language_detection(text: str) -> str:
    # Normalize text for language detection / Normaliza texto para detecção de idioma
    return (text or "").strip().lower()


def tokenize_language_text(text: str) -> list[str]:
    # Tokenize text into words / Divide texto em palavras
    return re.findall(r"[a-zA-ZÀ-ÿ']+", normalize_for_language_detection(text))


def detect_user_language(text: str, default_language: str = "pt") -> str:
    # Detect whether user input is Portuguese or English / Detecta se o input do usuário está em português ou inglês
    normalized = normalize_for_language_detection(text)

    if not normalized:
        return default_language

    # Portuguese diacritics are a strong signal / Acentos em português são um sinal forte
    if re.search(r"[ãõçáéíóúâêôà]", normalized):
        return "pt"

    tokens = tokenize_language_text(normalized)

    portuguese_score = sum(1 for token in tokens if token in PORTUGUESE_HINTS)
    english_score = sum(1 for token in tokens if token in ENGLISH_HINTS)

    if english_score > portuguese_score:
        return "en"

    if portuguese_score > english_score:
        return "pt"

    return default_language


def build_language_instruction(language: str) -> str:
    # Build strict instruction for the LLM to answer in the detected language / Cria instrução rígida para o LLM responder no idioma detectado
    if language == "en":
        return (
            "LANGUAGE RULE: The user wrote in English. "
            "You must answer in English only. "
            "All user-facing fields must be written in English, including: "
            "recommended_action, summary and final_response. "
            "Do not answer in Portuguese. "
            "Keep internal technical JSON keys unchanged."
        )

    return (
        "REGRA DE IDIOMA: O usuário escreveu em português. "
        "Você deve responder apenas em português do Brasil. "
        "Todos os campos visíveis ao usuário devem estar em português, incluindo: "
        "recommended_action, summary e final_response. "
        "Não responda em inglês. "
        "Mantenha nomes técnicos internos de campos JSON inalterados."
    )


# =========================
# PUBLIC RESPONSE LOCALIZATION / LOCALIZAÇÃO DE RESPOSTAS PÚBLICAS
# =========================

def localize_public_response(response: Dict[str, Any], language: str) -> Dict[str, Any]:
    # Localize public-safe system responses / Localiza respostas públicas seguras do sistema
    localized = dict(response)
    intent = localized.get("intent")

    if language == "en":
        localized["detected_language"] = "en"
        return localized

    localized["detected_language"] = "pt"

    if intent == "security_block":
        localized["recommended_action"] = "Revisar a solicitação manualmente antes de processar."
        localized["summary"] = "A solicitação foi bloqueada pela validação de segurança."
        localized["final_response"] = (
            "Não posso processar esta solicitação porque ela acionou as regras de segurança do sistema. "
            "Reescreva a mensagem sem comandos, credenciais, instruções de banco de dados, URLs internas, "
            "tentativas de acesso a arquivos ou tentativas de alterar o comportamento do sistema."
        )

    elif intent == "system_lockdown":
        localized["recommended_action"] = (
            "Revisão do operador necessária antes de processar novas solicitações operacionais."
        )
        localized["summary"] = "O Sentrya Ops V2 está atualmente em bloqueio de segurança."
        localized["final_response"] = (
            "O Sentrya Ops V2 está atualmente em bloqueio de segurança. "
            "As solicitações operacionais estão temporariamente bloqueadas até que o operador conclua "
            "o processo de recuperação ou liberação."
        )

    return localized