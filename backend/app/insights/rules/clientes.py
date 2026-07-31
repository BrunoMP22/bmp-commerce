"""Regras sobre a carteira de clientes: reativação e concentração de receita."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.format import percentual, plural

_DIAS_SUMIDO = 45
_MINIMO_CLIENTES_CONCENTRACAO = 5
_TOP_CLIENTES = 3
_LIMIAR_CONCENTRACAO = Decimal("40")


class ClientesSumidos(RegraDeInsight):
    """Cliente ativo que já comprou mas não volta há 45+ dias. Reativar quem já
    conhece a loja é mais barato que conquistar um cliente novo."""

    tipo = "clientes-sumidos"

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        ultima_compra: dict[UUID, datetime] = {}
        for venda in contexto.vendas_validas:
            if venda.cliente_id is None:
                continue
            registrada = ultima_compra.get(venda.cliente_id)
            if registrada is None or venda.data_hora > registrada:
                ultima_compra[venda.cliente_id] = venda.data_hora

        sumidos: list[tuple[str, int]] = []
        for cliente in contexto.clientes:
            if not cliente.ativo:
                continue

            data = ultima_compra.get(cliente.id)
            if data is None:
                continue

            dias = (contexto.agora - data).days
            if dias >= _DIAS_SUMIDO:
                sumidos.append((cliente.nome, dias))

        if not sumidos:
            return None

        sumidos.sort(key=lambda registro: registro[1], reverse=True)
        nome, dias = sumidos[0]
        quantidade = len(sumidos)

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.OPORTUNIDADE,
            titulo="Clientes esfriando",
            mensagem=(
                f"{quantidade} {plural(quantidade, 'cliente que já comprou não volta', 'clientes que já compraram não voltam')} "
                f"há mais de {_DIAS_SUMIDO} dias — o caso mais antigo é {nome}, sem comprar há {dias} dias."
            ),
            destaque=f"{quantidade} {plural(quantidade, 'cliente', 'clientes')}",
            acao=(
                "Uma mensagem simples de 'sentimos sua falta' com um benefício pequeno "
                "costuma reativar boa parte — e custa quase nada."
            ),
            valor=Decimal(quantidade),
        )


class ConcentracaoDeClientes(RegraDeInsight):
    """Poucos clientes segurando muita receita: bom sinal de fidelidade, risco de
    dependência. Financeiro: fala da composição da receita."""

    tipo = "concentracao-de-clientes"
    financeiro = True

    def avaliar(self, contexto: InsightContext) -> Insight | None:
        receita_por_cliente: dict[UUID, Decimal] = {}
        for venda in contexto.vendas_desde(90):
            if venda.cliente_id is None:
                continue
            receita_por_cliente[venda.cliente_id] = (
                receita_por_cliente.get(venda.cliente_id, Decimal("0")) + venda.total
            )

        if len(receita_por_cliente) < _MINIMO_CLIENTES_CONCENTRACAO:
            return None

        total = sum(receita_por_cliente.values(), Decimal("0"))
        if total <= 0:
            return None

        ordenados = sorted(receita_por_cliente.items(), key=lambda par: par[1], reverse=True)
        top = ordenados[:_TOP_CLIENTES]
        participacao = sum((valor for _, valor in top), Decimal("0")) / total * 100

        if participacao < _LIMIAR_CONCENTRACAO:
            return None

        nomes = {cliente.id: cliente.nome for cliente in contexto.clientes}
        maior = nomes.get(top[0][0], "seu maior cliente")

        return Insight(
            tipo=self.tipo,
            severidade=Severidade.INFO,
            titulo="Poucos clientes, muita receita",
            mensagem=(
                f"Apenas {_TOP_CLIENTES} clientes respondem por {percentual(participacao)} da receita "
                f"identificada dos últimos 90 dias — o maior é {maior}."
            ),
            destaque=percentual(participacao),
            acao=(
                "Eles seguram seu caixa: trate-os como VIPs. E trabalhe a base para "
                "que nenhuma saída isolada machuque o mês."
            ),
            valor=participacao,
        )
