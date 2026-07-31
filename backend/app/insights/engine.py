"""Motor de Insights (Doc 01 §9 PASSO 4-5, ADR 0004).

O motor não sabe o que cada regra faz: mantém a lista registrada, roda todas sobre o
mesmo contexto e agrega o resultado ordenado por urgência (alertas → oportunidades →
informativos). Adicionar um insight novo = registrar uma regra nova em
`motor_padrao()`; o motor em si não muda.
"""

from __future__ import annotations

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.rules import (
    CampeaoDeLucro,
    CapitalParado,
    ClientesSumidos,
    ConcentracaoDeClientes,
    ConcentracaoDeProduto,
    FaturamentoEmMovimento,
    MargemEmMovimento,
    MelhorDiaDaSemana,
    PrevisaoDeRuptura,
    ProdutosEncalhados,
    TicketMedioEmMovimento,
    VendasDeBalcao,
)

_ORDEM_SEVERIDADE = {
    Severidade.ALERTA: 0,
    Severidade.OPORTUNIDADE: 1,
    Severidade.INFO: 2,
}


class MotorDeInsights:
    def __init__(self, regras: list[RegraDeInsight]) -> None:
        self._regras = list(regras)

    def executar(self, contexto: InsightContext, *, incluir_financeiros: bool) -> list[Insight]:
        insights = [
            insight
            for regra in self._regras
            if incluir_financeiros or not regra.financeiro
            if (insight := regra.avaliar(contexto)) is not None
        ]
        # Ordenação estável: dentro da mesma severidade vale a ordem de registro.
        return sorted(insights, key=lambda insight: _ORDEM_SEVERIDADE[insight.severidade])


def motor_padrao() -> MotorDeInsights:
    """Registro único das regras ativas — o "catálogo" de insights do produto."""
    return MotorDeInsights(
        [
            FaturamentoEmMovimento(),
            MargemEmMovimento(),
            PrevisaoDeRuptura(),
            ProdutosEncalhados(),
            CapitalParado(),
            TicketMedioEmMovimento(),
            ClientesSumidos(),
            VendasDeBalcao(),
            MelhorDiaDaSemana(),
            CampeaoDeLucro(),
            ConcentracaoDeProduto(),
            ConcentracaoDeClientes(),
        ]
    )
