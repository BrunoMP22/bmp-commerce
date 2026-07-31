"""Formatação pt-BR das frases de negócio.

As mensagens saem do backend prontas para exibição: a tela nunca recompõe frase, só dá
ênfase ao `destaque`. Centralizar aqui evita que cada regra formate moeda/percentual de
um jeito.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def moeda(valor: Decimal) -> str:
    quantizado = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    inteiro, _, centavos = f"{quantizado:.2f}".partition(".")
    negativo = inteiro.startswith("-")
    inteiro = inteiro.lstrip("-")

    grupos: list[str] = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)

    sinal = "-" if negativo else ""
    return f"{sinal}R$ {'.'.join(grupos)},{centavos}"


def percentual(valor: Decimal, *, com_sinal: bool = False) -> str:
    arredondado = valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    sinal = "+" if com_sinal and arredondado > 0 else ""
    return f"{sinal}{arredondado}%"


def plural(quantidade: int, singular: str, plural_: str) -> str:
    return singular if quantidade == 1 else plural_
