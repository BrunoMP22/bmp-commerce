"""Equivalente a Domain/Common/BaseEntity.cs e Domain/Common/Result.cs do backend original.

`Entity` não é uma dataclass de propósito: cada entidade de domínio segue o mesmo padrão
do C# — um construtor público que valida e levanta DomainException, e um `from_persistence`
que reconstrói o objeto a partir de uma linha do banco sem repassar pelas validações
(equivalente ao construtor privado sem parâmetros que o EF Core usava via reflexão).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


class Entity:
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    def _init_entity(self) -> None:
        self.id = uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = None

    def mark_as_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class Result(Generic[T]):
    """Só para falhas de regra de negócio recuperáveis pelo chamador (ex: "SKU duplicado").
    "Não encontrado" nunca usa Result — sempre NotFoundException (ver core/exceptions.py)."""

    __slots__ = ("_is_success", "_value", "_error")

    def __init__(self, is_success: bool, value: T | None, error: str | None) -> None:
        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T | None:
        return self._value

    @property
    def error(self) -> str | None:
        return self._error

    @classmethod
    def success(cls, value: T | None = None) -> Result[T]:
        return cls(True, value, None)

    @classmethod
    def failure(cls, error: str) -> Result[T]:
        return cls(False, None, error)
