"""Equivalente a Domain/Entities/Produto.cs.

Concorrência otimista: o C# usava a coluna `rowversion` nativa do SQL Server (binária,
incrementada pelo próprio banco). Aqui usamos o mecanismo de `version_id_col` do
SQLAlchemy (inteiro, incrementado pelo próprio SQLAlchemy a cada UPDATE) — mesmo
comportamento observável (duas escritas concorrentes no mesmo produto → conflito
detectado → 409), implementação mais portável. Ver `app/models/produto.py`.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.exceptions import DomainException
from app.domain.common import Entity
from app.domain.enums import UnidadeMedida


class Produto(Entity):
    def __init__(
        self,
        nome: str,
        sku: str,
        descricao: str | None,
        codigo_barras: str | None,
        categoria: str | None,
        unidade_medida: UnidadeMedida,
        preco_custo: Decimal,
        preco_venda: Decimal,
        estoque_atual: int,
        estoque_minimo: int,
    ) -> None:
        self._validar(nome, sku, preco_custo, preco_venda, estoque_atual, estoque_minimo)

        self._init_entity()
        self.nome = nome.strip()
        self.sku = sku.strip()
        self.descricao = descricao.strip() if descricao else None
        self.codigo_barras = codigo_barras.strip() if codigo_barras and codigo_barras.strip() else None
        self.categoria = categoria.strip() if categoria and categoria.strip() else None
        self.unidade_medida = unidade_medida
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.estoque_atual = estoque_atual
        self.estoque_minimo = estoque_minimo
        self.ativo = True
        self.version = 1

    def atualizar(
        self,
        nome: str,
        sku: str,
        descricao: str | None,
        codigo_barras: str | None,
        categoria: str | None,
        unidade_medida: UnidadeMedida,
        preco_custo: Decimal,
        preco_venda: Decimal,
        estoque_atual: int,
        estoque_minimo: int,
        ativo: bool,
    ) -> None:
        self._validar(nome, sku, preco_custo, preco_venda, estoque_atual, estoque_minimo)

        self.nome = nome.strip()
        self.sku = sku.strip()
        self.descricao = descricao.strip() if descricao else None
        self.codigo_barras = codigo_barras.strip() if codigo_barras and codigo_barras.strip() else None
        self.categoria = categoria.strip() if categoria and categoria.strip() else None
        self.unidade_medida = unidade_medida
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.estoque_atual = estoque_atual
        self.estoque_minimo = estoque_minimo
        self.ativo = ativo
        self.mark_as_updated()

    def baixar_estoque(self, quantidade: int) -> None:
        """Doc 01 REGRA 1: nunca deixa o estoque negativo — estoque insuficiente bloqueia
        a venda inteira, nada é debitado."""
        if quantidade <= 0:
            raise DomainException("Quantidade deve ser maior que zero.")

        if self.estoque_atual < quantidade:
            raise DomainException(
                f"Estoque insuficiente para o produto '{self.nome}'. "
                f"Disponível: {self.estoque_atual}, solicitado: {quantidade}."
            )

        self.estoque_atual -= quantidade
        self.mark_as_updated()

    def repor_estoque(self, quantidade: int) -> None:
        """Estorno usado no cancelamento de venda: devolve os itens ao estoque."""
        if quantidade <= 0:
            raise DomainException("Quantidade deve ser maior que zero.")

        self.estoque_atual += quantidade
        self.mark_as_updated()

    @staticmethod
    def _validar(
        nome: str,
        sku: str,
        preco_custo: Decimal,
        preco_venda: Decimal,
        estoque_atual: int,
        estoque_minimo: int,
    ) -> None:
        if not nome or not nome.strip():
            raise DomainException("Nome do produto é obrigatório.")

        if not sku or not sku.strip():
            raise DomainException("SKU do produto é obrigatório.")

        if preco_venda <= 0:
            raise DomainException("Preço de venda deve ser maior que zero.")

        if preco_custo < 0:
            raise DomainException("Preço de custo não pode ser negativo.")

        if estoque_atual < 0:
            raise DomainException("Estoque atual não pode ser negativo.")

        if estoque_minimo < 0:
            raise DomainException("Estoque mínimo não pode ser negativo.")

    @classmethod
    def from_persistence(cls, **kwargs) -> Produto:
        obj = cls.__new__(cls)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
