"""Equivalente a Application/Operations/Clientes/ClienteService.cs."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.domain.cliente import Cliente
from app.domain.common import Result
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.cliente import AtualizarClienteRequest, ClienteDto, CriarClienteRequest


class ClienteService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._clientes = ClienteRepository(session)
        self._vendas = VendaRepository(session)

    def listar(self) -> list[ClienteDto]:
        return [self._to_dto(c) for c in self._clientes.get_all()]

    def obter_por_id(self, cliente_id: UUID) -> ClienteDto:
        cliente = self._clientes.get_by_id(cliente_id)
        if cliente is None:
            raise NotFoundException("Cliente não encontrado.")

        return self._to_dto(cliente)

    def criar(self, request: CriarClienteRequest) -> ClienteDto:
        cliente = Cliente(
            nome=request.nome,
            cpf_cnpj=request.cpf_cnpj,
            telefone=request.telefone,
            email=request.email,
            cidade=request.cidade,
            estado=request.estado,
            observacoes=request.observacoes,
        )

        self._clientes.add(cliente)
        self._session.commit()

        return self._to_dto(cliente)

    def atualizar(self, cliente_id: UUID, request: AtualizarClienteRequest) -> ClienteDto:
        cliente = self._clientes.get_by_id(cliente_id)
        if cliente is None:
            raise NotFoundException("Cliente não encontrado.")

        cliente.atualizar(
            nome=request.nome,
            cpf_cnpj=request.cpf_cnpj,
            telefone=request.telefone,
            email=request.email,
            cidade=request.cidade,
            estado=request.estado,
            observacoes=request.observacoes,
            ativo=request.ativo,
        )

        self._clientes.update(cliente)
        self._session.commit()

        return self._to_dto(cliente)

    def excluir(self, cliente_id: UUID) -> Result[None]:
        cliente = self._clientes.get_by_id(cliente_id)
        if cliente is None:
            raise NotFoundException("Cliente não encontrado.")

        if self._vendas.existe_venda_com_cliente(cliente_id):
            return Result.failure(
                "Cliente possui vendas registradas e não pode ser excluído. Inative-o em vez de excluir."
            )

        self._clientes.remove(cliente)
        self._session.commit()

        return Result.success()

    @staticmethod
    def _to_dto(cliente: Cliente) -> ClienteDto:
        return ClienteDto.model_validate(cliente)
