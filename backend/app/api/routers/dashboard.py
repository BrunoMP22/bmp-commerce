"""Equivalente a API/Controllers/DashboardController.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import DashboardServiceDep, get_current_user_id
from app.schemas.dashboard import DashboardDto

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=DashboardDto)
def obter(dashboard_service: DashboardServiceDep) -> DashboardDto:
    return dashboard_service.obter_dashboard()
