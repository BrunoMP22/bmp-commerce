"""Regras sobre o padrão das vendas: ritmo semanal e vendas de balcão."""

from __future__ import annotations

from decimal import Decimal

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.format import moeda, percentual
from app.insights.rules._comum import receita

_DIAS_JANELA_SEMANAL = 28
_MINIMO_VENDAS_SEMANAL = 8
_LIMIAR_DIA_FORTE = Decimal("25")

_MINIMO_VENDAS_BALCAO = 5
_LIMIAR_BALCAO = Decimal("30")

# (artigo, nome) por weekday() do Python — segunda = 0.
_DIAS_DA_SEMANA = [
    ("A", "segunda-feira"),
    ("A", "terça-feira"),
    ("A", "quarta-feira"),
    ("A", "quinta-feira"),
    ("A", "sexta-feira"),
    ("O", "sábado"),
    ("O", "domingo"),
]


class MelhorDiaDaSemana(RegraDeInsight):
    """Qual dia da semana concentra a receita das últimas 4 semanas — para decidir
    quando repor, escalar equipe e concentrar promoções."""

    tipo = "melhor-dia-da-semana"

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas = contexto.vendas_desde(_DIAS_JANELA_SEMANAL)
        if len(vendas) < _MINIMO_VENDAS_SEMANAL:
            return None

        total = receita(vendas)
        if total <= 0:
            return None

        por_dia: dict[int, Decimal] = {}
        for venda in vendas:
            dia = venda.data_hora.weekday()
            por_dia[dia] = por_dia.get(dia, Decimal("0")) + venda.total

        melhor_dia, receita_dia = max(por_dia.items(), key=lambda par: par[1])
        participacao = receita_dia / total * 100

        if participacao < _LIMIAR_DIA_FORTE:
            return None

        artigo, nome = _DIAS_DA_SEMANA[melhor_dia]

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.INFO,
            titulo="Seu dia mais forte",
            mensagem=(
                f"{artigo} {nome} concentra {percentual(participacao)} da sua receita das últimas "
                f"4 semanas ({moeda(receita_dia)})."
            ),
            destaque=percentual(participacao),
            acao=(
                f"Chegue n{artigo.lower()} {nome} com estoque reposto e equipe completa — "
                "é o dia em que falta de produto custa mais caro."
            ),
            valor=participacao,
        )


class VendasDeBalcao(RegraDeInsight):
    """Parcela das vendas sem cliente identificado. Cada venda anônima é histórico
    de recompra que o lojista perde."""

    tipo = "vendas-de-balcao"

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas = contexto.vendas_desde(30)
        if len(vendas) < _MINIMO_VENDAS_BALCAO:
            return None

        sem_cliente = sum(1 for venda in vendas if venda.cliente_id is None)
        participacao = Decimal(sem_cliente) / Decimal(len(vendas)) * 100

        if participacao < _LIMIAR_BALCAO:
            return None

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.OPORTUNIDADE,
            titulo="Clientes anônimos no balcão",
            mensagem=(
                f"{percentual(participacao)} das vendas dos últimos 30 dias saíram sem cliente "
                f"identificado ({sem_cliente} de {len(vendas)})."
            ),
            destaque=percentual(participacao),
            acao=(
                "Peça um telefone ou nome no fechamento: cliente identificado vira histórico, "
                "recompra e campanha de reativação."
            ),
            valor=participacao,
        )
