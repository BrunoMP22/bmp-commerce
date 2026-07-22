"""Equivalente a API/Middlewares/ExceptionHandlingMiddleware.cs — unifica toda resposta
de erro no formato `{"message": "..."}` já consumido pelo frontend
(`ApiError` em src/api/client.ts), com o mesmo mapeamento de status code.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import StaleDataError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import DomainException, NotFoundException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def handle_not_found(request: Request, exc: NotFoundException) -> JSONResponse:
        logger.warning(
            "Recurso não encontrado ao processar %s %s: %s", request.method, request.url.path, exc
        )
        return _error_response(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(DomainException)
    async def handle_domain(request: Request, exc: DomainException) -> JSONResponse:
        logger.warning(
            "Regra de domínio violada ao processar %s %s: %s", request.method, request.url.path, exc
        )
        return _error_response(status.HTTP_400_BAD_REQUEST, str(exc))

    @app.exception_handler(StaleDataError)
    async def handle_concurrency(request: Request, exc: StaleDataError) -> JSONResponse:
        # Conflito de concorrência otimista (version_id_col em Produto/Venda, equivalente
        # ao RowVersion do C#): outra operação alterou o mesmo registro — ex: duas vendas
        # simultâneas debitando o estoque do mesmo produto. Nada foi persistido.
        logger.warning(
            "Conflito de concorrência ao processar %s %s", request.method, request.url.path, exc_info=exc
        )
        return _error_response(
            status.HTTP_409_CONFLICT,
            "Os dados foram alterados por outra operação ao mesmo tempo. Tente novamente.",
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Equivalente ao `ApiBehaviorOptions.InvalidModelStateResponseFactory` do Program.cs:
        # devolve só a primeira mensagem de validação, no mesmo formato `{message}`.
        errors = exc.errors()
        message = str(errors[0]["msg"]) if errors else "Requisição inválida."
        return _error_response(status.HTTP_400_BAD_REQUEST, message)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Cobre, entre outros, o 401 levantado por app/dependencies/auth.py quando o
        # token está ausente/inválido — equivalente ao desafio 401 do JwtBearer no C#.
        detail = exc.detail if isinstance(exc.detail, str) and exc.detail else "Requisição inválida."
        return _error_response(exc.status_code, detail, headers=exc.headers)

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Erro não tratado ao processar %s %s", request.method, request.url.path, exc_info=exc
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Ocorreu um erro inesperado. Tente novamente."
        )


def _error_response(status_code: int, message: str, *, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"message": message}, headers=headers)
