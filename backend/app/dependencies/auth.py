"""Extração do usuário autenticado a partir do JWT — equivalente ao
`[Authorize]` + `ICurrentUserService` (Infrastructure/Tenancy no C#, injetado via
`HttpContextAccessor`) do backend original.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token

# `auto_error=False`: preferimos levantar nosso próprio 401 com corpo `{message}`
# (ver app/middleware/exception_handling.py) em vez do 403 genérico que o FastAPI
# devolveria sozinho quando o header Authorization está ausente.
_bearer_scheme = HTTPBearer(
    auto_error=False,
    description='Informe apenas o token. O prefixo "Bearer" é adicionado automaticamente.',
)

_INVALID_TOKEN_MESSAGE = "Token inválido ou expirado."


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> UUID:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado.")

    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE)

    try:
        return UUID(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_INVALID_TOKEN_MESSAGE) from exc


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
