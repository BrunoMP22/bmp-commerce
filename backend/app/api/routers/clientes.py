"""Equivalente a API/Controllers/ClientesController.cs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import ClienteServiceDep, get_current_user_id
from app.schemas.cliente import AtualizarClienteRequest, ClienteDto, CriarClienteRequest

router = APIRouter(prefix="/api/clientes", tags=["Clientes"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=list[ClienteDto])
def listar(cliente_service: ClienteServiceDep) -> list[ClienteDto]:
    return cliente_service.listar()


@router.get("/{cliente_id}", response_model=ClienteDto)
def obter_por_id(cliente_id: UUID, cliente_service: ClienteServiceDep) -> ClienteDto:
    return cliente_service.obter_por_id(cliente_id)


@router.post("", response_model=ClienteDto, status_code=status.HTTP_201_CREATED)
def criar(request: CriarClienteRequest, cliente_service: ClienteServiceDep, response: Response) -> ClienteDto:
    cliente = cliente_service.criar(request)
    response.headers["Location"] = f"/api/clientes/{cliente.id}"
    return cliente


@router.put("/{cliente_id}", response_model=ClienteDto)
def atualizar(
    cliente_id: UUID, request: AtualizarClienteRequest, cliente_service: ClienteServiceDep
) -> ClienteDto:
    return cliente_service.atualizar(cliente_id, request)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def excluir(cliente_id: UUID, cliente_service: ClienteServiceDep) -> None:
    result = cliente_service.excluir(cliente_id)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)
