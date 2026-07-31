"""Agregações compartilhadas pelas regras. Funções puras sobre listas de Venda."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.venda import Venda


def receita(vendas: list[Venda]) -> Decimal:
    return sum((venda.total for venda in vendas), Decimal("0"))


def custo(vendas: list[Venda]) -> Decimal:
    return sum(
        (item.preco_custo_momento * item.quantidade for venda in vendas for item in venda.itens),
        Decimal("0"),
    )


def receita_por_produto(vendas: list[Venda]) -> dict[UUID, tuple[str, Decimal]]:
    """produto_id -> (nome congelado no item, receita). Usa o nome do item mais recente."""
    resultado: dict[UUID, tuple[str, Decimal]] = {}
    for venda in vendas:
        for item in venda.itens:
            nome, acumulado = resultado.get(item.produto_id, (item.produto_nome, Decimal("0")))
            resultado[item.produto_id] = (nome, acumulado + item.subtotal)
    return resultado


def quantidade_por_produto(vendas: list[Venda]) -> dict[UUID, int]:
    resultado: dict[UUID, int] = {}
    for venda in vendas:
        for item in venda.itens:
            resultado[item.produto_id] = resultado.get(item.produto_id, 0) + item.quantidade
    return resultado
