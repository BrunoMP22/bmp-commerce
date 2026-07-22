"""Equivalente a Application/Operations/Vendas/VendaDtos.cs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel


class ItemVendaRequest(CamelModel):
    produto_id: UUID
    quantidade: int


class RegistrarVendaRequest(CamelModel):
    cliente_id: UUID | None = None
    itens: list[ItemVendaRequest]


class ItemVendaDto(CamelModel):
    produto_id: UUID
    produto_nome: str
    produto_sku: str
    quantidade: int
    preco_venda_momento: float
    subtotal: float


class VendaDto(CamelModel):
    id: UUID
    cliente_id: UUID | None
    cliente_nome: str | None
    usuario_nome: str
    data_hora: datetime
    total: float
    quantidade_itens: int
    cancelada: bool
    itens: list[ItemVendaDto]
