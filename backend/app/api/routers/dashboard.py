"""Equivalente a API/Controllers/DashboardController.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import CurrentUserRole, DashboardServiceDep, get_current_user_id
from app.schemas.dashboard import DashboardDto

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=DashboardDto)
def obter(dashboard_service: DashboardServiceDep, role: CurrentUserRole) -> DashboardDto:
    # Dashboard por papel (Doc 02 §6.1): Funcionário recebe a versão sem financeiro,
    # decidida no back-end — nunca só escondida na tela.
    return dashboard_service.obter_dashboard(role)
