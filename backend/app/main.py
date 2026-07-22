"""Ponto de entrada da aplicação — equivalente a API/Program.cs."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth_router, clientes_router, dashboard_router, produtos_router, vendas_router
from app.core.config import settings
from app.database import SessionLocal, seed_database
from app.middleware import register_exception_handlers

# Mesma política do Program.cs original (`SetIsOriginAllowed`): qualquer origem
# localhost/127.0.0.1, em qualquer porta — cobre o Vite dev server independente da
# porta escolhida.
_CORS_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Em desenvolvimento, popula o banco com dados de demonstração no boot — equivalente
    # ao bloco `if (app.Environment.IsDevelopment())` do Program.cs original. As
    # migrations em si já são aplicadas via `alembic upgrade head` (não é seguro rodar
    # DDL concorrente no boot de múltiplos workers Uvicorn).
    if settings.is_development:
        with SessionLocal() as session:
            seed_database(session)

    yield


app = FastAPI(
    title="BMP Commerce API",
    version="v1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=_CORS_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(produtos_router)
app.include_router(clientes_router)
app.include_router(vendas_router)
app.include_router(dashboard_router)
