"""Informações do sistema para a tela de Configurações (versão, ambiente)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.dependencies import get_current_user_id
from app.schemas.common import CamelModel

router = APIRouter(prefix="/api/sistema", tags=["Sistema"], dependencies=[Depends(get_current_user_id)])

_VERSAO_API = "1.0.0"


class InfoSistemaDto(CamelModel):
    nome: str
    versao: str
    ambiente: str


@router.get("/info", response_model=InfoSistemaDto)
def info() -> InfoSistemaDto:
    return InfoSistemaDto(nome="BMP Commerce", versao=_VERSAO_API, ambiente=settings.environment)
