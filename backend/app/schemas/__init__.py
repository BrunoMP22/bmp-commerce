"""Schemas Pydantic (contrato HTTP camelCase) — equivalente aos records DTO de
Application/Operations/*/**Dtos.cs do backend original."""

from app.schemas.auth import AuthenticatedUserResult, LoginRequest, LoginResult
from app.schemas.cliente import AtualizarClienteRequest, ClienteDto, CriarClienteRequest
from app.schemas.dashboard import DashboardDto, VendaPorDiaDto
from app.schemas.produto import AtualizarProdutoRequest, CriarProdutoRequest, ProdutoDto
from app.schemas.venda import ItemVendaDto, ItemVendaRequest, RegistrarVendaRequest, VendaDto

__all__ = [
    "LoginRequest",
    "AuthenticatedUserResult",
    "LoginResult",
    "ProdutoDto",
    "CriarProdutoRequest",
    "AtualizarProdutoRequest",
    "ClienteDto",
    "CriarClienteRequest",
    "AtualizarClienteRequest",
    "ItemVendaRequest",
    "RegistrarVendaRequest",
    "ItemVendaDto",
    "VendaDto",
    "VendaPorDiaDto",
    "DashboardDto",
]
