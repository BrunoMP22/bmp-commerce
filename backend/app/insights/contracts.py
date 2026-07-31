"""Contrato do Motor de Insights (Doc 01 §9, ADR 0004).

Um `Insight` é uma frase de negócio: além do mínimo do contrato (tipo, severidade,
mensagem, valor), carrega `titulo`, `destaque` (o número da frase já formatado, para a
tela dar ênfase sem reimplementar formatação) e `acao` (o "e agora?" — a recomendação
prática que transforma dado em decisão).

`InsightContext` é a fotografia dos dados do tenant no momento da consulta: as regras
recebem tudo já carregado e não tocam em repositório nem em sessão — por construção,
uma regra não tem como escrever no banco.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.domain.cliente import Cliente
    from app.domain.produto import Produto
    from app.domain.venda import Venda


class Severidade(StrEnum):
    ALERTA = "Alerta"
    OPORTUNIDADE = "Oportunidade"
    INFO = "Info"


@dataclass(frozen=True)
class Insight:
    tipo: str
    severidade: Severidade
    titulo: str
    mensagem: str
    destaque: str | None = None
    acao: str | None = None
    valor: Decimal | None = None


@dataclass
class InsightContext:
    """Dados do tenant carregados uma única vez e compartilhados por todas as regras."""

    agora: datetime
    vendas: list[Venda]
    produtos: list[Produto]
    clientes: list[Cliente]
    _vendas_validas: list[Venda] | None = field(default=None, init=False, repr=False)

    @property
    def vendas_validas(self) -> list[Venda]:
        """Vendas não canceladas — a base de todo cálculo (cancelada não é receita)."""
        if self._vendas_validas is None:
            self._vendas_validas = [venda for venda in self.vendas if not venda.is_deleted]
        return self._vendas_validas

    def vendas_desde(self, dias: int) -> list[Venda]:
        limite = self.agora - timedelta(days=dias)
        return [venda for venda in self.vendas_validas if venda.data_hora >= limite]

    def vendas_entre(self, dias_inicio: int, dias_fim: int) -> list[Venda]:
        """Vendas válidas na janela [agora - dias_inicio, agora - dias_fim)."""
        inicio = self.agora - timedelta(days=dias_inicio)
        fim = self.agora - timedelta(days=dias_fim)
        return [venda for venda in self.vendas_validas if inicio <= venda.data_hora < fim]


class RegraDeInsight(ABC):
    """Uma regra = um insight em potencial. Devolve `None` quando não há nada relevante
    a dizer — silêncio é melhor que ruído (só falamos quando o dado sustenta a frase)."""

    tipo: ClassVar[str]
    # Regras financeiras (margem, lucro, concentração de receita) só rodam para
    # Admin/SuperAdmin — bloqueio no back-end, nunca só na tela (ADR 0004).
    financeiro: ClassVar[bool] = False

    @abstractmethod
    def avaliar(self, contexto: InsightContext) -> Insight | None: ...
