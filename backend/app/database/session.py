"""Engine e fábrica de sessões SQLAlchemy — equivalente ao registro do
`BMPCommerceDbContext` em Infrastructure/DependencyInjection.cs."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Uma sessão por requisição (equivalente ao DbContext com `Scoped` lifetime do
    ASP.NET Core): commit fica a cargo de cada service, aqui só garante rollback em caso
    de exceção não tratada e o fechamento da conexão ao final."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
