"""Testes das regras do Motor de Insights — puros, sem banco.

Cada teste monta um InsightContext com objetos de domínio reais (Venda.registrar etc.)
e verifica a decisão da regra: dispara com a severidade certa ou fica em silêncio.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.domain.cliente import Cliente
from app.domain.enums import UnidadeMedida, UserRole
from app.domain.produto import Produto
from app.domain.usuario import Usuario
from app.domain.value_objects import Email
from app.domain.venda import Venda
from app.insights import InsightContext, Severidade, motor_padrao
from app.insights.rules import (
    ClientesSumidos,
    FaturamentoEmMovimento,
    PrevisaoDeRuptura,
    ProdutosEncalhados,
    VendasDeBalcao,
)

AGORA = datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc)


def fazer_usuario() -> Usuario:
    return Usuario(
        name="Vendedor",
        email=Email.create("vendedor@teste.com"),
        password_hash="hash",
        role=UserRole.SUPER_ADMIN,
        tenant_id=None,
    )


def fazer_produto(nome: str = "Produto", estoque: int = 1000, custo: str = "10", venda: str = "20") -> Produto:
    return Produto(
        nome=nome,
        sku=f"SKU-{nome[:10].upper()}",
        descricao=None,
        codigo_barras=None,
        categoria=None,
        unidade_medida=UnidadeMedida.UNIDADE,
        preco_custo=Decimal(custo),
        preco_venda=Decimal(venda),
        estoque_atual=estoque,
        estoque_minimo=1,
    )


def fazer_cliente(nome: str = "Cliente") -> Cliente:
    return Cliente(
        nome=nome, cpf_cnpj=None, telefone=None, email=None, cidade=None, estado=None, observacoes=None
    )


def fazer_venda(
    usuario: Usuario,
    produto: Produto,
    quantidade: int,
    dias_atras: int,
    cliente: Cliente | None = None,
) -> Venda:
    return Venda.registrar(usuario, cliente, [(produto, quantidade)], AGORA - timedelta(days=dias_atras))


def contexto(vendas: list[Venda], produtos: list[Produto] = [], clientes: list[Cliente] = []) -> InsightContext:
    return InsightContext(agora=AGORA, vendas=vendas, produtos=list(produtos), clientes=list(clientes))


# ---------------------------------------------------------------- faturamento


class TestFaturamentoEmMovimento:
    def test_alta_gera_oportunidade(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        vendas = [fazer_venda(usuario, produto, 10, dias_atras=5), fazer_venda(usuario, produto, 5, dias_atras=45)]

        insight = FaturamentoEmMovimento().avaliar(contexto(vendas))

        assert insight is not None
        assert insight.severidade == Severidade.OPORTUNIDADE
        assert insight.valor == Decimal("100")

    def test_queda_gera_alerta(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        vendas = [fazer_venda(usuario, produto, 5, dias_atras=5), fazer_venda(usuario, produto, 10, dias_atras=45)]

        insight = FaturamentoEmMovimento().avaliar(contexto(vendas))

        assert insight is not None
        assert insight.severidade == Severidade.ALERTA

    def test_sem_historico_fica_em_silencio(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        vendas = [fazer_venda(usuario, produto, 10, dias_atras=5)]

        assert FaturamentoEmMovimento().avaliar(contexto(vendas)) is None

    def test_venda_cancelada_nao_conta(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        atual = fazer_venda(usuario, produto, 10, dias_atras=5)
        atual.cancelar()
        anterior = fazer_venda(usuario, produto, 10, dias_atras=45)

        assert FaturamentoEmMovimento().avaliar(contexto([atual, anterior])) is None


# ------------------------------------------------------------------- estoque


class TestPrevisaoDeRuptura:
    def test_estoque_zerando_gera_alerta(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto(nome="Papel A4", estoque=40)
        vendas = [fazer_venda(usuario, produto, 30, dias_atras=10)]  # sobram 10; ~10 dias de estoque

        insight = PrevisaoDeRuptura().avaliar(contexto(vendas, produtos=[produto]))

        assert insight is not None
        assert insight.severidade == Severidade.ALERTA
        assert "Papel A4" in insight.mensagem
        assert insight.valor == Decimal("10")

    def test_estoque_folgado_fica_em_silencio(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto(estoque=1000)
        vendas = [fazer_venda(usuario, produto, 3, dias_atras=10)]

        assert PrevisaoDeRuptura().avaliar(contexto(vendas, produtos=[produto])) is None


class TestProdutosEncalhados:
    def test_produto_sem_venda_ha_60_dias_gera_alerta(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto(nome="Luminária")
        vendas = [fazer_venda(usuario, produto, 1, dias_atras=60)]

        insight = ProdutosEncalhados().avaliar(contexto(vendas, produtos=[produto]))

        assert insight is not None
        assert insight.severidade == Severidade.ALERTA
        assert "60 dias" in insight.mensagem

    def test_produto_que_nunca_vendeu_usa_data_de_cadastro(self) -> None:
        produto = fazer_produto(nome="Organizador")
        produto.created_at = AGORA - timedelta(days=75)

        insight = ProdutosEncalhados().avaliar(contexto([], produtos=[produto]))

        assert insight is not None
        assert "nunca vendeu" in insight.mensagem

    def test_produto_vendendo_fica_em_silencio(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        vendas = [fazer_venda(usuario, produto, 1, dias_atras=2)]

        assert ProdutosEncalhados().avaliar(contexto(vendas, produtos=[produto])) is None


# ------------------------------------------------------------------ clientes


class TestClientesSumidos:
    def test_cliente_sumido_gera_oportunidade(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        cliente = fazer_cliente("Ana")
        vendas = [fazer_venda(usuario, produto, 1, dias_atras=50, cliente=cliente)]

        insight = ClientesSumidos().avaliar(contexto(vendas, clientes=[cliente]))

        assert insight is not None
        assert insight.severidade == Severidade.OPORTUNIDADE
        assert "Ana" in insight.mensagem

    def test_cliente_recente_fica_em_silencio(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        cliente = fazer_cliente()
        vendas = [fazer_venda(usuario, produto, 1, dias_atras=10, cliente=cliente)]

        assert ClientesSumidos().avaliar(contexto(vendas, clientes=[cliente])) is None


class TestVendasDeBalcao:
    def test_metade_das_vendas_sem_cliente_gera_oportunidade(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto()
        cliente = fazer_cliente()
        vendas = [
            fazer_venda(usuario, produto, 1, dias_atras=dia, cliente=cliente if dia % 2 == 0 else None)
            for dia in range(6)
        ]

        insight = VendasDeBalcao().avaliar(contexto(vendas, clientes=[cliente]))

        assert insight is not None
        assert insight.valor == Decimal("50")


# --------------------------------------------------------------------- motor


class TestMotor:
    def _contexto_rico(self) -> InsightContext:
        usuario = fazer_usuario()
        produto = fazer_produto(estoque=10_000)
        vendas = [fazer_venda(usuario, produto, 10, dias_atras=5), fazer_venda(usuario, produto, 5, dias_atras=45)]
        return contexto(vendas, produtos=[produto])

    def test_funcionario_nao_recebe_insights_financeiros(self) -> None:
        motor = motor_padrao()

        para_admin = motor.executar(self._contexto_rico(), incluir_financeiros=True)
        para_funcionario = motor.executar(self._contexto_rico(), incluir_financeiros=False)

        assert any(insight.tipo == "faturamento-em-movimento" for insight in para_admin)
        assert not any(insight.tipo == "faturamento-em-movimento" for insight in para_funcionario)

    def test_ordena_alertas_antes_de_oportunidades_e_infos(self) -> None:
        usuario = fazer_usuario()
        produto = fazer_produto(nome="Girando", estoque=40)
        encalhado = fazer_produto(nome="Parado")
        encalhado.created_at = AGORA - timedelta(days=90)
        vendas = [
            fazer_venda(usuario, produto, 30, dias_atras=10),  # ruptura (alerta)
            fazer_venda(usuario, produto, 5, dias_atras=45),
        ]
        ctx = contexto(vendas, produtos=[produto, encalhado])

        insights = motor_padrao().executar(ctx, incluir_financeiros=True)

        severidades = [insight.severidade for insight in insights]
        assert severidades == sorted(
            severidades,
            key=lambda severidade: {Severidade.ALERTA: 0, Severidade.OPORTUNIDADE: 1, Severidade.INFO: 2}[severidade],
        )
        assert len(insights) >= 2
