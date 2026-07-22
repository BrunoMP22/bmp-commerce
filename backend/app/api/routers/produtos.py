"""Equivalente a API/Controllers/ProdutosController.cs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import ProdutoServiceDep, get_current_user_id
from app.schemas.produto import AtualizarProdutoRequest, CriarProdutoRequest, ProdutoDto

# `dependencies=[Depends(get_current_user_id)]` no router inteiro == [Authorize] na
# classe do controller C#: toda rota abaixo exige um Bearer token válido.
router = APIRouter(prefix="/api/produtos", tags=["Produtos"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=list[ProdutoDto])
def listar(produto_service: ProdutoServiceDep, search: str | None = None) -> list[ProdutoDto]:
    return produto_service.listar(search)


@router.get("/{produto_id}", response_model=ProdutoDto)
def obter_por_id(produto_id: UUID, produto_service: ProdutoServiceDep) -> ProdutoDto:
    return produto_service.obter_por_id(produto_id)


@router.post("", response_model=ProdutoDto, status_code=status.HTTP_201_CREATED)
def criar(
    request: CriarProdutoRequest,
    produto_service: ProdutoServiceDep,
    response: Response,
) -> ProdutoDto:
    result = produto_service.criar(request)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)

    assert result.value is not None
    response.headers["Location"] = f"/api/produtos/{result.value.id}"
    return result.value


@router.put("/{produto_id}", response_model=ProdutoDto)
def atualizar(
    produto_id: UUID,
    request: AtualizarProdutoRequest,
    produto_service: ProdutoServiceDep,
) -> ProdutoDto:
    result = produto_service.atualizar(produto_id, request)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)

    assert result.value is not None
    return result.value


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def excluir(produto_id: UUID, produto_service: ProdutoServiceDep) -> None:
    result = produto_service.excluir(produto_id)

    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)
