from __future__ import annotations
from src.security_state_integration import record_blocked_security_event    
from src.lockdown_guard import enforce_lockdown_or_none 

import json
import re
from typing import Any, Dict, Optional, TypedDict
from src.security import (
    GLOBAL_RATE_LIMITER,
    build_security_block_response,
    validate_user_input,
)

from src.language_router import (
    build_language_instruction,
    detect_user_language,
    localize_public_response,
)

from langchain_groq import ChatGroq
from langchain_core.tracers.langchain import wait_for_all_tracers
from langgraph.graph import StateGraph, START, END

from src.config import (
    validate_env,
    GROQ_MODEL_AGENT,
    GROQ_MODEL_FAST,
    GROQ_MODEL_REASONING,
    GROQ_MODEL_GENERAL,
    LANGSMITH_PROJECT,
)


# Define the main LangGraph state / Define o estado principal do LangGraph
class SentryaOpsState(TypedDict):
    user_input: str
    intent: Optional[str]
    priority: Optional[str]
    selected_model: Optional[str]
    confidence: Optional[str]
    reasoning_required: Optional[bool]
    human_review_required: Optional[bool]
    analysis: Optional[str]
    final_response: Optional[str]
    structured_output: Optional[Dict[str, Any]]


# Extract JSON from model response / Extrai JSON da resposta do modelo
def extract_json_from_text(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from markdown or raw text / Tenta extrair bloco JSON de markdown ou texto bruto
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(
            f"No JSON found in model response / Nenhum JSON encontrado na resposta do modelo: {text}"
        )

    return json.loads(match.group(0))


# Create Groq LLM instances / Cria instâncias dos LLMs da Groq
def create_llms() -> Dict[str, Any]:
    validate_env()

    return {
        "fast": {
            "llm": ChatGroq(model=GROQ_MODEL_FAST, temperature=0),
            "model_name": GROQ_MODEL_FAST,
            "role": "fast classification and validation / classificação rápida e validação",
        },
        "agent": {
            "llm": ChatGroq(model=GROQ_MODEL_AGENT, temperature=0),
            "model_name": GROQ_MODEL_AGENT,
            "role": "agent orchestration and structured decision / orquestração do agente e decisão estruturada",
        },
        "reasoning": {
            "llm": ChatGroq(model=GROQ_MODEL_REASONING, temperature=0),
            "model_name": GROQ_MODEL_REASONING,
            "role": "complex reasoning and critical analysis / raciocínio complexo e análise crítica",
        },
        "general": {
            "llm": ChatGroq(model=GROQ_MODEL_GENERAL, temperature=0),
            "model_name": GROQ_MODEL_GENERAL,
            "role": "natural response and synthesis / resposta natural e síntese",
        },
    }


LLM_ROUTES = create_llms()


# Select the best LLM based on the route / Seleciona o melhor LLM com base na rota
def select_llm_by_route(state: SentryaOpsState) -> Dict[str, Any]:
    selected_model = state.get("selected_model") or "agent"
    return LLM_ROUTES.get(selected_model, LLM_ROUTES["agent"])


# Apply deterministic routing guardrails / Aplica guardrails determinísticos de roteamento
def apply_routing_guardrails(user_input: str, parsed: dict) -> dict:
    text = user_input.lower()

    complex_signals = [
        "vários canais",
        "varios canais",
        "crm desorganizado",
        "baixa resposta",
        "decidir qual processo",
        "automatizar primeiro",
        "priorizar",
        "prioridade",
        "diagnóstico",
        "diagnostico",
        "múltiplos problemas",
        "multiplos problemas",
    ]

    technical_signals = [
        "webhook",
        "api",
        "json",
        "n8n",
        "langgraph",
        "langchain",
        "langflow",
        "integrar",
        "conectar",
        "configurar",
        "deploy",
    ]

    commercial_signals = [
        "quero automatizar",
        "crm",
        "leads",
        "atendimento",
        "vendas",
        "processo comercial",
        "cliente",
    ]

    general_signals = [
        "explique",
        "o que é",
        "o que e",
        "como funciona",
        "de forma simples",
        "conceito",
        "resumo",
    ]

    # Force complex analysis route / Força rota de análise complexa
    if any(signal in text for signal in complex_signals):
        parsed["intent"] = "complex_analysis"
        parsed["priority"] = "high"
        parsed["confidence"] = "high"
        parsed["reasoning_required"] = True
        parsed["human_review_required"] = False
        parsed["selected_model"] = "reasoning"
        parsed["analysis"] = (
            "A solicitação apresenta múltiplos problemas operacionais e exige priorização estratégica antes da automação."
        )
        return parsed

    # Force technical request route / Força rota de solicitação técnica
    if any(signal in text for signal in technical_signals):
        parsed["intent"] = "technical_request"
        parsed["priority"] = parsed.get("priority") or "medium"
        parsed["confidence"] = parsed.get("confidence") or "high"
        parsed["reasoning_required"] = False
        parsed["human_review_required"] = False
        parsed["selected_model"] = "agent"
        parsed["analysis"] = (
            "A solicitação envolve integração, configuração técnica ou desenvolvimento de fluxo operacional."
        )
        return parsed

    # Force commercial lead route / Força rota de lead comercial
    if any(signal in text for signal in commercial_signals) and not any(signal in text for signal in general_signals):
        parsed["intent"] = "commercial_lead"
        parsed["priority"] = parsed.get("priority") or "medium"
        parsed["confidence"] = parsed.get("confidence") or "high"
        parsed["reasoning_required"] = False
        parsed["human_review_required"] = False
        parsed["selected_model"] = "agent"
        parsed["analysis"] = (
            "A solicitação indica interesse em automação operacional ou melhoria de processo comercial."
        )
        return parsed

    # Force general question route / Força rota de pergunta geral
    if any(signal in text for signal in general_signals):
        parsed["intent"] = "general_question"
        parsed["priority"] = "low"
        parsed["confidence"] = parsed.get("confidence") or "high"
        parsed["reasoning_required"] = False
        parsed["human_review_required"] = False
        parsed["selected_model"] = "general"
        parsed["analysis"] = (
            "A solicitação pede uma explicação conceitual ou educativa, sem ação técnica imediata."
        )
        return parsed

    return parsed

# Classify input and decide routing / Classifica a entrada e decide o roteamento
def classify_input(state: SentryaOpsState) -> dict:
    user_input = state["user_input"]

    prompt = f"""
You are the fast classification and routing layer of Sentrya Ops V2.

Your job is to classify the user request and decide which model should handle the next step.

User request:
{user_input}

Return ONLY valid JSON with this schema:
{{
  "intent": "commercial_lead | support_request | technical_request | complex_analysis | general_question | unclear",
  "priority": "low | medium | high",
  "confidence": "low | medium | high",
  "reasoning_required": true or false,
  "human_review_required": true or false,
  "selected_model": "fast | agent | reasoning | general",
  "analysis": "short explanation in the detected user language"
}}

Core routing rules:
- Use "general_question" with selected_model "general" when the user asks for a simple explanation, concept, definition, summary, educational answer, or asks "what is", "explain", "how does it work", "de forma simples", "explique", "o que é", or "como funciona".
- Use "technical_request" with selected_model "agent" when the user asks to build, configure, implement, connect, integrate, debug, deploy, create a workflow, call an API, return JSON, use n8n, LangGraph, LangChain, Langflow, webhook or automation logic.
- Use "commercial_lead" with selected_model "agent" when the user shows interest in buying, hiring, automating their business, CRM, leads, sales process, customer service or business operations.
- Use "complex_analysis" with selected_model "reasoning" when the user presents multiple problems, strategic decisions, prioritization, risk, architecture decisions, ambiguous business context or high-impact analysis.
- Use "fast" only for very simple validation, simple classification, yes/no checks or low-risk preprocessing.

Important distinction:
- If the user only wants to understand or learn, route to "general".
- If the user wants the system to do, build, connect, automate, configure or decide operationally, route to "agent" or "reasoning".
- Do NOT classify educational explanation requests as technical_request.
- Do NOT use "agent" for simple conceptual explanations.

Return only JSON. Do not use markdown.
"""

    response = LLM_ROUTES["fast"]["llm"].with_config(
        {
            "run_name": "sentrya_ops_v2_agent_module_classify_input",
            "tags": ["sentrya-ops-v2", "agent-module", "classification", "routing"],
            "metadata": {
                "node": "classify_input",
                "model_role": "fast classification and routing / classificação rápida e roteamento",
                "source": "src.sentrya_agent",
            },
        }
    ).invoke(prompt)

    parsed = extract_json_from_text(response.content)

    # Apply routing guardrails after LLM classification / Aplica guardrails de roteamento após a classificação do LLM
    parsed = apply_routing_guardrails(user_input, parsed)

    return {
        "intent": parsed.get("intent"),
        "priority": parsed.get("priority"),
        "confidence": parsed.get("confidence"),
        "reasoning_required": parsed.get("reasoning_required"),
        "human_review_required": parsed.get("human_review_required"),
        "selected_model": parsed.get("selected_model"),
        "analysis": parsed.get("analysis"),
    }

def generate_structured_response(state: SentryaOpsState) -> dict:
    selected_route = select_llm_by_route(state)

    llm = selected_route["llm"]
    model_name = selected_route["model_name"]
    model_role = selected_route["role"]

    intent = state.get("intent")
    priority = state.get("priority")
    confidence = state.get("confidence")
    selected_model = state.get("selected_model")
    human_review_required = state.get("human_review_required")
    analysis = state.get("analysis")

    prompt = f"""
You are Sentrya Ops V2, an Agentic AI Operations Desk.

Your task is to generate a clean structured operational response based on the classified request.

User request:
{state["user_input"]}

Classification:
intent: {intent}
priority: {priority}
confidence: {confidence}
selected_model: {selected_model}
reasoning_required: {state.get("reasoning_required")}
human_review_required: {human_review_required}
analysis: {analysis}

Selected model:
{model_name}

Model role:
{model_role}

Return ONLY valid JSON with this schema:
{{
 "final_response": "short natural response in the detected user language",
  "structured_output": {{
    "status": "success",
    "intent": "{intent}",
    "priority": "{priority}",
    "confidence": "{confidence}",
    "selected_model": "{selected_model}",
    "model_name": "{model_name}",
    "recommended_action": "short action aligned with the intent",
    "requires_human_review": true or false,
    "summary": "short operational summary in the detected user language"
  }}
}}

Response rules by intent:
- If intent is "commercial_lead", recommend a discovery call, requirement mapping, CRM/process diagnosis or commercial qualification.
- If intent is "technical_request", recommend a technical implementation step, integration plan, API/webhook validation or structured development action.
- If intent is "complex_analysis", recommend diagnosis, prioritization, process mapping, risk review or strategic analysis before implementation.
- If intent is "general_question", provide a simple educational explanation and recommend learning/understanding, NOT implementation.
- If intent is "support_request", recommend support triage, issue reproduction, logs review or troubleshooting.
- If intent is "unclear", recommend asking for more context before deciding the next step.

Important:
- Do not recommend implementation for "general_question" unless the user explicitly asks to build or configure something.
- Keep the final response concise, useful and human.
- Keep the structured_output operational and clean.
- Return only JSON.
- Do not use markdown.
"""

    response = llm.with_config(
        {
            "run_name": "sentrya_ops_v2_agent_module_generate_response",
            "tags": [
                "sentrya-ops-v2",
                "agent-module",
                "structured-response",
                selected_model or "unknown",
            ],
            "metadata": {
                "node": "generate_structured_response",
                "intent": intent,
                "selected_model": selected_model,
                "model_name": model_name,
                "model_role": model_role,
                "source": "src.sentrya_agent",
            },
        }
    ).invoke(prompt)

    parsed = extract_json_from_text(response.content)

    return {
        "final_response": parsed.get("final_response"),
        "structured_output": parsed.get("structured_output"),
    }


# Build clean final output / Cria saída final limpa
def build_clean_output(result: dict) -> dict:
    structured = result.get("structured_output") or {}

    return {
        "status": structured.get("status", "success"),
        "intent": result.get("intent"),
        "priority": result.get("priority"),
        "confidence": result.get("confidence"),
        "selected_route": result.get("selected_model"),
        "model_used": structured.get("model_name"),
        "requires_human_review": structured.get("requires_human_review"),
        "recommended_action": structured.get("recommended_action"),
        "summary": structured.get("summary"),
        "final_response": result.get("final_response"),
    }


# Create LangGraph workflow / Cria o workflow LangGraph
def create_sentrya_graph():
    workflow = StateGraph(SentryaOpsState)

    # Add graph nodes / Adiciona os nodes do grafo
    workflow.add_node("classify_input", classify_input)
    workflow.add_node("generate_structured_response", generate_structured_response)

    # Define graph flow / Define o fluxo do grafo
    workflow.add_edge(START, "classify_input")
    workflow.add_edge("classify_input", "generate_structured_response")
    workflow.add_edge("generate_structured_response", END)

    return workflow.compile()


SENTRYA_GRAPH = create_sentrya_graph()


# Run Sentrya Ops V2 agent / Executa o agente Sentrya Ops V2
def _run_sentrya_agent_core(user_input: str) -> dict:
    input_state: SentryaOpsState = {
        "user_input": user_input,
        "intent": None,
        "priority": None,
        "selected_model": None,
        "confidence": None,
        "reasoning_required": None,
        "human_review_required": None,
        "analysis": None,
        "final_response": None,
        "structured_output": None,
    }

    result = SENTRYA_GRAPH.with_config(
        {
            "run_name": "sentrya_ops_v2_agent_module_run",
            "tags": ["sentrya-ops-v2", "agent-module", "telegram-ready", "multi-llm"],
            "metadata": {
                "source": "src.sentrya_agent",
                "architecture": "multi-model-routing",
                "langsmith_project": LANGSMITH_PROJECT,
            },
        }
    ).invoke(input_state)

    wait_for_all_tracers()

    return build_clean_output(result)


if __name__ == "__main__":
    test_message = "Quero automatizar meu atendimento com IA e integrar com CRM."

    output = _run_sentrya_agent_core(test_message)

    print("SENTRYA_AGENT_TEST_OK")
    print(json.dumps(output, indent=2, ensure_ascii=False))

# =========================
# SECURITY GATE WRAPPER / WRAPPER DE SEGURANÇA
# =========================

def run_sentrya_agent(
    user_input: str,
    *args,
    actor_id: str = "local-dev",
    enable_rate_limit: bool = False,
    **kwargs,
) -> dict:
    # Validate external input before LangGraph / Valida input externo antes do LangGraph
    security_validation = validate_user_input(
        raw_input=user_input,
        actor_id=actor_id,
        rate_limiter=GLOBAL_RATE_LIMITER if enable_rate_limit else None,
    )

        # Detect user language for public responses / Detecta o idioma do usuário para respostas públicas
    detected_language = detect_user_language(user_input)

    if not security_validation["allowed"]:
        # Record blocked security event before returning public response / Registra evento bloqueado antes de retornar resposta pública
        record_blocked_security_event(
            validation=security_validation,
            actor_id=actor_id,
            source="sentrya_agent",
        )

        security_response = build_security_block_response(security_validation)
        return localize_public_response(security_response, detected_language) 

       # Block operational execution if system is in LOCKDOWN / Bloqueia execução operacional se o sistema estiver em LOCKDOWN
    lockdown_response = enforce_lockdown_or_none()

    if lockdown_response is not None:
        return localize_public_response(lockdown_response, detected_language)

    # Add language instruction to the safe input / Adiciona instrução de idioma ao input seguro
    language_instruction = build_language_instruction(detected_language)

    request_label = "User request:" if detected_language == "en" else "Solicitação do usuário:"

    safe_user_input = (
        f"{language_instruction}\n\n"
        f"{request_label}\n"
        f"{security_validation['safe_input_for_agent']}"
    )

    # Run original agent core / Executa o core original do agente
    result = _run_sentrya_agent_core(
        safe_user_input,
        *args,
        **kwargs,
    )

    # Guarantee dictionary output / Garante saída em dicionário
    if not isinstance(result, dict):
        result = {
            "status": "success",
            "intent": "unknown",
            "priority": "medium",
            "confidence": "medium",
            "selected_route": "agent",
            "model_used": "unknown",
            "requires_human_review": True,
            "recommended_action": "Review agent output manually.",
            "summary": "The agent returned a non-structured response.",
            "final_response": str(result),
        }
    result["security"] = {
    "status": "passed",
    "risk_level": security_validation["risk_level"],
}
    
    # Attach detected language to output / Anexa idioma detectado à saída
    result["detected_language"] = detected_language
    
    return result

