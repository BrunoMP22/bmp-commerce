"""Equivalente a Domain/Entities/Tenant.cs."""

from __future__ import annotations

from app.core.exceptions import DomainException
from app.domain.common import Entity


class Tenant(Entity):
    def __init__(self, name: str, plan: str) -> None:
        if not name or not name.strip():
            raise DomainException("Nome do tenant é obrigatório.")

        if not plan or not plan.strip():
            raise DomainException("Plan do tenant é obrigatório.")

        self._init_entity()
        self.name = name.strip()
        self.plan = plan.strip()
        self.is_active = True

    def activate(self) -> None:
        self.is_active = True
        self.mark_as_updated()

    def deactivate(self) -> None:
        self.is_active = False
        self.mark_as_updated()

    @classmethod
    def from_persistence(cls, **kwargs) -> Tenant:
        obj = cls.__new__(cls)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
