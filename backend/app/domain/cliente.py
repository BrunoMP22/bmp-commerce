"""Equivalente a Domain/Entities/Cliente.cs — "CRUD honesto" (Doc 01 §6): sem value
objects nem agregado, validações simples direto na entidade."""

from __future__ import annotations

import re

from app.core.exceptions import DomainException
from app.domain.common import Entity

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Cliente(Entity):
    def __init__(
        self,
        nome: str,
        cpf_cnpj: str | None,
        telefone: str | None,
        email: str | None,
        cidade: str | None,
        estado: str | None,
        observacoes: str | None,
    ) -> None:
        self._init_entity()
        self._preencher(nome, cpf_cnpj, telefone, email, cidade, estado, observacoes)
        self.ativo = True

    def atualizar(
        self,
        nome: str,
        cpf_cnpj: str | None,
        telefone: str | None,
        email: str | None,
        cidade: str | None,
        estado: str | None,
        observacoes: str | None,
        ativo: bool,
    ) -> None:
        self._preencher(nome, cpf_cnpj, telefone, email, cidade, estado, observacoes)
        self.ativo = ativo
        self.mark_as_updated()

    def _preencher(
        self,
        nome: str,
        cpf_cnpj: str | None,
        telefone: str | None,
        email: str | None,
        cidade: str | None,
        estado: str | None,
        observacoes: str | None,
    ) -> None:
        if not nome or not nome.strip():
            raise DomainException("Nome do cliente é obrigatório.")

        self.nome = nome.strip()
        self.cpf_cnpj = self._normalizar_cpf_cnpj(cpf_cnpj)
        self.telefone = telefone.strip() if telefone and telefone.strip() else None
        self.email = self._normalizar_email(email)
        self.cidade = cidade.strip() if cidade and cidade.strip() else None
        self.estado = self._normalizar_estado(estado)
        self.observacoes = observacoes.strip() if observacoes and observacoes.strip() else None

    @staticmethod
    def _normalizar_cpf_cnpj(valor: str | None) -> str | None:
        if not valor or not valor.strip():
            return None

        digitos = "".join(ch for ch in valor if ch.isdigit())

        if len(digitos) not in (11, 14):
            raise DomainException("CPF/CNPJ inválido: informe 11 dígitos (CPF) ou 14 dígitos (CNPJ).")

        return digitos

    @staticmethod
    def _normalizar_email(email: str | None) -> str | None:
        if not email or not email.strip():
            return None

        normalizado = email.strip().lower()

        if not _EMAIL_PATTERN.match(normalizado):
            raise DomainException(f"Email '{email}' possui formato inválido.")

        return normalizado

    @staticmethod
    def _normalizar_estado(estado: str | None) -> str | None:
        if not estado or not estado.strip():
            return None

        normalizado = estado.strip().upper()

        if len(normalizado) != 2:
            raise DomainException("Estado deve ser a sigla UF com 2 letras (ex: SP).")

        return normalizado

    @classmethod
    def from_persistence(cls, **kwargs) -> Cliente:
        obj = cls.__new__(cls)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
