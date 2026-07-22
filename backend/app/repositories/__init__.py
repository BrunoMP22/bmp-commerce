"""Repositórios: ponte entre os modelos SQLAlchemy (app/models) e as entidades de
domínio puras (app/domain) — equivalente às implementações de
Infrastructure/Persistence/Repositories/*.cs do backend original."""

from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.venda_repository import VendaRepository

__all__ = [
    "ProdutoRepository",
    "ClienteRepository",
    "VendaRepository",
    "UsuarioRepository",
    "TenantRepository",
]
