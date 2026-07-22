"""Equivalente a Infrastructure/Persistence/Repositories/ProdutoRepository.cs.

Ponte entre `ProdutoModel` (ORM, mapeamento burro) e `Produto` (domínio, puro). No C#
original a entidade de domínio E a entidade do EF Core eram o mesmo objeto, então o
change-tracker do EF persistia mutações automaticamente. Aqui os dois são objetos
distintos, então todo método que muta um `Produto` já carregado precisa terminar com
uma chamada a `update()` para copiar o novo estado de volta no `ProdutoModel` rastreado
pela sessão — é essa chamada que faz o UPDATE (via `session.flush()`/commit) sair no
lugar certo.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.domain.enums import UnidadeMedida
from app.domain.produto import Produto
from app.models.base import to_aware_utc, to_naive_utc
from app.models.produto import ProdutoModel


def _to_domain(model: ProdutoModel) -> Produto:
    return Produto.from_persistence(
        id=model.id,
        nome=model.nome,
        descricao=model.descricao,
        sku=model.sku,
        codigo_barras=model.codigo_barras,
        categoria=model.categoria,
        unidade_medida=UnidadeMedida(model.unidade_medida),
        preco_custo=model.preco_custo,
        preco_venda=model.preco_venda,
        estoque_atual=model.estoque_atual,
        estoque_minimo=model.estoque_minimo,
        ativo=model.ativo,
        version=model.version,
        created_at=to_aware_utc(model.created_at),
        updated_at=to_aware_utc(model.updated_at),
    )


def _like_pattern(termo: str) -> str:
    """Escapa curingas de LIKE (%, _, [) para que uma busca por "50%" ou "a_b" não vire
    um padrão. Mesmo comportamento que o EF Core aplica ao traduzir `string.Contains`."""
    escaped = termo.replace("~", "~~").replace("%", "~%").replace("_", "~_").replace("[", "~[")
    return f"%{escaped}%"


class ProdutoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, produto_id: uuid.UUID) -> Produto | None:
        model = self._session.get(ProdutoModel, produto_id)
        return _to_domain(model) if model is not None else None

    def get_all(self, search: str | None) -> list[Produto]:
        query = self._session.query(ProdutoModel)

        if search is not None and search.strip():
            pattern = _like_pattern(search.strip())
            query = query.filter(
                ProdutoModel.nome.like(pattern, escape="~") | ProdutoModel.sku.like(pattern, escape="~")
            )

        query = query.order_by(ProdutoModel.nome)
        return [_to_domain(model) for model in query.all()]

    def existe_sku(self, sku: str, ignorar_id: uuid.UUID | None) -> bool:
        query = self._session.query(ProdutoModel.id).filter(ProdutoModel.sku == sku)

        if ignorar_id is not None:
            query = query.filter(ProdutoModel.id != ignorar_id)

        return query.first() is not None

    def add(self, produto: Produto) -> None:
        model = ProdutoModel(
            id=produto.id,
            nome=produto.nome,
            descricao=produto.descricao,
            sku=produto.sku,
            codigo_barras=produto.codigo_barras,
            categoria=produto.categoria,
            unidade_medida=produto.unidade_medida.value,
            preco_custo=produto.preco_custo,
            preco_venda=produto.preco_venda,
            estoque_atual=produto.estoque_atual,
            estoque_minimo=produto.estoque_minimo,
            ativo=produto.ativo,
            version=produto.version,
            created_at=to_naive_utc(produto.created_at),
            updated_at=to_naive_utc(produto.updated_at),
        )
        self._session.add(model)

    def update(self, produto: Produto) -> None:
        model = self._session.get(ProdutoModel, produto.id)
        if model is None:
            raise NotFoundException("Produto não encontrado.")

        model.nome = produto.nome
        model.descricao = produto.descricao
        model.sku = produto.sku
        model.codigo_barras = produto.codigo_barras
        model.categoria = produto.categoria
        model.unidade_medida = produto.unidade_medida.value
        model.preco_custo = produto.preco_custo
        model.preco_venda = produto.preco_venda
        model.estoque_atual = produto.estoque_atual
        model.estoque_minimo = produto.estoque_minimo
        model.ativo = produto.ativo
        model.updated_at = to_naive_utc(produto.updated_at)
        # `version` NÃO é copiado: é o SQLAlchemy (version_id_col) quem lê/incrementa essa
        # coluna sozinho no UPDATE, comparando com o valor que estava carregado na sessão —
        # é isso que detecta conflito de concorrência e levanta StaleDataError (-> 409).

    def remove(self, produto: Produto) -> None:
        model = self._session.get(ProdutoModel, produto.id)
        if model is not None:
            self._session.delete(model)
