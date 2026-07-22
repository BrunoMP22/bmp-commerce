"""Equivalente a API/Controllers/AuthController.cs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AuthServiceDep, CurrentUserId
from app.schemas.auth import AuthenticatedUserResult, LoginRequest, LoginResult

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResult)
def login(request: LoginRequest, auth_service: AuthServiceDep) -> LoginResult:
    result = auth_service.login(request)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.error)

    assert result.value is not None
    return result.value


@router.get("/me", response_model=AuthenticatedUserResult)
def me(user_id: CurrentUserId, auth_service: AuthServiceDep) -> AuthenticatedUserResult:
    return auth_service.obter_usuario_atual(user_id)
