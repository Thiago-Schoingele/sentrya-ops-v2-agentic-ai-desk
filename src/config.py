import os
from dotenv import load_dotenv

load_dotenv(override=True)

# =========================
# GROQ
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_AGENT = os.getenv("GROQ_MODEL_AGENT", "openai/gpt-oss-20b")
GROQ_MODEL_FAST = os.getenv("GROQ_MODEL_FAST", "llama-3.1-8b-instant")
GROQ_MODEL_REASONING = os.getenv("GROQ_MODEL_REASONING", "openai/gpt-oss-120b")
GROQ_MODEL_GENERAL = os.getenv("GROQ_MODEL_GENERAL", "llama-3.3-70b-versatile")

# =========================
# LANGSMITH
# =========================
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "sentrya-ops-v2-agentic-ai-desk")

# =========================
# LANGFLOW
# =========================
LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")

# =========================
# TELEGRAM
# =========================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID")

# =========================
# APP
# =========================
APP_NAME = os.getenv("APP_NAME", "sentrya-ops-v2-agentic-ai-desk")
APP_ENV = os.getenv("APP_ENV", "development")


def validate_env():
    required_vars = [
        "GROQ_API_KEY",
        "LANGSMITH_API_KEY",
        "LANGFLOW_API_KEY",
        "LANGFLOW_BASE_URL",
        "GROQ_MODEL_AGENT",
        "LANGSMITH_PROJECT",
        "LANGSMITH_TRACING",
        "TELEGRAM_BOT_TOKEN",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    return {var: "OK" for var in required_vars}
