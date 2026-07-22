from app.api.routers.auth import router as auth_router
from app.api.routers.clientes import router as clientes_router
from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.produtos import router as produtos_router
from app.api.routers.vendas import router as vendas_router

__all__ = [
    "auth_router",
    "produtos_router",
    "clientes_router",
    "vendas_router",
    "dashboard_router",
]
