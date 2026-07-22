"""Equivalente a Application/Operations/Clientes/ClienteDtos.cs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel


class ClienteDto(CamelModel):
    id: UUID
    nome: str
    cpf_cnpj: str | None
    telefone: str | None
    email: str | None
    cidade: str | None
    estado: str | None
    observacoes: str | None
    ativo: bool
    created_at: datetime
    updated_at: datetime | None


class CriarClienteRequest(CamelModel):
    nome: str
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    cidade: str | None = None
    estado: str | None = None
    observacoes: str | None = None


class AtualizarClienteRequest(CamelModel):
    nome: str
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    cidade: str | None = None
    estado: str | None = None
    observacoes: str | None = None
    ativo: bool
