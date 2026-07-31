"""Equivalente a Application/Operations/Usuarios/AuthService.cs."""

from __future__ import annotations

import base64
import binascii
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.security import generate_token, hash_password, verify_password
from app.domain.common import Result
from app.domain.tenant import Tenant
from app.domain.usuario import Usuario
from app.repositories.tenant_repository import TenantRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import (
    AlterarSenhaRequest,
    AtualizarAvatarRequest,
    AtualizarPerfilRequest,
    AuthenticatedUserResult,
    LoginRequest,
    LoginResult,
)

logger = logging.getLogger(__name__)

# Avatar chega como data URL de imagem já redimensionada no cliente.
_PREFIXOS_AVATAR = ("data:image/jpeg;base64,", "data:image/png;base64,", "data:image/webp;base64,")
_TAMANHO_MAXIMO_AVATAR_BYTES = 300 * 1024


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
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

    def alterar_senha(self, user_id: UUID, request: AlterarSenhaRequest) -> Result[None]:
        """Troca a senha do próprio usuário autenticado. Exige a senha atual — um token
        vazado sozinho não é suficiente para tomar a conta."""
        usuario = self._usuarios.get_by_id(user_id)
        if usuario is None:
            raise NotFoundException("Usuário não encontrado.")

        if len(request.nova_senha) < 8:
            return Result.failure("A nova senha deve ter pelo menos 8 caracteres.")

        if not verify_password(request.senha_atual, usuario.password_hash):
            logger.warning("Alteração de senha recusada para o usuário %s: senha atual incorreta.", usuario.id)
            return Result.failure("Senha atual incorreta.")

        if request.senha_atual == request.nova_senha:
            return Result.failure("A nova senha deve ser diferente da senha atual.")

        usuario.change_password(hash_password(request.nova_senha))
        self._usuarios.update(usuario)
        self._session.commit()

        logger.info("Senha alterada com sucesso para o usuário %s.", usuario.id)
        return Result.success()

    def obter_usuario_atual(self, user_id: UUID) -> AuthenticatedUserResult:
        usuario = self._usuarios.get_by_id(user_id)
        if usuario is None:
            raise NotFoundException("Usuário não encontrado.")

        tenant = self._tenants.get_by_id(usuario.tenant_id) if usuario.tenant_id is not None else None

        return self._to_result(usuario, tenant)

    def atualizar_perfil(self, user_id: UUID, request: AtualizarPerfilRequest) -> AuthenticatedUserResult:
        usuario = self._buscar_ou_404(user_id)

        usuario.alterar_nome(request.name)
        self._usuarios.update(usuario)
        self._session.commit()

        return self._resultado_atual(usuario)

    def definir_avatar(self, user_id: UUID, request: AtualizarAvatarRequest) -> Result[AuthenticatedUserResult]:
        usuario = self._buscar_ou_404(user_id)

        imagem = request.imagem.strip()
        prefixo = next((p for p in _PREFIXOS_AVATAR if imagem.startswith(p)), None)
        if prefixo is None:
            return Result.failure("Formato de imagem inválido. Use JPEG, PNG ou WebP.")

        try:
            conteudo = base64.b64decode(imagem[len(prefixo) :], validate=True)
        except (binascii.Error, ValueError):
            return Result.failure("Imagem corrompida ou codificação inválida.")

        if len(conteudo) > _TAMANHO_MAXIMO_AVATAR_BYTES:
            return Result.failure("Imagem muito grande. O limite é 300 KB após o redimensionamento.")

        usuario.definir_avatar(imagem)
        self._usuarios.update(usuario)
        self._session.commit()

        return Result.success(self._resultado_atual(usuario))

    def remover_avatar(self, user_id: UUID) -> AuthenticatedUserResult:
        usuario = self._buscar_ou_404(user_id)

        usuario.remover_avatar()
        self._usuarios.update(usuario)
        self._session.commit()

        return self._resultado_atual(usuario)

    def _buscar_ou_404(self, user_id: UUID) -> Usuario:
        usuario = self._usuarios.get_by_id(user_id)
        if usuario is None:
            raise NotFoundException("Usuário não encontrado.")
        return usuario

    def _resultado_atual(self, usuario: Usuario) -> AuthenticatedUserResult:
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
            avatar=usuario.avatar,
            criado_em=usuario.created_at,
        )
