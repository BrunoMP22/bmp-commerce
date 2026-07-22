import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(50), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unidade_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    estoque_atual: Mapped[int] = mapped_column(Integer, nullable=False)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Concorrência otimista (equivalente ao RowVersion do SQL Server no schema original) —
    # o SQLAlchemy incrementa e checa este contador automaticamente a cada UPDATE.
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __mapper_args__ = {"version_id_col": version}
