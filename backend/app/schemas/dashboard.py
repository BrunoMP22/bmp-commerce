"""Contrato HTTP do dashboard executivo.

KPIs principais usam janelas móveis de 30 dias com variação vs os 30 dias
anteriores (mesma régua do Motor de Insights — nunca mês parcial vs mês fechado).

Dashboard por papel (Doc 02 §6.1, ADR 0004): para Funcionário os campos
financeiros vêm como None/vazios — o bloqueio é no back-end, nunca só na tela.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from app.schemas.common import CamelModel


class KpiComVariacaoDto(CamelModel):
    atual: float
    anterior: float
    # None quando não há base de comparação (janela anterior zerada).
    variacao_percentual: float | None


class VendaPorDiaDto(CamelModel):
    data: date
    # None para Funcionário (receita é financeira); quantidade é operacional.
    total: float | None
    quantidade: int


class CategoriaReceitaDto(CamelModel):
    categoria: str
    receita: float
    participacao_percentual: float


class TopProdutoDto(CamelModel):
    produto_id: UUID
    nome: str
    sku: str
    quantidade: int
    # None para Funcionário — o ranking dele é por unidades vendidas.
    receita: float | None


class UltimaVendaDto(CamelModel):
    id: UUID
    cliente_nome: str | None
    data_hora: datetime
    total: float
    quantidade_itens: int
    cancelada: bool


class ProdutoEstoqueAlertaDto(CamelModel):
    produto_id: UUID
    nome: str
    sku: str
    estoque_atual: int
    estoque_minimo: int
    sem_estoque: bool


class DashboardDto(CamelModel):
    # KPIs de janela: últimos 30 dias vs 30 dias anteriores.
    # Os financeiros são None para Funcionário.
    receita_30_dias: KpiComVariacaoDto | None
    vendas_30_dias: KpiComVariacaoDto
    ticket_medio_30_dias: KpiComVariacaoDto | None
    valor_estoque: float | None

    # Totais gerais (histórico completo).
    receita_total: float | None
    quantidade_vendas: int
    clientes_cadastrados: int
    produtos_cadastrados: int
    produtos_abaixo_minimo: int
    produtos_sem_estoque: int

    vendas_por_dia: list[VendaPorDiaDto]
    receita_por_categoria: list[CategoriaReceitaDto]
    top_produtos: list[TopProdutoDto]
    ultimas_vendas: list[UltimaVendaDto]
    estoque_em_alerta: list[ProdutoEstoqueAlertaDto]
