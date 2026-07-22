"""Base declarativa do SQLAlchemy + helpers de timezone.

SQL Server (datetime2) não guarda offset de timezone — igual ao schema que o EF Core
gerava. O domínio trabalha com datetimes "aware" em UTC (mais correto); estas funções
convertem na fronteira do repositório para não vazar esse detalhe de infraestrutura.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def to_naive_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


def to_aware_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
