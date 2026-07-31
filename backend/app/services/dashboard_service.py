"""Dashboard executivo — leitura agregada de Operations (contexto Insights, ADR 0004:
lê, nunca escreve; cálculo on-read em memória, volume por tenant baixo no MVP).

KPIs de janela usam 30 dias móveis vs os 30 anteriores — a mesma régua do Motor de
Insights, para o dashboard e a aba Insights nunca discordarem sobre "crescimento".
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_EVEN, Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.produto import Produto
from app.domain.venda import Venda
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.dashboard import (
    CategoriaReceitaDto,
    DashboardDto,
    KpiComVariacaoDto,
    ProdutoEstoqueAlertaDto,
    TopProdutoDto,
    UltimaVendaDto,
    VendaPorDiaDto,
)

_DIAS_DO_GRAFICO = 30
_DIAS_JANELA = 30
_LIMITE_TOP_PRODUTOS = 5
_LIMITE_ULTIMAS_VENDAS = 6
_LIMITE_ESTOQUE_ALERTA = 6
_LIMITE_CATEGORIAS = 3  # top 3 + "Outras" — teto validado da paleta categórica
_SEM_CATEGORIA = "Sem categoria"
_OUTRAS = "Outras"


def _dois_decimais(valor: Decimal) -> Decimal:
    # Math.Round(x, 2) do C# usa banker's rounding (ToEven) por padrão.
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def _receita(vendas: list[Venda]) -> Decimal:
    return sum((venda.total for venda in vendas), Decimal("0"))


def _kpi(atual: Decimal, anterior: Decimal) -> KpiComVariacaoDto:
    variacao = float((atual - anterior) / anterior * 100) if anterior > 0 else None
    return KpiComVariacaoDto(atual=float(atual), anterior=float(anterior), variacao_percentual=variacao)


class DashboardService:
    def __init__(self, session: Session) -> None:
        self._vendas = VendaRepository(session)
        self._produtos = ProdutoRepository(session)
        self._clientes = ClienteRepository(session)

    def obter_dashboard(self) -> DashboardDto:
        vendas = self._vendas.get_all()
        produtos = self._produtos.get_all(search=None)
        clientes = self._clientes.get_all()

        agora = datetime.now(timezone.utc)
        vendas_validas = [venda for venda in vendas if not venda.is_deleted]

        inicio_janela = agora - timedelta(days=_DIAS_JANELA)
        inicio_janela_anterior = agora - timedelta(days=2 * _DIAS_JANELA)
        janela_atual = [v for v in vendas_validas if v.data_hora >= inicio_janela]
        janela_anterior = [
            v for v in vendas_validas if inicio_janela_anterior <= v.data_hora < inicio_janela
        ]

        receita_atual = _receita(janela_atual)
        receita_anterior = _receita(janela_anterior)

        ticket_atual = (
            _dois_decimais(receita_atual / len(janela_atual)) if janela_atual else Decimal("0")
        )
        ticket_anterior = (
            _dois_decimais(receita_anterior / len(janela_anterior)) if janela_anterior else Decimal("0")
        )

        receita_total = _receita(vendas_validas)
        valor_estoque = sum(
            (produto.preco_custo * produto.estoque_atual for produto in produtos), Decimal("0")
        )

        hoje = agora.date()
        inicio_grafico = hoje - timedelta(days=_DIAS_DO_GRAFICO - 1)
        vendas_por_dia = [
            self._resumo_do_dia(inicio_grafico + timedelta(days=offset), vendas_validas)
            for offset in range(_DIAS_DO_GRAFICO)
        ]

        return DashboardDto(
            receita_30_dias=_kpi(receita_atual, receita_anterior),
            vendas_30_dias=_kpi(Decimal(len(janela_atual)), Decimal(len(janela_anterior))),
            ticket_medio_30_dias=_kpi(ticket_atual, ticket_anterior),
            valor_estoque=float(valor_estoque),
            receita_total=float(receita_total),
            quantidade_vendas=len(vendas_validas),
            clientes_cadastrados=len(clientes),
            produtos_cadastrados=len(produtos),
            produtos_abaixo_minimo=sum(
                1 for produto in produtos if 0 < produto.estoque_atual < produto.estoque_minimo
            ),
            produtos_sem_estoque=sum(1 for produto in produtos if produto.estoque_atual == 0),
            vendas_por_dia=vendas_por_dia,
            receita_por_categoria=self._receita_por_categoria(janela_atual, produtos),
            top_produtos=self._top_produtos(janela_atual),
            ultimas_vendas=self._ultimas_vendas(vendas),
            estoque_em_alerta=self._estoque_em_alerta(produtos),
        )

    @staticmethod
    def _resumo_do_dia(dia: date, vendas_validas: list[Venda]) -> VendaPorDiaDto:
        vendas_do_dia = [venda for venda in vendas_validas if venda.data_hora.date() == dia]
        return VendaPorDiaDto(
            data=dia,
            total=float(_receita(vendas_do_dia)),
            quantidade=len(vendas_do_dia),
        )

    @staticmethod
    def _receita_por_categoria(
        janela_atual: list[Venda], produtos: list[Produto]
    ) -> list[CategoriaReceitaDto]:
        categoria_por_produto: dict[UUID, str] = {
            produto.id: produto.categoria or _SEM_CATEGORIA for produto in produtos
        }

        receita_por_categoria: dict[str, Decimal] = {}
        for venda in janela_atual:
            for item in venda.itens:
                categoria = categoria_por_produto.get(item.produto_id, _SEM_CATEGORIA)
                receita_por_categoria[categoria] = (
                    receita_por_categoria.get(categoria, Decimal("0")) + item.subtotal
                )

        total = sum(receita_por_categoria.values(), Decimal("0"))
        if total <= 0:
            return []

        ordenadas = sorted(receita_por_categoria.items(), key=lambda par: par[1], reverse=True)
        principais = ordenadas[:_LIMITE_CATEGORIAS]
        resto = ordenadas[_LIMITE_CATEGORIAS:]
        if resto:
            principais.append((_OUTRAS, sum((valor for _, valor in resto), Decimal("0"))))

        return [
            CategoriaReceitaDto(
                categoria=categoria,
                receita=float(valor),
                participacao_percentual=float(valor / total * 100),
            )
            for categoria, valor in principais
        ]

    @staticmethod
    def _top_produtos(janela_atual: list[Venda]) -> list[TopProdutoDto]:
        acumulado: dict[UUID, tuple[str, str, int, Decimal]] = {}
        for venda in janela_atual:
            for item in venda.itens:
                nome, sku, quantidade, receita = acumulado.get(
                    item.produto_id, (item.produto_nome, item.produto_sku, 0, Decimal("0"))
                )
                acumulado[item.produto_id] = (
                    nome,
                    sku,
                    quantidade + item.quantidade,
                    receita + item.subtotal,
                )

        ordenados = sorted(acumulado.items(), key=lambda par: par[1][3], reverse=True)
        return [
            TopProdutoDto(
                produto_id=produto_id, nome=nome, sku=sku, quantidade=quantidade, receita=float(receita)
            )
            for produto_id, (nome, sku, quantidade, receita) in ordenados[:_LIMITE_TOP_PRODUTOS]
        ]

    @staticmethod
    def _ultimas_vendas(vendas: list[Venda]) -> list[UltimaVendaDto]:
        # Inclui canceladas (com o flag): o dashboard mostra a operação como ela é.
        recentes = sorted(vendas, key=lambda venda: venda.data_hora, reverse=True)
        return [
            UltimaVendaDto(
                id=venda.id,
                cliente_nome=venda.cliente_nome,
                data_hora=venda.data_hora,
                total=float(venda.total),
                quantidade_itens=sum(item.quantidade for item in venda.itens),
                cancelada=venda.is_deleted,
            )
            for venda in recentes[:_LIMITE_ULTIMAS_VENDAS]
        ]

    @staticmethod
    def _estoque_em_alerta(produtos: list[Produto]) -> list[ProdutoEstoqueAlertaDto]:
        em_alerta = [
            produto
            for produto in produtos
            if produto.ativo and produto.estoque_atual < produto.estoque_minimo
        ]
        # Sem estoque primeiro; depois os mais próximos de zerar.
        em_alerta.sort(key=lambda produto: (produto.estoque_atual > 0, produto.estoque_atual))
        return [
            ProdutoEstoqueAlertaDto(
                produto_id=produto.id,
                nome=produto.nome,
                sku=produto.sku,
                estoque_atual=produto.estoque_atual,
                estoque_minimo=produto.estoque_minimo,
                sem_estoque=produto.estoque_atual == 0,
            )
            for produto in em_alerta[:_LIMITE_ESTOQUE_ALERTA]
        ]
