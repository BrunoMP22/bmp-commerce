"""Equivalente a Application/Operations/Vendas/VendaService.cs."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import DomainException, NotFoundException
from app.domain.produto import Produto
from app.domain.venda import Venda
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.venda import ItemVendaDto, RegistrarVendaRequest, VendaDto

logger = logging.getLogger(__name__)


class VendaService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._vendas = VendaRepository(session)
        self._produtos = ProdutoRepository(session)
        self._clientes = ClienteRepository(session)
        self._usuarios = UsuarioRepository(session)

    def listar(self) -> list[VendaDto]:
        return [self._to_dto(v) for v in self._vendas.get_all()]

    def obter_por_id(self, venda_id: UUID) -> VendaDto:
        venda = self._vendas.get_by_id(venda_id)
        if venda is None:
            raise NotFoundException("Venda não encontrada.")

        return self._to_dto(venda)

    def registrar(self, request: RegistrarVendaRequest, usuario_id: UUID) -> VendaDto:
        if not request.itens:
            raise DomainException("Venda deve ter ao menos um item.")

        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundException("Usuário não encontrado.")

        cliente = None
        if request.cliente_id is not None:
            cliente = self._clientes.get_by_id(request.cliente_id)
            if cliente is None:
                raise NotFoundException("Cliente não encontrado.")

        # O mesmo produto informado em mais de uma linha é consolidado somando as
        # quantidades — dict preserva a ordem de primeira ocorrência (equivalente ao
        # GroupBy do LINQ original).
        quantidades: dict[UUID, int] = {}
        for item in request.itens:
            quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade

        itens: list[tuple[Produto, int]] = []
        for produto_id, quantidade in quantidades.items():
            produto = self._produtos.get_by_id(produto_id)
            if produto is None:
                raise NotFoundException("Um dos produtos informados não foi encontrado.")

            itens.append((produto, quantidade))

        # O agregado valida todas as invariantes (estoque, produto ativo, quantidades)
        # e baixa o estoque; o commit único persiste venda + itens + baixa
        # atomicamente (uma transação), e a version dos produtos bloqueia
        # vendas simultâneas conflitantes (Doc 01 REGRA 1 e 2).
        venda = Venda.registrar(usuario, cliente, itens)

        self._vendas.add(venda)
        for produto, _quantidade in itens:
            self._produtos.update(produto)

        self._session.commit()

        logger.info(
            "Venda %s registrada por %s: %s itens, total %s.",
            venda.id,
            usuario_id,
            len(venda.itens),
            venda.total,
        )

        return self._to_dto(venda)

    def cancelar(self, venda_id: UUID) -> VendaDto:
        venda = self._vendas.get_by_id(venda_id)
        if venda is None:
            raise NotFoundException("Venda não encontrada.")

        venda.cancelar()

        # Estorno: devolve os itens ao estoque na mesma transação do cancelamento.
        for item in venda.itens:
            produto = self._produtos.get_by_id(item.produto_id)
            if produto is not None:
                produto.repor_estoque(item.quantidade)
                self._produtos.update(produto)

        self._vendas.update(venda)
        self._session.commit()

        logger.info("Venda %s cancelada; estoque dos itens estornado.", venda.id)

        return self._to_dto(venda)

    @staticmethod
    def _to_dto(venda: Venda) -> VendaDto:
        itens = venda.itens
        return VendaDto(
            id=venda.id,
            cliente_id=venda.cliente_id,
            cliente_nome=venda.cliente_nome,
            usuario_nome=venda.usuario_nome,
            data_hora=venda.data_hora,
            total=venda.total,
            quantidade_itens=sum(item.quantidade for item in itens),
            cancelada=venda.is_deleted,
            itens=[
                ItemVendaDto(
                    produto_id=item.produto_id,
                    produto_nome=item.produto_nome,
                    produto_sku=item.produto_sku,
                    quantidade=item.quantidade,
                    preco_venda_momento=item.preco_venda_momento,
                    subtotal=item.subtotal,
                )
                for item in itens
            ],
        )
