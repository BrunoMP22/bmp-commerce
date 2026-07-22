"""Equivalente a Infrastructure/Persistence/Repositories/ClienteRepository.cs.

Ver nota de arquitetura em `produto_repository.py` sobre o porquê de existir `update()`
aqui mesmo `IClienteRepository` não tendo esse método no C# original.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.domain.cliente import Cliente
from app.models.base import to_aware_utc, to_naive_utc
from app.models.cliente import ClienteModel


def _to_domain(model: ClienteModel) -> Cliente:
    return Cliente.from_persistence(
        id=model.id,
        nome=model.nome,
        cpf_cnpj=model.cpf_cnpj,
        telefone=model.telefone,
        email=model.email,
        cidade=model.cidade,
        estado=model.estado,
        observacoes=model.observacoes,
        ativo=model.ativo,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


class ClienteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None:
        model = self._session.get(ClienteModel, cliente_id)
        return _to_domain(model) if model is not None else None

    def get_all(self) -> list[Cliente]:
        query = self._session.query(ClienteModel).order_by(ClienteModel.nome)
        return [_to_domain(model) for model in query.all()]

    def add(self, cliente: Cliente) -> None:
        model = ClienteModel(
            id=cliente.id,
            nome=cliente.nome,
            cpf_cnpj=cliente.cpf_cnpj,
            telefone=cliente.telefone,
            email=cliente.email,
            cidade=cliente.cidade,
            estado=cliente.estado,
            observacoes=cliente.observacoes,
            ativo=cliente.ativo,
            created_at=to_naive_utc(cliente.created_at),
            updated_at=to_naive_utc(cliente.updated_at),
        )
        self._session.add(model)

    def update(self, cliente: Cliente) -> None:
        model = self._session.get(ClienteModel, cliente.id)
        if model is None:
            raise NotFoundException("Cliente não encontrado.")

        model.nome = cliente.nome
        model.cpf_cnpj = cliente.cpf_cnpj
        model.telefone = cliente.telefone
        model.email = cliente.email
        model.cidade = cliente.cidade
        model.estado = cliente.estado
        model.observacoes = cliente.observacoes
        model.ativo = cliente.ativo
        model.updated_at = to_naive_utc(cliente.updated_at)

    def remove(self, cliente: Cliente) -> None:
        model = self._session.get(ClienteModel, cliente.id)
        if model is not None:
            self._session.delete(model)
