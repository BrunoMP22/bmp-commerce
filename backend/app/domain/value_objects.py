"""Equivalente a Domain/ValueObjects/Email.cs — validação de formato, normalização para
minúsculas e igualdade por valor."""

from __future__ import annotations

import re

from app.core.exceptions import DomainException

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def create(cls, value: str | None) -> Email:
        if not value or not value.strip():
            raise DomainException("Email não pode ser vazio.")

        normalized = value.strip().lower()

        if not _EMAIL_PATTERN.match(normalized):
            raise DomainException(f"Email '{value}' possui formato inválido.")

        return cls(normalized)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Email) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email({self._value!r})"
