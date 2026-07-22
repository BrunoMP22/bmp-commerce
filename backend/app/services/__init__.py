"""Serviços de aplicação — equivalente a Application/Operations/*/**Service.cs e
Application/Insights/Dashboard/DashboardService.cs do backend original."""

from app.services.auth_service import AuthService
from app.services.cliente_service import ClienteService
from app.services.dashboard_service import DashboardService
from app.services.produto_service import ProdutoService
from app.services.venda_service import VendaService

__all__ = [
    "AuthService",
    "ProdutoService",
    "ClienteService",
    "VendaService",
    "DashboardService",
]
