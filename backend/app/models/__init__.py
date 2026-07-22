"""Modelos SQLAlchemy (mapeamento de persistência — equivalente a
Infrastructure/Persistence/Configurations/*.cs do backend original).

Importar todos aqui garante que `Base.metadata` os conheça (usado pelo Alembic e por
qualquer `create_all` de teste).
"""

from app.models.base import Base
from app.models.cliente import ClienteModel
from app.models.produto import ProdutoModel
from app.models.tenant import TenantModel
from app.models.usuario import UsuarioModel
from app.models.venda import ItemVendaModel, VendaModel

__all__ = [
    "Base",
    "TenantModel",
    "UsuarioModel",
    "ProdutoModel",
    "ClienteModel",
    "VendaModel",
    "ItemVendaModel",
]
