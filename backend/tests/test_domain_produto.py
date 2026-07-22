"""Equivalente aos testes de domínio de Produto que existiriam em
BMPCommerce.UnitTests (o projeto C# tinha apenas o `UnitTest1.cs` gerado pelo
template, sem testes reais — esta suíte é escrita do zero para o backend Python)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.exceptions import DomainException
from app.domain.enums import UnidadeMedida
from app.domain.produto import Produto


def _make_produto(**overrides) -> Produto:
    defaults = dict(
        nome="Caneta",
        sku="PAP-001",
        descricao=None,
        codigo_barras=None,
        categoria=None,
        unidade_medida=UnidadeMedida.UNIDADE,
        preco_custo=Decimal("0.80"),
        preco_venda=Decimal("1.90"),
        estoque_atual=10,
        estoque_minimo=2,
    )
    defaults.update(overrides)
    return Produto(**defaults)


def test_criar_produto_valido_define_ativo_e_version():
    produto = _make_produto()

    assert produto.ativo is True
    assert produto.version == 1
    assert produto.nome == "Caneta"


def test_preco_venda_zero_ou_negativo_levanta_domain_exception():
    with pytest.raises(DomainException, match="Preço de venda deve ser maior que zero"):
        _make_produto(preco_venda=Decimal("0"))


def test_preco_custo_negativo_levanta_domain_exception():
    with pytest.raises(DomainException, match="Preço de custo não pode ser negativo"):
        _make_produto(preco_custo=Decimal("-1"))


def test_nome_vazio_levanta_domain_exception():
    with pytest.raises(DomainException, match="Nome do produto é obrigatório"):
        _make_produto(nome="   ")


def test_baixar_estoque_reduz_quantidade_e_marca_atualizado():
    produto = _make_produto(estoque_atual=10)

    produto.baixar_estoque(4)

    assert produto.estoque_atual == 6
    assert produto.updated_at is not None


def test_baixar_estoque_insuficiente_bloqueia_e_nao_altera_estoque():
    produto = _make_produto(estoque_atual=2)

    with pytest.raises(DomainException, match="Estoque insuficiente"):
        produto.baixar_estoque(999)

    assert produto.estoque_atual == 2


def test_repor_estoque_aumenta_quantidade():
    produto = _make_produto(estoque_atual=5)

    produto.repor_estoque(3)

    assert produto.estoque_atual == 8


def test_atualizar_com_sku_invalido_nao_altera_estado_anterior():
    produto = _make_produto()

    with pytest.raises(DomainException):
        produto.atualizar(
            nome="Novo nome",
            sku="",
            descricao=None,
            codigo_barras=None,
            categoria=None,
            unidade_medida=UnidadeMedida.UNIDADE,
            preco_custo=Decimal("1"),
            preco_venda=Decimal("2"),
            estoque_atual=1,
            estoque_minimo=0,
            ativo=True,
        )

    assert produto.nome == "Caneta"
