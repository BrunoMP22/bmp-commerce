"""Extração do usuário autenticado a partir do JWT — equivalente ao
`[Authorize]` + `ICurrentUserService` (Infrastructure/Tenancy no C#, injetado via
`HttpContextAccessor`) do backend original.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.domain.enums import UserRole

# `auto_error=False`: preferimos levantar nosso próprio 401 com corpo `{message}`
# (ver app/middleware/exception_handling.py) em vez do 403 genérico que o FastAPI
# devolveria sozinho quando o header Authorization está ausente.
_bearer_scheme = HTTPBearer(
    auto_error=False,
    description='Informe apenas o token. O prefixo "Bearer" é adicionado automaticamente.',
)

_INVALID_TOKEN_MESSAGE = "Token inválido ou expirado."


def _decode_or_401(
    credentials: HTTPAuthorizationCredentials | None,
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado.")

    try:
        return decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE) from exc


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> UUID:
    payload = _decode_or_401(credentials)

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE)

    try:
        return UUID(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE) from exc


def get_current_user_role(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> UserRole:
    """Papel vindo do claim "role" do JWT. Claim ausente ou desconhecido degrada para
    Funcionário — na dúvida, o menor privilégio (usado pelo filtro de insights
    financeiros, ADR 0004)."""
    payload = _decode_or_401(credentials)

    try:
        return UserRole(payload.get("role"))
    except ValueError:
        return UserRole.EMPLOYEE


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserRole = Annotated[UserRole, Depends(get_current_user_role)]
