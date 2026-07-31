"""Endpoint da área de Insights — as frases de negócio do tenant."""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import CurrentUserRole, InsightsServiceDep
from app.schemas.insight import InsightsDto

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("", response_model=InsightsDto)
def obter(insights_service: InsightsServiceDep, role: CurrentUserRole) -> InsightsDto:
    return insights_service.obter_insights(role)
