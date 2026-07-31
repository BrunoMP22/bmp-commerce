"""Schemas Pydantic (contrato HTTP camelCase) — equivalente aos records DTO de
Application/Operations/*/**Dtos.cs do backend original."""

from app.schemas.auth import (
    AlterarSenhaRequest,
    AtualizarAvatarRequest,
    AtualizarPerfilRequest,
    AuthenticatedUserResult,
    LoginRequest,
    LoginResult,
)
from app.schemas.cliente import AtualizarClienteRequest, ClienteDto, CriarClienteRequest
from app.schemas.dashboard import (
    CategoriaReceitaDto,
    DashboardDto,
    KpiComVariacaoDto,
    ProdutoEstoqueAlertaDto,
    TopProdutoDto,
    UltimaVendaDto,
    VendaPorDiaDto,
)
from app.schemas.insight import InsightDto, InsightsDto, ResumoInsightsDto
from app.schemas.produto import AtualizarProdutoRequest, CriarProdutoRequest, ProdutoDto
from app.schemas.venda import ItemVendaDto, ItemVendaRequest, RegistrarVendaRequest, VendaDto

__all__ = [
    "LoginRequest",
    "AuthenticatedUserResult",
    "LoginResult",
    "AlterarSenhaRequest",
    "AtualizarPerfilRequest",
    "AtualizarAvatarRequest",
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
    "KpiComVariacaoDto",
    "CategoriaReceitaDto",
    "TopProdutoDto",
    "UltimaVendaDto",
    "ProdutoEstoqueAlertaDto",
    "InsightDto",
    "ResumoInsightsDto",
    "InsightsDto",
]
