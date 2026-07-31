"""Contrato HTTP do dashboard executivo.

KPIs principais usam janelas móveis de 30 dias com variação vs os 30 dias
anteriores (mesma régua do Motor de Insights — nunca mês parcial vs mês fechado).
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
    total: float
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
    receita: float


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
    receita_30_dias: KpiComVariacaoDto
    vendas_30_dias: KpiComVariacaoDto
    ticket_medio_30_dias: KpiComVariacaoDto
    valor_estoque: float

    # Totais gerais (histórico completo).
    receita_total: float
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
