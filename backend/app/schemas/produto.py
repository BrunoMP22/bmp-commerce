"""Equivalente a Application/Operations/Produtos/ProdutoDtos.cs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel


class ProdutoDto(CamelModel):
    id: UUID
    nome: str
    descricao: str | None
    sku: str
    codigo_barras: str | None
    categoria: str | None
    unidade_medida: str
    preco_custo: float
    preco_venda: float
    estoque_atual: int
    estoque_minimo: int
    ativo: bool
    created_at: datetime
    updated_at: datetime | None


class CriarProdutoRequest(CamelModel):
    nome: str
    descricao: str | None = None
    sku: str
    codigo_barras: str | None = None
    categoria: str | None = None
    unidade_medida: str
    preco_custo: float
    preco_venda: float
    estoque_atual: int
    estoque_minimo: int


class AtualizarProdutoRequest(CamelModel):
    nome: str
    descricao: str | None = None
    sku: str
    codigo_barras: str | None = None
    categoria: str | None = None
    unidade_medida: str
    preco_custo: float
    preco_venda: float
    estoque_atual: int
    estoque_minimo: int
    ativo: bool
