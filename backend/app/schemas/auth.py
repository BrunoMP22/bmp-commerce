"""Equivalente a Application/Operations/Usuarios/AuthDtos.cs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel


class LoginRequest(CamelModel):
    email: str
    password: str


class AuthenticatedUserResult(CamelModel):
    user_id: UUID
    name: str
    email: str
    role: str
    tenant_id: UUID | None
    tenant_name: str | None
    avatar: str | None
    criado_em: datetime


class LoginResult(CamelModel):
    token: str
    user: AuthenticatedUserResult


class AlterarSenhaRequest(CamelModel):
    senha_atual: str
    # Tamanho mínimo é validado no AuthService (mensagem pt-BR, padrão do projeto).
    nova_senha: str


class AtualizarPerfilRequest(CamelModel):
    name: str


class AtualizarAvatarRequest(CamelModel):
    # Data URL de imagem pequena (o cliente redimensiona antes de enviar).
    imagem: str
