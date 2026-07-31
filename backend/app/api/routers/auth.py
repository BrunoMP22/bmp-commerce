"""Equivalente a API/Controllers/AuthController.cs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AuthServiceDep, CurrentUserId
from app.schemas.auth import (
    AlterarSenhaRequest,
    AtualizarAvatarRequest,
    AtualizarPerfilRequest,
    AuthenticatedUserResult,
    LoginRequest,
    LoginResult,
)

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


@router.put("/perfil", response_model=AuthenticatedUserResult)
def atualizar_perfil(
    request: AtualizarPerfilRequest, user_id: CurrentUserId, auth_service: AuthServiceDep
) -> AuthenticatedUserResult:
    return auth_service.atualizar_perfil(user_id, request)


@router.put("/avatar", response_model=AuthenticatedUserResult)
def definir_avatar(
    request: AtualizarAvatarRequest, user_id: CurrentUserId, auth_service: AuthServiceDep
) -> AuthenticatedUserResult:
    result = auth_service.definir_avatar(user_id, request)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)

    assert result.value is not None
    return result.value


@router.delete("/avatar", response_model=AuthenticatedUserResult)
def remover_avatar(user_id: CurrentUserId, auth_service: AuthServiceDep) -> AuthenticatedUserResult:
    return auth_service.remover_avatar(user_id)
