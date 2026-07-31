"""Caso de uso da área de Insights: carrega a fotografia dos dados, roda o motor e
devolve as frases prontas.

O papel do usuário decide o alcance (ADR 0004): Admin/SuperAdmin recebem tudo;
Funcionário só recebe insights operacionais — o filtro acontece aqui, no back-end,
nunca só na tela.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.enums import UserRole
from app.insights import InsightContext, Severidade, motor_padrao
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.venda_repository import VendaRepository
from app.schemas.insight import InsightDto, InsightsDto, ResumoInsightsDto

_PAPEIS_FINANCEIROS = (UserRole.SUPER_ADMIN, UserRole.ADMIN)


class InsightsService:
    def __init__(self, session: Session) -> None:
        self._vendas = VendaRepository(session)
        self._produtos = ProdutoRepository(session)
        self._clientes = ClienteRepository(session)
        self._motor = motor_padrao()

    def obter_insights(self, role: UserRole) -> InsightsDto:
        contexto = InsightContext(
            agora=datetime.now(timezone.utc),
            vendas=self._vendas.get_all(),
            produtos=self._produtos.get_all(search=None),
            clientes=self._clientes.get_all(),
        )

        insights = self._motor.executar(
            contexto,
            incluir_financeiros=role in _PAPEIS_FINANCEIROS,
        )

        return InsightsDto(
            gerado_em=contexto.agora,
            resumo=ResumoInsightsDto(
                alertas=sum(1 for insight in insights if insight.severidade == Severidade.ALERTA),
                oportunidades=sum(
                    1 for insight in insights if insight.severidade == Severidade.OPORTUNIDADE
                ),
                informativos=sum(1 for insight in insights if insight.severidade == Severidade.INFO),
            ),
            insights=[
                InsightDto(
                    tipo=insight.tipo,
                    severidade=insight.severidade.value,
                    titulo=insight.titulo,
                    mensagem=insight.mensagem,
                    destaque=insight.destaque,
                    acao=insight.acao,
                    valor=float(insight.valor) if insight.valor is not None else None,
                )
                for insight in insights
            ],
        )
