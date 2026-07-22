"""Equivalente às operações de Tenant de
Infrastructure/Persistence/DbContext/BMPCommerceDbContext.cs (`IApplicationDbContext`)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.domain.tenant import Tenant
from app.models.base import to_aware_utc, to_naive_utc
from app.models.tenant import TenantModel


def _to_domain(model: TenantModel) -> Tenant:
    return Tenant.from_persistence(
        id=model.id,
        name=model.name,
        plan=model.plan,
        is_active=model.is_active,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


class TenantRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        model = self._session.get(TenantModel, tenant_id)
        return _to_domain(model) if model is not None else None

    def get_by_name(self, name: str) -> Tenant | None:
        model = self._session.query(TenantModel).filter(TenantModel.name == name).one_or_none()
        return _to_domain(model) if model is not None else None

    def add(self, tenant: Tenant) -> None:
        model = TenantModel(
            id=tenant.id,
            name=tenant.name,
            plan=tenant.plan,
            is_active=tenant.is_active,
            created_at=to_naive_utc(tenant.created_at),
            updated_at=to_naive_utc(tenant.updated_at),
        )
        self._session.add(model)
