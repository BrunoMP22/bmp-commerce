"""Fábricas de serviço por requisição — equivalente ao `AddScoped<IXxxService, XxxService>`
de Application/DependencyInjection/DependencyInjection.cs do backend original."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import AuthService, ClienteService, DashboardService, ProdutoService, VendaService

DbSession = Annotated[Session, Depends(get_db)]


def get_auth_service(session: DbSession) -> AuthService:
    return AuthService(session)


def get_produto_service(session: DbSession) -> ProdutoService:
    return ProdutoService(session)


def get_cliente_service(session: DbSession) -> ClienteService:
    return ClienteService(session)


def get_venda_service(session: DbSession) -> VendaService:
    return VendaService(session)


def get_dashboard_service(session: DbSession) -> DashboardService:
    return DashboardService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ProdutoServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]
ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]
VendaServiceDep = Annotated[VendaService, Depends(get_venda_service)]
DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
