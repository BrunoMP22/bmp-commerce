"""Equivalente a API/Controllers/VendasController.cs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import CurrentUserId, VendaServiceDep, get_current_user_id
from app.schemas.venda import RegistrarVendaRequest, VendaDto

router = APIRouter(prefix="/api/vendas", tags=["Vendas"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=list[VendaDto])
def listar(venda_service: VendaServiceDep) -> list[VendaDto]:
    return venda_service.listar()


@router.get("/{venda_id}", response_model=VendaDto)
def obter_por_id(venda_id: UUID, venda_service: VendaServiceDep) -> VendaDto:
    return venda_service.obter_por_id(venda_id)


@router.post("", response_model=VendaDto, status_code=status.HTTP_201_CREATED)
def registrar(
    request: RegistrarVendaRequest,
    venda_service: VendaServiceDep,
    user_id: CurrentUserId,
    response: Response,
) -> VendaDto:
    venda = venda_service.registrar(request, user_id)
    response.headers["Location"] = f"/api/vendas/{venda.id}"
    return venda


# Cancelamento é soft delete (Doc 01 REGRA 4) com estorno de estoque — a venda
# permanece no histórico como cancelada.
@router.post("/{venda_id}/cancelar", response_model=VendaDto)
def cancelar(venda_id: UUID, venda_service: VendaServiceDep) -> VendaDto:
    return venda_service.cancelar(venda_id)
