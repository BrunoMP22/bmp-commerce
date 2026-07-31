"""Regras financeiras — só rodam para Admin/SuperAdmin (financeiro=True, ADR 0004).

Comparações temporais usam janelas móveis de 30 dias (últimos 30 vs 30 anteriores),
nunca mês-calendário parcial vs mês fechado: comparar 10 dias de julho com junho
inteiro geraria "quedas" falsas o mês todo.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.format import moeda, percentual
from app.insights.rules._comum import custo, quantidade_por_produto, receita, receita_por_produto

_LIMIAR_VARIACAO_PCT = Decimal("5")
_LIMIAR_MARGEM_PP = Decimal("2")
_MINIMO_VENDAS_TICKET = 3


class FaturamentoEmMovimento(RegraDeInsight):
    tipo = "faturamento-em-movimento"
    financeiro = True

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        atual = receita(contexto.vendas_desde(30))
        anterior = receita(contexto.vendas_entre(60, 30))

        if anterior <= 0 or atual <= 0:
            return None

        delta = (atual - anterior) / anterior * 100
        mensagem = (
            f"Você faturou {moeda(atual)} nos últimos 30 dias, contra {moeda(anterior)} "
            f"nos 30 dias anteriores ({percentual(delta, com_sinal=True)})."
        )

        if delta >= _LIMIAR_VARIACAO_PCT:
            return Insight(
                tipo=self.tipo,
                severidade=Severidade.OPORTUNIDADE,
                titulo="Faturamento em alta",
                mensagem=mensagem,
                destaque=percentual(delta, com_sinal=True),
                acao="Aproveite o embalo: garanta estoque dos produtos que puxaram o crescimento antes que falte.",
                valor=delta,
            )

        if delta <= -_LIMIAR_VARIACAO_PCT:
            return Insight(
                tipo=self.tipo,
                severidade=Severidade.ALERTA,
                titulo="Faturamento em queda",
                mensagem=mensagem,
                destaque=percentual(delta, com_sinal=True),
                acao=(
                    "Compare o que vendia no período anterior e parou de vender — "
                    "uma queda quase sempre tem dois ou três produtos como causa."
                ),
                valor=delta,
            )

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.INFO,
            titulo="Faturamento estável",
            mensagem=mensagem,
            destaque=percentual(delta, com_sinal=True),
            valor=delta,
        )


class TicketMedioEmMovimento(RegraDeInsight):
    tipo = "ticket-medio-em-movimento"
    financeiro = True

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas_atual = contexto.vendas_desde(30)
        vendas_anterior = contexto.vendas_entre(60, 30)

        # Com pouquíssimas vendas o ticket médio vira loteria — melhor ficar calado.
        if len(vendas_atual) < _MINIMO_VENDAS_TICKET or len(vendas_anterior) < _MINIMO_VENDAS_TICKET:
            return None

        ticket_atual = receita(vendas_atual) / len(vendas_atual)
        ticket_anterior = receita(vendas_anterior) / len(vendas_anterior)

        if ticket_anterior <= 0:
            return None

        delta = (ticket_atual - ticket_anterior) / ticket_anterior * 100

        if delta >= _LIMIAR_VARIACAO_PCT:
            return Insight(
                tipo=self.tipo,
                severidade=Severidade.OPORTUNIDADE,
                titulo="Ticket médio subindo",
                mensagem=(
                    f"Cada venda está valendo mais: ticket médio de {moeda(ticket_atual)} nos últimos "
                    f"30 dias, contra {moeda(ticket_anterior)} antes ({percentual(delta, com_sinal=True)})."
                ),
                destaque=percentual(delta, com_sinal=True),
                acao="Seus clientes estão levando mais por compra — teste kits e combos para reforçar o movimento.",
                valor=delta,
            )

        if delta <= -_LIMIAR_VARIACAO_PCT:
            return Insight(
                tipo=self.tipo,
                severidade=Severidade.ALERTA,
                titulo="Ticket médio caindo",
                mensagem=(
                    f"Cada venda está valendo menos: ticket médio de {moeda(ticket_atual)} nos últimos "
                    f"30 dias, contra {moeda(ticket_anterior)} antes ({percentual(delta, com_sinal=True)})."
                ),
                destaque=percentual(delta, com_sinal=True),
                acao="Reveja o mix: sugerir um item complementar no fechamento é o jeito mais barato de recuperar ticket.",
                valor=delta,
            )

        return None


class MargemEmMovimento(RegraDeInsight):
    tipo = "margem-em-movimento"
    financeiro = True

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas_atual = contexto.vendas_desde(30)
        vendas_anterior = contexto.vendas_entre(60, 30)

        receita_atual = receita(vendas_atual)
        receita_anterior = receita(vendas_anterior)

        if receita_atual <= 0 or receita_anterior <= 0:
            return None

        margem_atual = (receita_atual - custo(vendas_atual)) / receita_atual * 100
        margem_anterior = (receita_anterior - custo(vendas_anterior)) / receita_anterior * 100
        delta_pp = margem_atual - margem_anterior

        if abs(delta_pp) < _LIMIAR_MARGEM_PP:
            return None

        pontos = delta_pp.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        destaque = f"{'+' if pontos > 0 else ''}{pontos} p.p."
        mensagem = (
            f"Sua margem bruta foi de {percentual(margem_anterior)} para {percentual(margem_atual)} "
            f"({destaque}) comparando os últimos 30 dias com os 30 anteriores."
        )

        if delta_pp < 0:
            return Insight(
                tipo=self.tipo,
                severidade=Severidade.ALERTA,
                titulo="Margem encolhendo",
                mensagem=mensagem,
                destaque=destaque,
                acao=(
                    "Margem menor com venda igual é lucro evaporando: verifique custos reajustados "
                    "que não foram repassados e descontos concedidos no balcão."
                ),
                valor=delta_pp,
            )

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.OPORTUNIDADE,
            titulo="Margem melhorando",
            mensagem=mensagem,
            destaque=destaque,
            acao="O mix está mais rentável — identifique o que mudou e dobre a aposta.",
            valor=delta_pp,
        )


class CampeaoDeLucro(RegraDeInsight):
    tipo = "campeao-de-lucro"
    financeiro = True

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas = contexto.vendas_desde(90)

        lucro_por_produto: dict = {}
        for venda in vendas:
            for item in venda.itens:
                lucro_item = (item.preco_venda_momento - item.preco_custo_momento) * item.quantidade
                nome, acumulado = lucro_por_produto.get(item.produto_id, (item.produto_nome, Decimal("0")))
                lucro_por_produto[item.produto_id] = (nome, acumulado + lucro_item)

        if not lucro_por_produto:
            return None

        lucro_total = sum((lucro for _, lucro in lucro_por_produto.values()), Decimal("0"))
        nome, lucro_top = max(lucro_por_produto.values(), key=lambda par: par[1])

        if lucro_top <= 0 or lucro_total <= 0:
            return None

        participacao = lucro_top / lucro_total * 100

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.INFO,
            titulo="Campeão de lucro",
            mensagem=(
                f"'{nome}' gerou {moeda(lucro_top)} de lucro bruto nos últimos 90 dias — "
                f"{percentual(participacao)} de todo o lucro do período."
            ),
            destaque=moeda(lucro_top),
            acao="Esse produto é o motor do seu resultado: nunca deixe faltar e resista a dar desconto nele.",
            valor=lucro_top,
        )


class ConcentracaoDeProduto(RegraDeInsight):
    tipo = "concentracao-de-produto"
    financeiro = True

    _LIMIAR_INFO = Decimal("25")
    _LIMIAR_ALERTA = Decimal("40")

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendas = contexto.vendas_desde(90)
        por_produto = receita_por_produto(vendas)
        total = receita(vendas)

        if not por_produto or total <= 0:
            return None

        nome, receita_top = max(por_produto.values(), key=lambda par: par[1])
        participacao = receita_top / total * 100

        if participacao < self._LIMIAR_INFO:
            return None

        alerta = participacao >= self._LIMIAR_ALERTA
        return Insight(
            tipo=self.tipo,
            severidade=Severidade.ALERTA if alerta else Severidade.INFO,
            titulo="Faturamento dependente de um produto",
            mensagem=(
                f"'{nome}' sozinho respondeu por {percentual(participacao)} de tudo que você "
                f"faturou nos últimos 90 dias."
            ),
            destaque=percentual(participacao),
            acao=(
                "Se ele faltar, o mês desaba. Garanta fornecimento e desenvolva um segundo carro-chefe."
                if alerta
                else "Bom vendedor — mas vale desenvolver alternativas para não depender de um item só."
            ),
            valor=participacao,
        )
