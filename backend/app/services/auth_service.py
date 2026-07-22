"""Equivalente a Application/Operations/Usuarios/AuthService.cs."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.security import generate_token, verify_password
from app.domain.common import Result
from app.domain.tenant import Tenant
from app.domain.usuario import Usuario
from app.repositories.tenant_repository import TenantRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import AuthenticatedUserResult, LoginRequest, LoginResult

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: Session) -> None:
        self._usuarios = UsuarioRepository(session)
        self._tenants = TenantRepository(session)

    def login(self, request: LoginRequest) -> Result[LoginResult]:
        usuario = self._usuarios.get_by_email(request.email)

        if usuario is None or not usuario.is_active or not verify_password(request.password, usuario.password_hash):
            logger.warning("Tentativa de login falhou para o email %s.", request.email)
            return Result.failure("Email ou senha inválidos.")

        tenant: Tenant | None = None

        if usuario.tenant_id is not None:
            tenant = self._tenants.get_by_id(usuario.tenant_id)

            if tenant is None or not tenant.is_active:
                logger.warning(
                    "Login bloqueado para o usuário %s: tenant %s inativo ou não encontrado.",
                    usuario.id,
                    usuario.tenant_id,
                )
                return Result.failure("Empresa inativa ou não encontrada.")

        token = generate_token(
            user_id=usuario.id,
            name=usuario.name,
            email=usuario.email.value,
            role=usuario.role.value,
            tenant_id=usuario.tenant_id,
        )
        user = self._to_result(usuario, tenant)

        logger.info("Login bem-sucedido para o usuário %s.", usuario.id)

        return Result.success(LoginResult(token=token, user=user))

    def obter_usuario_atual(self, user_id: UUID) -> AuthenticatedUserResult:
        usuario = self._usuarios.get_by_id(user_id)
        if usuario is None:
            raise NotFoundException("Usuário não encontrado.")

        tenant = self._tenants.get_by_id(usuario.tenant_id) if usuario.tenant_id is not None else None

        return self._to_result(usuario, tenant)

    @staticmethod
    def _to_result(usuario: Usuario, tenant: Tenant | None) -> AuthenticatedUserResult:
        return AuthenticatedUserResult(
            user_id=usuario.id,
            name=usuario.name,
            email=usuario.email.value,
            role=usuario.role.value,
            tenant_id=usuario.tenant_id,
            tenant_name=tenant.name if tenant is not None else None,
        )
