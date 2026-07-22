"""Invariantes do agregado Venda (Doc 01 §6, Doc 02 §3.6) — a parte mais crítica do
domínio: nenhum estoque pode ser debitado se QUALQUER item da venda for inválido."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.exceptions import DomainException
from app.domain.cliente import Cliente
from app.domain.enums import UnidadeMedida, UserRole
from app.domain.produto import Produto
from app.domain.usuario import Usuario
from app.domain.value_objects import Email
from app.domain.venda import Venda


def _produto(nome="Caneta", sku="PAP-001", preco_venda="1.90", estoque=10) -> Produto:
    return Produto(
        nome=nome,
        sku=sku,
        descricao=None,
        codigo_barras=None,
        categoria=None,
        unidade_medida=UnidadeMedida.UNIDADE,
        preco_custo=Decimal("0.80"),
        preco_venda=Decimal(preco_venda),
        estoque_atual=estoque,
        estoque_minimo=2,
    )


def _usuario() -> Usuario:
    return Usuario(
        name="Admin",
        email=Email.create("admin@bmpcommerce.com"),
        password_hash="hash",
        role=UserRole.SUPER_ADMIN,
        tenant_id=None,
    )


def test_registrar_venda_debita_estoque_e_soma_total():
    produto = _produto(estoque=10, preco_venda="1.90")
    usuario = _usuario()

    venda = Venda.registrar(usuario, None, [(produto, 3)])

    assert produto.estoque_atual == 7
    assert venda.total == Decimal("5.70")
    assert len(venda.itens) == 1
    assert venda.itens[0].subtotal == Decimal("5.70")
    assert venda.is_deleted is False


def test_registrar_venda_congela_preco_e_nome_no_momento_da_venda():
    produto = _produto(preco_venda="10.00", estoque=5)
    usuario = _usuario()

    venda = Venda.registrar(usuario, None, [(produto, 1)])
    item = venda.itens[0]

    # Alterar o produto depois não pode mudar o histórico já registrado.
    produto.atualizar(
        nome="Nome Novo",
        sku=produto.sku,
        descricao=None,
        codigo_barras=None,
        categoria=None,
        unidade_medida=produto.unidade_medida,
        preco_custo=produto.preco_custo,
        preco_venda=Decimal("999.00"),
        estoque_atual=produto.estoque_atual,
        estoque_minimo=produto.estoque_minimo,
        ativo=True,
    )

    assert item.produto_nome == "Caneta"
    assert item.preco_venda_momento == Decimal("10.00")


def test_registrar_venda_sem_itens_levanta_domain_exception():
    with pytest.raises(DomainException, match="ao menos um item"):
        Venda.registrar(_usuario(), None, [])


def test_estoque_insuficiente_em_um_item_bloqueia_venda_inteira_sem_debitar_nada():
    """INV 5: se QUALQUER item não tiver estoque suficiente, nenhum produto pode ter o
    estoque debitado — nem os itens que, isoladamente, teriam estoque de sobra."""
    produto_ok = _produto(nome="Caderno", sku="PAP-002", estoque=50)
    produto_sem_estoque = _produto(nome="Caneta", sku="PAP-001", estoque=2)
    usuario = _usuario()

    with pytest.raises(DomainException, match="Estoque insuficiente"):
        Venda.registrar(usuario, None, [(produto_ok, 5), (produto_sem_estoque, 999)])

    assert produto_ok.estoque_atual == 50
    assert produto_sem_estoque.estoque_atual == 2


def test_produto_inativo_bloqueia_venda():
    produto = _produto(estoque=10)
    produto.atualizar(
        nome=produto.nome,
        sku=produto.sku,
        descricao=None,
        codigo_barras=None,
        categoria=None,
        unidade_medida=produto.unidade_medida,
        preco_custo=produto.preco_custo,
        preco_venda=produto.preco_venda,
        estoque_atual=produto.estoque_atual,
        estoque_minimo=produto.estoque_minimo,
        ativo=False,
    )

    with pytest.raises(DomainException, match="está inativo"):
        Venda.registrar(_usuario(), None, [(produto, 1)])


def test_venda_com_cliente_inativo_e_bloqueada():
    cliente = Cliente(
        nome="Ana",
        cpf_cnpj=None,
        telefone=None,
        email=None,
        cidade=None,
        estado=None,
        observacoes=None,
    )
    cliente.atualizar(
        nome=cliente.nome,
        cpf_cnpj=None,
        telefone=None,
        email=None,
        cidade=None,
        estado=None,
        observacoes=None,
        ativo=False,
    )
    produto = _produto(estoque=10)

    with pytest.raises(DomainException, match="está inativo"):
        Venda.registrar(_usuario(), cliente, [(produto, 1)])


def test_cancelar_marca_deletada_e_bloqueia_segundo_cancelamento():
    produto = _produto(estoque=10)
    venda = Venda.registrar(_usuario(), None, [(produto, 2)])

    venda.cancelar()

    assert venda.is_deleted is True

    with pytest.raises(DomainException, match="já está cancelada"):
        venda.cancelar()
