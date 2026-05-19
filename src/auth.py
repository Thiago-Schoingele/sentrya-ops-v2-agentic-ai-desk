from __future__ import annotations

import getpass
import hashlib
import hmac
import os
from pathlib import Path
import secrets
import sys
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv



# Load .env from project root / Carrega .env da raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH, override=True)

DEFAULT_PBKDF2_ITERATIONS = 310_000

AUTH_ENABLED_ENV = "SENTRYA_OPERATOR_AUTH_ENABLED"
USERNAME_ENV = "SENTRYA_OPERATOR_USERNAME"
PASSWORD_HASH_ENV = "SENTRYA_OPERATOR_PASSWORD_HASH"
PASSWORD_SALT_ENV = "SENTRYA_OPERATOR_PASSWORD_SALT"
PASSWORD_ITERATIONS_ENV = "SENTRYA_OPERATOR_PASSWORD_ITERATIONS"


@dataclass
class OperatorAuthConfig:
    # Operator authentication configuration / Configuração da autenticação do operador
    enabled: bool
    username: str
    password_hash: str
    password_salt: str
    iterations: int


class OperatorAuthError(Exception):
    # Base authentication error / Erro base de autenticação
    pass


class OperatorAuthConfigError(OperatorAuthError):
    # Authentication configuration error / Erro de configuração da autenticação
    pass


class OperatorAuthFailedError(OperatorAuthError):
    # Authentication failed error / Erro de autenticação falha
    pass


def generate_password_salt() -> str:
    # Generate a cryptographically secure salt / Gera um salt criptograficamente seguro
    return secrets.token_hex(32)


def hash_password(
    password: str,
    salt: str,
    iterations: int = DEFAULT_PBKDF2_ITERATIONS,
) -> str:
    # Hash password using PBKDF2-HMAC-SHA256 / Gera hash da senha usando PBKDF2-HMAC-SHA256
    if not password:
        raise ValueError("Password cannot be empty.")

    if not salt:
        raise ValueError("Salt cannot be empty.")

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )

    return derived_key.hex()


def verify_password(
    password: str,
    expected_hash: str,
    salt: str,
    iterations: int = DEFAULT_PBKDF2_ITERATIONS,
) -> bool:
    # Verify password with constant-time comparison / Verifica senha com comparação em tempo constante
    calculated_hash = hash_password(
        password=password,
        salt=salt,
        iterations=iterations,
    )

    return hmac.compare_digest(calculated_hash, expected_hash)


def parse_bool(value: Optional[str], default: bool = True) -> bool:
    # Parse boolean environment values / Interpreta valores booleanos do ambiente
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_operator_auth_config() -> OperatorAuthConfig:
    # Load operator authentication config from environment / Carrega configuração de autenticação do operador pelo ambiente
    enabled = parse_bool(os.getenv(AUTH_ENABLED_ENV), default=True)

    username = os.getenv(USERNAME_ENV, "").strip()
    password_hash = os.getenv(PASSWORD_HASH_ENV, "").strip()
    password_salt = os.getenv(PASSWORD_SALT_ENV, "").strip()

    try:
        iterations = int(os.getenv(PASSWORD_ITERATIONS_ENV, str(DEFAULT_PBKDF2_ITERATIONS)))
    except ValueError as error:
        raise OperatorAuthConfigError(
            f"Invalid {PASSWORD_ITERATIONS_ENV}. It must be an integer."
        ) from error

    return OperatorAuthConfig(
        enabled=enabled,
        username=username,
        password_hash=password_hash,
        password_salt=password_salt,
        iterations=iterations,
    )


def validate_operator_auth_config(config: OperatorAuthConfig) -> None:
    # Validate authentication configuration / Valida configuração de autenticação
    if not config.enabled:
        return

    missing_fields = []

    if not config.username:
        missing_fields.append(USERNAME_ENV)

    if not config.password_hash:
        missing_fields.append(PASSWORD_HASH_ENV)

    if not config.password_salt:
        missing_fields.append(PASSWORD_SALT_ENV)

    if missing_fields:
        missing = ", ".join(missing_fields)
        raise OperatorAuthConfigError(
            f"Operator authentication is enabled, but these environment variables are missing: {missing}. "
            f"Run: python -m src.auth setup"
        )

    if config.iterations < 100_000:
        raise OperatorAuthConfigError(
            f"{PASSWORD_ITERATIONS_ENV} is too low. Use at least 100000."
        )


def authenticate_operator(
    username: str,
    password: str,
    config: Optional[OperatorAuthConfig] = None,
) -> bool:
    # Authenticate operator credentials / Autentica credenciais do operador
    config = config or load_operator_auth_config()
    validate_operator_auth_config(config)

    if not config.enabled:
        return True

    username_matches = hmac.compare_digest(username.strip(), config.username)

    if not username_matches:
        return False

    return verify_password(
        password=password,
        expected_hash=config.password_hash,
        salt=config.password_salt,
        iterations=config.iterations,
    )


def require_operator_auth(
    entrypoint_name: str = "Sentrya Ops V2",
    max_attempts: int = 3,
) -> bool:
    # Require operator login before starting a protected entrypoint / Exige login do operador antes de iniciar um ponto protegido
    config = load_operator_auth_config()
    validate_operator_auth_config(config)

    if not config.enabled:
        print(f"[AUTH] Operator authentication disabled for {entrypoint_name}.")
        return True

    print("=" * 80)
    print(f"{entrypoint_name} — Operator Authentication Required")
    print("=" * 80)

    for attempt in range(1, max_attempts + 1):
        username = input("Operator login: ").strip()
        password = getpass.getpass("Operator password: ")

        if authenticate_operator(username, password, config=config):
            print("[AUTH] Operator authenticated successfully.")
            return True

        remaining = max_attempts - attempt
        print(f"[AUTH] Invalid credentials. Attempts remaining: {remaining}")

    raise OperatorAuthFailedError(
        "Operator authentication failed. Sentrya startup blocked."
    )


def setup_operator_credentials() -> None:
    # Generate environment variables for operator login / Gera variáveis de ambiente para login do operador
    print("=" * 80)
    print("Sentrya Ops V2 — Operator Credential Setup")
    print("=" * 80)

    username = input("Create operator login: ").strip()

    if not username:
        raise OperatorAuthConfigError("Operator login cannot be empty.")

    password = getpass.getpass("Create operator password: ")
    password_confirm = getpass.getpass("Confirm operator password: ")

    if password != password_confirm:
        raise OperatorAuthConfigError("Passwords do not match.")

    if len(password) < 12:
        raise OperatorAuthConfigError(
            "Password is too short. Use at least 12 characters."
        )

    salt = generate_password_salt()
    iterations = DEFAULT_PBKDF2_ITERATIONS
    password_hash = hash_password(
        password=password,
        salt=salt,
        iterations=iterations,
    )

    print("\nAdd these lines to your .env file:")
    print("-" * 80)
    print(f"{AUTH_ENABLED_ENV}=true")
    print(f"{USERNAME_ENV}={username}")
    print(f"{PASSWORD_SALT_ENV}={salt}")
    print(f"{PASSWORD_HASH_ENV}={password_hash}")
    print(f"{PASSWORD_ITERATIONS_ENV}={iterations}")
    print("-" * 80)
    print("Do not commit .env to GitHub.")


def verify_operator_credentials_cli() -> None:
    # Verify configured credentials interactively / Verifica credenciais configuradas de forma interativa
    require_operator_auth(
        entrypoint_name="Sentrya Ops V2 Verification",
        max_attempts=3,
    )


def main() -> None:
    # Command-line interface for auth setup and verification / Interface CLI para configurar e verificar autenticação
    command = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "verify"

    if command == "setup":
        setup_operator_credentials()
        return

    if command == "verify":
        verify_operator_credentials_cli()
        return

    raise SystemExit(
        "Invalid command. Use: python -m src.auth setup OR python -m src.auth verify"
    )


if __name__ == "__main__":
    main()
