"""Equivalente às operações de Usuario de
Infrastructure/Persistence/DbContext/BMPCommerceDbContext.cs (`IApplicationDbContext`)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import DomainException
from app.domain.enums import UserRole
from app.domain.usuario import Usuario
from app.domain.value_objects import Email
from app.models.base import to_aware_utc, to_naive_utc
from app.models.usuario import UsuarioModel


def _to_domain(model: UsuarioModel) -> Usuario:
    return Usuario.from_persistence(
        id=model.id,
        name=model.name,
        email=Email.create(model.email),
        password_hash=model.password_hash,
        role=UserRole(model.role),
        tenant_id=model.tenant_id,
        is_active=model.is_active,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


class UsuarioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, usuario_id: uuid.UUID) -> Usuario | None:
        model = self._session.get(UsuarioModel, usuario_id)
        return _to_domain(model) if model is not None else None

    def get_by_email(self, email: str) -> Usuario | None:
        try:
            parsed = Email.create(email)
        except DomainException:
            # Mesmo comportamento do BMPCommerceDbContext.GetUsuarioByEmailAsync: email
            # com formato inválido simplesmente não é encontrado, não é erro 400.
            return None

        model = self._session.query(UsuarioModel).filter(UsuarioModel.email == parsed.value).one_or_none()
        return _to_domain(model) if model is not None else None

    def add(self, usuario: Usuario) -> None:
        model = UsuarioModel(
            id=usuario.id,
            name=usuario.name,
            email=usuario.email.value,
            password_hash=usuario.password_hash,
            role=usuario.role.value,
            is_active=usuario.is_active,
            tenant_id=usuario.tenant_id,
            created_at=to_naive_utc(usuario.created_at),
            updated_at=to_naive_utc(usuario.updated_at),
        )
        self._session.add(model)
