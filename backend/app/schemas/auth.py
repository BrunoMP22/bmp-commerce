"""Equivalente a Application/Operations/Usuarios/AuthDtos.cs."""

from __future__ import annotations

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


class LoginResult(CamelModel):
    token: str
    user: AuthenticatedUserResult
