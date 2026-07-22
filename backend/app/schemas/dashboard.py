"""Equivalente a Application/Insights/Dashboard/DashboardDtos.cs."""

from __future__ import annotations

from datetime import date

from app.schemas.common import CamelModel


class VendaPorDiaDto(CamelModel):
    data: date
    total: float
    quantidade: int


class DashboardDto(CamelModel):
    receita_total: float
    quantidade_vendas: int
    clientes_cadastrados: int
    produtos_cadastrados: int
    produtos_abaixo_minimo: int
    produtos_sem_estoque: int
    ticket_medio: float
    valor_estoque: float
    vendas_por_dia: list[VendaPorDiaDto]
