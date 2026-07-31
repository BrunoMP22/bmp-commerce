"""Equivalente a API/Controllers/AuthController.cs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AuthServiceDep, CurrentUserId
from app.schemas.auth import AlterarSenhaRequest, AuthenticatedUserResult, LoginRequest, LoginResult

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


@router.put("/senha", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def alterar_senha(request: AlterarSenhaRequest, user_id: CurrentUserId, auth_service: AuthServiceDep) -> None:
    result = auth_service.alterar_senha(user_id, request)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)
