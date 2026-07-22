"""Equivalente a Application/Insights/Dashboard/DashboardService.cs.

Contexto Insights (ADR 0004): LÊ dos dados de Operations, nunca escreve. Cálculo on-read
em memória — volume por tenant é baixo no MVP; a troca por queries agregadas/pré-cálculo
acontece atrás deste mesmo contrato.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_EVEN, Decimal

from sqlalchemy.orm import Session

from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.dashboard import DashboardDto, VendaPorDiaDto

_DIAS_DO_GRAFICO = 14


class DashboardService:
    def __init__(self, session: Session) -> None:
        self._vendas = VendaRepository(session)
        self._produtos = ProdutoRepository(session)
        self._clientes = ClienteRepository(session)

    def obter_dashboard(self) -> DashboardDto:
        vendas = self._vendas.get_all()
        produtos = self._produtos.get_all(search=None)
        clientes = self._clientes.get_all()

        vendas_validas = [venda for venda in vendas if not venda.is_deleted]

        receita_total = sum((venda.total for venda in vendas_validas), Decimal("0"))
        quantidade_vendas = len(vendas_validas)
        ticket_medio = (
            # Math.Round(x, 2) do C# usa banker's rounding (ToEven) por padrão.
            (receita_total / quantidade_vendas).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            if quantidade_vendas > 0
            else Decimal("0")
        )
        valor_estoque = sum((produto.preco_custo * produto.estoque_atual for produto in produtos), Decimal("0"))

        hoje = datetime.now(timezone.utc).date()
        inicio_janela = hoje - timedelta(days=_DIAS_DO_GRAFICO - 1)

        vendas_por_dia = [
            self._resumo_do_dia(inicio_janela + timedelta(days=offset), vendas_validas)
            for offset in range(_DIAS_DO_GRAFICO)
        ]

        return DashboardDto(
            receita_total=receita_total,
            quantidade_vendas=quantidade_vendas,
            clientes_cadastrados=len(clientes),
            produtos_cadastrados=len(produtos),
            produtos_abaixo_minimo=sum(
                1 for produto in produtos if 0 < produto.estoque_atual < produto.estoque_minimo
            ),
            produtos_sem_estoque=sum(1 for produto in produtos if produto.estoque_atual == 0),
            ticket_medio=ticket_medio,
            valor_estoque=valor_estoque,
            vendas_por_dia=vendas_por_dia,
        )

    @staticmethod
    def _resumo_do_dia(dia: date, vendas_validas: list) -> VendaPorDiaDto:
        vendas_do_dia = [venda for venda in vendas_validas if venda.data_hora.date() == dia]
        return VendaPorDiaDto(
            data=dia,
            total=sum((venda.total for venda in vendas_do_dia), Decimal("0")),
            quantidade=len(vendas_do_dia),
        )
