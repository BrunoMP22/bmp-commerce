"""Fixtures compartilhadas dos testes.

Os testes de integração rodam contra um SQL Server real (BMPCommerceTestDb), não
SQLite: o objetivo desta migração é fidelidade de comportamento com o backend C#
original (inclusive nuances do dialeto T-SQL, como a própria descoberta do bug de
`ON DELETE RESTRICT` durante a migration — algo que um SQLite in-memory não teria
pegado). Cada teste roda dentro de uma transação que é revertida no final
(`join_transaction_mode="create_savepoint"`), então nunca precisa recriar o schema.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ["DATABASE_URL"] = (
    "mssql+pyodbc://localhost/BMPCommerceTestDb"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_token, hash_password
from app.database import get_db
from app.domain.enums import UserRole
from app.domain.usuario import Usuario
from app.domain.value_objects import Email
from app.models import Base
from app.repositories.usuario_repository import UsuarioRepository


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    eng = create_engine(settings.database_url)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    from app.main import app

    def _override_get_db() -> Iterator[Session]:
        # Precisa ser uma função geradora de verdade (com `yield`): o FastAPI só entra
        # no modo "dependência yield" (chamando `next()`/tratando cleanup) quando
        # detecta isso via `inspect.isgeneratorfunction` — uma lambda retornando um
        # iterador pronto não é reconhecida e o iterador acaba injetado como valor.
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Sem `with TestClient(app) as ...`: usar como context manager dispara o lifespan
    # (inclusive `seed_database`), que rodaria fora da transação/rollback deste fixture
    # e sujaria BMPCommerceTestDb permanentemente. Sem o `with`, nenhum evento de
    # startup/shutdown roda — os testes só precisam das rotas, não do seed de demo.
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def admin_usuario(db_session: Session) -> Usuario:
    usuario = Usuario(
        name="Admin Teste",
        email=Email.create("admin.teste@bmpcommerce.com"),
        password_hash=hash_password("Senha@123"),
        role=UserRole.SUPER_ADMIN,
        tenant_id=None,
    )
    UsuarioRepository(db_session).add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture()
def auth_headers(admin_usuario: Usuario) -> dict[str, str]:
    token = generate_token(
        user_id=admin_usuario.id,
        name=admin_usuario.name,
        email=admin_usuario.email.value,
        role=admin_usuario.role.value,
        tenant_id=admin_usuario.tenant_id,
    )
    return {"Authorization": f"Bearer {token}"}
