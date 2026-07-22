"""Equivalente a Domain/Entities/Usuario.cs.

Invariantes preservadas:
- SuperAdmin nunca tem tenant_id.
- Admin/Employee sempre tem tenant_id.
- Senha nunca é texto puro — só hash (o construtor só aceita password_hash).
"""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import DomainException
from app.domain.common import Entity
from app.domain.enums import UserRole
from app.domain.value_objects import Email


class Usuario(Entity):
    def __init__(
        self,
        name: str,
        email: Email,
        password_hash: str,
        role: UserRole,
        tenant_id: UUID | None,
    ) -> None:
        if not name or not name.strip():
            raise DomainException("Nome do usuário é obrigatório.")

        if email is None:
            raise DomainException("Email é obrigatório.")

        if not password_hash or not password_hash.strip():
            raise DomainException("PasswordHash é obrigatório.")

        if role == UserRole.SUPER_ADMIN and tenant_id is not None:
            raise DomainException("Usuário SuperAdmin não pode estar vinculado a um tenant.")

        if role != UserRole.SUPER_ADMIN and tenant_id is None:
            raise DomainException("Usuário Admin/Employee precisa estar vinculado a um tenant.")

        self._init_entity()
        self.name = name.strip()
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.tenant_id = tenant_id
        self.is_active = True

    def activate(self) -> None:
        self.is_active = True
        self.mark_as_updated()

    def deactivate(self) -> None:
        self.is_active = False
        self.mark_as_updated()

    def change_password(self, new_password_hash: str) -> None:
        if not new_password_hash or not new_password_hash.strip():
            raise DomainException("PasswordHash é obrigatório.")

        self.password_hash = new_password_hash
        self.mark_as_updated()

    @classmethod
    def from_persistence(cls, **kwargs) -> Usuario:
        obj = cls.__new__(cls)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
