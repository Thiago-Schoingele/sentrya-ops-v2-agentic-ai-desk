import asyncio
import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_ID, validate_env
from src.sentrya_agent import run_sentrya_agent
from src.auth import require_operator_auth
from src.language_router import detect_user_language
from src.security_admin import (
    execute_security_admin_command,
    format_security_admin_result_for_telegram,
)


def is_allowed_chat(chat_id: int) -> bool:
    # Check if the Telegram chat is authorized / Verifica se o chat do Telegram está autorizado
    return str(chat_id) == str(TELEGRAM_ALLOWED_CHAT_ID)


def format_agent_response(result: dict) -> str:
    # Format agent result for Telegram based on detected language / Formata o resultado do agente no Telegram conforme o idioma detectado
    detected_language = result.get("detected_language", "pt")

    if detected_language == "en":
        return (
            "Sentrya Ops V2 — Result\n\n"
            f"Intent: {result.get('intent')}\n"
            f"Priority: {result.get('priority')}\n"
            f"Confidence: {result.get('confidence')}\n"
            f"LLM Route: {result.get('selected_route')}\n"
            f"Model used: {result.get('model_used')}\n"
            f"Human review: {result.get('requires_human_review')}\n\n"
            f"Recommended action:\n{result.get('recommended_action')}\n\n"
            f"Final response:\n{result.get('final_response')}"
        )

    return (
        "Sentrya Ops V2 — Resultado\n\n"
        f"Intenção: {result.get('intent')}\n"
        f"Prioridade: {result.get('priority')}\n"
        f"Confiança: {result.get('confidence')}\n"
        f"Rota LLM: {result.get('selected_route')}\n"
        f"Modelo usado: {result.get('model_used')}\n"
        f"Revisão humana: {result.get('requires_human_review')}\n\n"
        f"Ação recomendada:\n{result.get('recommended_action')}\n\n"
        f"Resposta final:\n{result.get('final_response')}"
    )
async def handle_security_admin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: str,
) -> None:
    # Handle security admin command from Telegram / Processa comando administrativo de segurança pelo Telegram
    chat_id = update.effective_chat.id

    if not is_allowed_chat(chat_id):
        await update.message.reply_text(
            "Acesso negado. Este chat não está autorizado a administrar o Sentrya Ops V2."
        )
        return

    result = execute_security_admin_command(
        command=command,
        reason=f"Telegram admin command /{command} from chat_id {chat_id}",
        operator_authenticated=True,
    )

    await update.message.reply_text(
        format_security_admin_result_for_telegram(result)
    )


async def handle_status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Show current security status / Mostra o status atual de segurança
    await handle_security_admin_command(update, context, "status")


async def handle_security_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Alias for security status / Alias para status de segurança
    await handle_security_admin_command(update, context, "status")


async def handle_actions_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Show allowed admin actions / Mostra ações administrativas permitidas
    await handle_security_admin_command(update, context, "allowed_actions")


async def handle_lockdown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Activate manual lockdown / Ativa lockdown manual
    await handle_security_admin_command(update, context, "activate_lockdown")


async def handle_staff_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Activate STAFF protocol / Ativa protocolo STAFF
    await handle_security_admin_command(update, context, "activate_staff")


async def handle_recovery_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Request recovery flow / Solicita fluxo de recuperação
    await handle_security_admin_command(update, context, "request_recovery")


async def handle_start_recovery_validation_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Start recovery validation window / Inicia janela de validação de recuperação
    await handle_security_admin_command(update, context, "start_recovery_validation")


async def handle_force_release_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Force release using authenticated operator session / Liberação imediata usando sessão autenticada do operador
    await handle_security_admin_command(update, context, "force_release")


async def handle_complete_monitoring_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Complete released monitoring if expired / Finaliza monitoramento pós-liberação se expirado
    await handle_security_admin_command(update, context, "complete_monitoring")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle /start command / Processa o comando /start
    chat_id = update.effective_chat.id

    if not is_allowed_chat(chat_id):
        await update.message.reply_text("Acesso não autorizado.")
        return

    await update.message.reply_text(
        "Sentrya Ops V2 ativo.\n\n"
        "Agora o Telegram está conectado ao agente LangGraph.\n"
        "Envie uma solicitação para testar o roteamento multi-LLM."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle /status command / Processa o comando /status
    chat_id = update.effective_chat.id

    if not is_allowed_chat(chat_id):
        await update.message.reply_text("Acesso não autorizado.")
        return

    await update.message.reply_text(
        "Status: online\n"
        "Telegram: conectado\n"
        "LangGraph Agent: conectado\n"
        "Groq multi-LLM: ativo\n"
        "LangSmith tracing: ativo\n"
        "Modo: teste local"
    )


async def test_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle /test_agent command / Processa o comando /test_agent
    chat_id = update.effective_chat.id

    if not is_allowed_chat(chat_id):
        await update.message.reply_text("Acesso não autorizado.")
        return

    test_message = "Quero automatizar meu atendimento com IA e integrar com CRM."

    await update.message.reply_text("Executando teste do agente...")

    try:
        # Run blocking agent call in a thread / Executa a chamada bloqueante do agente em uma thread
        result = await asyncio.to_thread(
    run_sentrya_agent,
    test_message,
    actor_id="telegram:test",
    enable_rate_limit=False,
)

        await update.message.reply_text(format_agent_response(result))

    except Exception as error:
        await update.message.reply_text(
            "Erro ao executar o agente.\n\n"
            f"Detalhes: {error}"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle regular text messages / Processa mensagens de texto comuns
    chat_id = update.effective_chat.id
    user_text = update.message.text
    result_language = detect_user_language(user_text)

    if not is_allowed_chat(chat_id):
        await update.message.reply_text("Acesso não autorizado.")
        return

    await update.message.reply_text("Recebi sua solicitação. Processando com o Sentrya Ops V2...")

    try:
        # Get Telegram chat ID / Obtém o ID do chat do Telegram
        chat_id = update.effective_chat.id

        # Run Sentrya agent with Security Gate and rate limit / Executa o agente Sentrya com Security Gate e rate limit
        result = await asyncio.to_thread(
            run_sentrya_agent,
            user_text,
            actor_id=f"telegram:{chat_id}",
            enable_rate_limit=True,
        )

        await update.message.reply_text(format_agent_response(result))

    except Exception as error:
        await update.message.reply_text(
            "Erro ao processar sua solicitação no agente.\n\n"
            f"Detalhes: {error}"
        )


def main():
    # Validate environment variables / Valida as variáveis de ambiente
    validate_env()

    # Create Telegram application / Cria a aplicação do Telegram
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register bot commands / Registra os comandos do bot
    app.add_handler(CommandHandler("start", start))
        # Security Admin Console commands / Comandos do console administrativo de segurança
    app.add_handler(CommandHandler("status", handle_status_command))
    app.add_handler(CommandHandler("security", handle_security_command))
    app.add_handler(CommandHandler("actions", handle_actions_command))
    app.add_handler(CommandHandler("lockdown", handle_lockdown_command))
    app.add_handler(CommandHandler("staff", handle_staff_command))
    app.add_handler(CommandHandler("recovery", handle_recovery_command))
    app.add_handler(CommandHandler("start_recovery_validation", handle_start_recovery_validation_command))
    app.add_handler(CommandHandler("force_release", handle_force_release_command))
    app.add_handler(CommandHandler("complete_monitoring", handle_complete_monitoring_command))

    # Internal test command / Comando interno de teste
    app.add_handler(CommandHandler("test_agent", test_agent))

    # Register text message handler / Registra o manipulador de mensagens de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("SENTRYA_OPS_V2_TELEGRAM_AGENT_RUNNING")
    print("Press Ctrl+C to stop / Pressione Ctrl+C para parar")

    # Start polling / Inicia o polling
    app.run_polling()


if __name__ == "__main__":
    require_operator_auth(
        entrypoint_name="Sentrya Ops V2 Telegram Bot",
        max_attempts=3,
    )

    # Run bot / Executa o bot
    main()
