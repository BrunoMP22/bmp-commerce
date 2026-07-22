"""Equivalente a Infrastructure/Persistence/Repositories/VendaRepository.cs.

`itens` é `lazy="selectin"` em `VendaModel` (ver models/venda.py), então toda leitura de
Venda já vem com os itens carregados — equivalente ao `.Include(v => v.Itens)` do EF.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.domain.venda import ItemVenda, Venda
from app.models.base import to_aware_utc, to_naive_utc
from app.models.venda import ItemVendaModel, VendaModel


def _item_to_domain(model: ItemVendaModel) -> ItemVenda:
    return ItemVenda.from_persistence(
        id=model.id,
        venda_id=model.venda_id,
        produto_id=model.produto_id,
        produto_nome=model.produto_nome,
        produto_sku=model.produto_sku,
        quantidade=model.quantidade,
        preco_venda_momento=model.preco_venda_momento,
        preco_custo_momento=model.preco_custo_momento,
        subtotal=model.subtotal,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


def _to_domain(model: VendaModel) -> Venda:
    return Venda.from_persistence(
        itens=[_item_to_domain(item) for item in model.itens],
        id=model.id,
        cliente_id=model.cliente_id,
        cliente_nome=model.cliente_nome,
        usuario_id=model.usuario_id,
        usuario_nome=model.usuario_nome,
        data_hora=to_aware_utc(model.data_hora),
        total=model.total,
        is_deleted=model.is_deleted,
        version=model.version,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


class VendaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, venda_id: uuid.UUID) -> Venda | None:
        model = self._session.get(VendaModel, venda_id)
        return _to_domain(model) if model is not None else None

    def get_all(self) -> list[Venda]:
        query = self._session.query(VendaModel).order_by(VendaModel.data_hora.desc())
        return [_to_domain(model) for model in query.all()]

    def existe_venda_com_produto(self, produto_id: uuid.UUID) -> bool:
        return (
            self._session.query(ItemVendaModel.id).filter(ItemVendaModel.produto_id == produto_id).first()
            is not None
        )

    def existe_venda_com_cliente(self, cliente_id: uuid.UUID) -> bool:
        return (
            self._session.query(VendaModel.id).filter(VendaModel.cliente_id == cliente_id).first() is not None
        )

    def add(self, venda: Venda) -> None:
        model = VendaModel(
            id=venda.id,
            cliente_id=venda.cliente_id,
            cliente_nome=venda.cliente_nome,
            usuario_id=venda.usuario_id,
            usuario_nome=venda.usuario_nome,
            data_hora=to_naive_utc(venda.data_hora),
            total=venda.total,
            is_deleted=venda.is_deleted,
            version=venda.version,
            created_at=to_naive_utc(venda.created_at),
            updated_at=to_naive_utc(venda.updated_at),
            itens=[
                ItemVendaModel(
                    id=item.id,
                    produto_id=item.produto_id,
                    produto_nome=item.produto_nome,
                    produto_sku=item.produto_sku,
                    quantidade=item.quantidade,
                    preco_venda_momento=item.preco_venda_momento,
                    preco_custo_momento=item.preco_custo_momento,
                    subtotal=item.subtotal,
                    created_at=to_naive_utc(item.created_at),
                    updated_at=to_naive_utc(item.updated_at),
                )
                for item in venda.itens
            ],
        )
        self._session.add(model)

    def update(self, venda: Venda) -> None:
        """Só usado após `venda.cancelar()` — itens/total nunca mudam pós-registro, então
        só is_deleted/updated_at precisam ser sincronizados de volta pro model rastreado."""
        model = self._session.get(VendaModel, venda.id)
        if model is None:
            raise NotFoundException("Venda não encontrada.")

        model.is_deleted = venda.is_deleted
        model.updated_at = to_naive_utc(venda.updated_at)
