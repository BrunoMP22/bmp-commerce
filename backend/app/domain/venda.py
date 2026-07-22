"""Equivalente a Domain/Entities/Venda.cs + Domain/Entities/ItemVenda.cs — o agregado
DDD real do domínio (Doc 01 §6, Doc 02 §3.6).

Toda venda nasce completa pela factory `Venda.registrar()`, que garante as invariantes:
  INV 1: venda tem ao menos 1 item
  INV 2: quantidade de cada item > 0
  INV 3: preço/custo congelados no item no momento da venda
  INV 4: total = soma dos subtotais
  INV 5: estoque insuficiente em qualquer item bloqueia a venda inteira
  INV 6: venda nunca é deletada fisicamente (soft delete via cancelar())
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.exceptions import DomainException
from app.domain.common import Entity

if TYPE_CHECKING:
    from app.domain.cliente import Cliente
    from app.domain.produto import Produto
    from app.domain.usuario import Usuario


class ItemVenda(Entity):
    """Parte do agregado Venda — só deve ser criado por dentro de `Venda.registrar()`.
    Preço, custo, nome e SKU são CONGELADOS no momento da venda (Doc 01 REGRA 3): se o
    produto mudar depois, o histórico e a margem desta venda não mudam."""

    def __init__(self, venda_id: UUID, produto: Produto, quantidade: int) -> None:
        if quantidade <= 0:
            raise DomainException("Quantidade de cada item deve ser maior que zero.")

        self._init_entity()
        self.venda_id = venda_id
        self.produto_id = produto.id
        self.produto_nome = produto.nome
        self.produto_sku = produto.sku
        self.quantidade = quantidade
        self.preco_venda_momento = produto.preco_venda
        self.preco_custo_momento = produto.preco_custo
        self.subtotal = Decimal(quantidade) * produto.preco_venda

    @classmethod
    def from_persistence(cls, **kwargs) -> ItemVenda:
        obj = cls.__new__(cls)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj


class Venda(Entity):
    def __init__(self) -> None:
        # Uso interno — instâncias só devem vir de `Venda.registrar()` ou `from_persistence()`.
        self._itens: list[ItemVenda] = []
        self.total: Decimal = Decimal("0")
        self.is_deleted: bool = False
        self.version: int = 1

    @property
    def itens(self) -> list[ItemVenda]:
        return list(self._itens)

    @staticmethod
    def registrar(
        usuario: Usuario,
        cliente: Cliente | None,
        itens: list[tuple[Produto, int]],
        data_hora: datetime | None = None,
    ) -> Venda:
        if usuario is None:
            raise DomainException("Usuário responsável pela venda é obrigatório.")

        if cliente is not None and not cliente.ativo:
            raise DomainException(f"Cliente '{cliente.nome}' está inativo e não pode ser vinculado a uma venda.")

        if not itens:
            raise DomainException("Venda deve ter ao menos um item.")

        venda = Venda()
        venda._init_entity()
        venda.usuario_id = usuario.id
        venda.usuario_nome = usuario.name
        venda.cliente_id = cliente.id if cliente else None
        venda.cliente_nome = cliente.nome if cliente else None
        venda.data_hora = data_hora if data_hora is not None else datetime.now(timezone.utc)

        # Valida TUDO antes de debitar qualquer estoque: estoque insuficiente em
        # qualquer item bloqueia a venda inteira, nada é baixado (INV 5).
        for produto, quantidade in itens:
            if quantidade <= 0:
                raise DomainException("Quantidade de cada item deve ser maior que zero.")

            if not produto.ativo:
                raise DomainException(f"Produto '{produto.nome}' está inativo e não pode ser vendido.")

            if produto.estoque_atual < quantidade:
                raise DomainException(
                    f"Estoque insuficiente para o produto '{produto.nome}'. "
                    f"Disponível: {produto.estoque_atual}, solicitado: {quantidade}."
                )

        for produto, quantidade in itens:
            produto.baixar_estoque(quantidade)
            item = ItemVenda(venda.id, produto, quantidade)
            venda._itens.append(item)
            venda.total += item.subtotal

        return venda

    def cancelar(self) -> None:
        """Soft delete (INV 6): a venda permanece no histórico como cancelada. O estorno
        de estoque dos itens é orquestrado pelo VendaService, na mesma transação."""
        if self.is_deleted:
            raise DomainException("Venda já está cancelada.")

        self.is_deleted = True
        self.mark_as_updated()

    @classmethod
    def from_persistence(cls, *, itens: list[ItemVenda], **kwargs) -> Venda:
        obj = cls.__new__(cls)
        obj._itens = list(itens)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
