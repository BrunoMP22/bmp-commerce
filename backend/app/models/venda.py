import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VendaModel(Base):
    __tablename__ = "vendas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    # Sem `ondelete`: ver nota em app/models/usuario.py sobre RESTRICT não existir no
    # dialeto T-SQL — o padrão (NO ACTION) já bloqueia o DELETE se houver referências.
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("clientes.id"), nullable=True, index=True
    )
    cliente_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False, index=True
    )
    usuario_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    itens: Mapped[list["ItemVendaModel"]] = relationship(
        back_populates="venda", cascade="all, delete-orphan", lazy="selectin"
    )

    __mapper_args__ = {"version_id_col": version}


class ItemVendaModel(Base):
    __tablename__ = "itens_venda"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    venda_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendas.id", ondelete="CASCADE"), nullable=False)
    produto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("produtos.id"), nullable=False, index=True)
    produto_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    produto_sku: Mapped[str] = mapped_column(String(50), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_venda_momento: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    preco_custo_momento: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    venda: Mapped["VendaModel"] = relationship(back_populates="itens")
