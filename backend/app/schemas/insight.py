"""Contrato HTTP da área de Insights (camelCase, como todos os schemas)."""

from __future__ import annotations

from datetime import datetime

from app.schemas.common import CamelModel


class InsightDto(CamelModel):
    tipo: str
    severidade: str
    titulo: str
    mensagem: str
    destaque: str | None
    acao: str | None
    valor: float | None


class ResumoInsightsDto(CamelModel):
    alertas: int
    oportunidades: int
    informativos: int


class InsightsDto(CamelModel):
    gerado_em: datetime
    resumo: ResumoInsightsDto
    insights: list[InsightDto]
