"""Segurança: hashing de senha (equivalente a Infrastructure/Security/PasswordHasher.cs)
e geração/validação de JWT (equivalente a Infrastructure/Security/JwtService.cs).

Claim de tenant usa a mesma chave "tenant_id" que o backend .NET usava
(Infrastructure/Tenancy/TenancyClaimTypes.cs), por consistência — embora o token em
si seja opaco para o frontend, que só armazena e reenvia a string.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from app.core.config import settings

TENANT_CLAIM = "tenant_id"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # hash malformado/incompatível — trata como senha inválida, nunca como erro 500.
        return False


def generate_token(*, user_id: UUID, name: str, email: str, role: str, tenant_id: UUID | None) -> str:
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "name": name,
        "email": email,
        "role": role,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }

    if tenant_id is not None:
        claims[TENANT_CLAIM] = str(tenant_id)

    return jwt.encode(claims, settings.jwt_key, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """Lança jwt.PyJWTError (ou subclasses) se o token for inválido/expirado."""
    return jwt.decode(
        token,
        settings.jwt_key,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
