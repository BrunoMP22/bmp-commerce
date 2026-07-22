"""Equivalente a Application/Operations/Produtos/ProdutoService.cs."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.domain.common import Result
from app.domain.enums import UnidadeMedida
from app.domain.produto import Produto
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.produto import AtualizarProdutoRequest, CriarProdutoRequest, ProdutoDto


class ProdutoService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._produtos = ProdutoRepository(session)
        self._vendas = VendaRepository(session)

    def listar(self, search: str | None) -> list[ProdutoDto]:
        produtos = self._produtos.get_all(search)
        return [self._to_dto(p) for p in produtos]

    def obter_por_id(self, produto_id: UUID) -> ProdutoDto:
        produto = self._produtos.get_by_id(produto_id)
        if produto is None:
            raise NotFoundException("Produto não encontrado.")

        return self._to_dto(produto)

    def criar(self, request: CriarProdutoRequest) -> Result[ProdutoDto]:
        if self._produtos.existe_sku(request.sku, ignorar_id=None):
            return Result.failure("Já existe um produto com esse SKU.")

        try:
            unidade_medida = UnidadeMedida(request.unidade_medida)
        except ValueError:
            return Result.failure("Unidade de medida inválida.")

        produto = Produto(
            nome=request.nome,
            sku=request.sku,
            descricao=request.descricao,
            codigo_barras=request.codigo_barras,
            categoria=request.categoria,
            unidade_medida=unidade_medida,
            preco_custo=_to_decimal(request.preco_custo),
            preco_venda=_to_decimal(request.preco_venda),
            estoque_atual=request.estoque_atual,
            estoque_minimo=request.estoque_minimo,
        )

        self._produtos.add(produto)
        self._session.commit()

        return Result.success(self._to_dto(produto))

    def atualizar(self, produto_id: UUID, request: AtualizarProdutoRequest) -> Result[ProdutoDto]:
        produto = self._produtos.get_by_id(produto_id)
        if produto is None:
            raise NotFoundException("Produto não encontrado.")

        if self._produtos.existe_sku(request.sku, ignorar_id=produto_id):
            return Result.failure("Já existe um produto com esse SKU.")

        try:
            unidade_medida = UnidadeMedida(request.unidade_medida)
        except ValueError:
            return Result.failure("Unidade de medida inválida.")

        produto.atualizar(
            nome=request.nome,
            sku=request.sku,
            descricao=request.descricao,
            codigo_barras=request.codigo_barras,
            categoria=request.categoria,
            unidade_medida=unidade_medida,
            preco_custo=_to_decimal(request.preco_custo),
            preco_venda=_to_decimal(request.preco_venda),
            estoque_atual=request.estoque_atual,
            estoque_minimo=request.estoque_minimo,
            ativo=request.ativo,
        )

        self._produtos.update(produto)
        self._session.commit()

        return Result.success(self._to_dto(produto))

    def excluir(self, produto_id: UUID) -> Result[None]:
        produto = self._produtos.get_by_id(produto_id)
        if produto is None:
            raise NotFoundException("Produto não encontrado.")

        # Preserva o histórico de vendas (Doc 01 REGRA 4): produto vendido não sai do banco.
        if self._vendas.existe_venda_com_produto(produto_id):
            return Result.failure(
                "Produto possui vendas registradas e não pode ser excluído. Inative-o em vez de excluir."
            )

        self._produtos.remove(produto)
        self._session.commit()

        return Result.success()

    @staticmethod
    def _to_dto(produto: Produto) -> ProdutoDto:
        return ProdutoDto.model_validate(produto)


def _to_decimal(value: float) -> Decimal:
    """`float` chega do schema Pydantic (contrato JSON com o frontend); convertido via
    `str()` para não herdar erro de ponto flutuante binário (Decimal(0.1) != Decimal("0.1"))."""
    return Decimal(str(value))
