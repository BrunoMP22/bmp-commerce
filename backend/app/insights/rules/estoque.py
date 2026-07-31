"""Regras operacionais de estoque: giro, ruptura e capital imobilizado."""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.format import moeda, percentual, plural

_DIAS_SEM_VENDA = 30
_DIAS_RUPTURA = 14


def _ultima_venda_por_produto(contexto: InsightContext) -> dict[UUID, datetime]:
    resultado: dict[UUID, datetime] = {}
    for venda in contexto.vendas_validas:
        for item in venda.itens:
            registrada = resultado.get(item.produto_id)
            if registrada is None or venda.data_hora > registrada:
                resultado[item.produto_id] = venda.data_hora
    return resultado


class ProdutosEncalhados(RegraDeInsight):
    """Produto ativo, com estoque, que não vende há 30+ dias (ou nunca vendeu desde
    que foi cadastrado há 30+ dias). O pior caso vira a frase; o resto vira contagem."""

    tipo = "produtos-encalhados"

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        ultima_venda = _ultima_venda_por_produto(contexto)

        encalhados: list[tuple[str, int, bool]] = []
        for produto in contexto.produtos:
            if not produto.ativo or produto.estoque_atual <= 0:
                continue

            referencia = ultima_venda.get(produto.id)
            nunca_vendeu = referencia is None
            dias = (contexto.agora - (referencia or produto.created_at)).days

            if dias >= _DIAS_SEM_VENDA:
                encalhados.append((produto.nome, dias, nunca_vendeu))

        if not encalhados:
            return None

        encalhados.sort(key=lambda registro: registro[1], reverse=True)
        nome, dias, nunca_vendeu = encalhados[0]
        demais = len(encalhados) - 1

        frase_pior = (
            f"'{nome}' está no catálogo há {dias} dias e nunca vendeu uma unidade"
            if nunca_vendeu
            else f"'{nome}' não vende há {dias} dias"
        )
        complemento = (
            f" — e mais {demais} {plural(demais, 'produto está', 'produtos estão')} sem vender há 30+ dias."
            if demais > 0
            else "."
        )

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.ALERTA,
            titulo="Produto encalhado",
            mensagem=frase_pior + complemento,
            destaque=f"{dias} dias",
            acao=(
                "Considere promoção pontual, combo ou lugar de destaque na loja. "
                "Se não girar mesmo assim, é candidato a sair do catálogo."
            ),
            valor=Decimal(dias),
        )


class PrevisaoDeRuptura(RegraDeInsight):
    """Previsão simples e honesta: velocidade de venda dos últimos 30 dias projetada
    sobre o estoque atual. Não é IA — é aritmética que evita prateleira vazia."""

    tipo = "previsao-de-ruptura"

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendido_30_dias: dict[UUID, int] = {}
        for venda in contexto.vendas_desde(30):
            for item in venda.itens:
                vendido_30_dias[item.produto_id] = vendido_30_dias.get(item.produto_id, 0) + item.quantidade

        em_risco: list[tuple[str, int]] = []
        for produto in contexto.produtos:
            if not produto.ativo or produto.estoque_atual <= 0:
                continue

            quantidade = vendido_30_dias.get(produto.id, 0)
            if quantidade <= 0:
                continue

            dias_restantes = int(
                (Decimal(produto.estoque_atual) * 30 / Decimal(quantidade)).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            if dias_restantes <= _DIAS_RUPTURA:
                em_risco.append((produto.nome, dias_restantes))

        if not em_risco:
            return None

        em_risco.sort(key=lambda registro: registro[1])
        nome, dias = em_risco[0]
        demais = len(em_risco) - 1

        complemento = (
            f" Outros {demais} {plural(demais, 'produto zera', 'produtos zeram')} em até 14 dias."
            if demais > 0
            else ""
        )

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.ALERTA,
            titulo="Risco de ruptura de estoque",
            mensagem=(
                f"No ritmo de venda atual, '{nome}' zera o estoque em aproximadamente "
                f"{dias} {plural(dias, 'dia', 'dias')}.{complemento}"
            ),
            destaque=f"~{dias} {plural(dias, 'dia', 'dias')}",
            acao="Programe a reposição agora — venda perdida por falta de estoque não volta.",
            valor=Decimal(dias),
        )


class CapitalParado(RegraDeInsight):
    """Quanto do valor do estoque (a preço de custo) está em produtos que não venderam
    nada nos últimos 30 dias. Financeiro: fala de capital, não de operação."""

    tipo = "capital-parado"
    financeiro = True

    _LIMIAR_INFO = Decimal("20")
    _LIMIAR_ALERTA = Decimal("35")

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        vendidos_30_dias = {
            item.produto_id for venda in contexto.vendas_desde(30) for item in venda.itens
        }

        valor_total = Decimal("0")
        valor_parado = Decimal("0")
        for produto in contexto.produtos:
            if not produto.ativo or produto.estoque_atual <= 0:
                continue

            valor = produto.preco_custo * produto.estoque_atual
            valor_total += valor
            if produto.id not in vendidos_30_dias:
                valor_parado += valor

        if valor_total <= 0 or valor_parado <= 0:
            return None

        participacao = valor_parado / valor_total * 100
        if participacao < self._LIMIAR_INFO:
            return None

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.ALERTA if participacao >= self._LIMIAR_ALERTA else Severidade.INFO,
            titulo="Capital parado no estoque",
            mensagem=(
                f"{moeda(valor_parado)} — {percentual(participacao)} do valor do seu estoque a preço "
                f"de custo — estão em produtos que não venderam nada nos últimos 30 dias."
            ),
            destaque=moeda(valor_parado),
            acao="Estoque parado é dinheiro que não trabalha: gire com promoção ou reduza a próxima compra.",
            valor=valor_parado,
        )
