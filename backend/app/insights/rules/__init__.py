"""Regras do Motor de Insights — uma classe por insight (ADR 0004).

Organização por tema, não por severidade: a severidade é decidida pela própria regra
a partir do dado (o mesmo insight pode ser oportunidade num mês e alerta no outro).
"""

from app.insights.rules.clientes import ClientesSumidos, ConcentracaoDeClientes
from app.insights.rules.estoque import CapitalParado, PrevisaoDeRuptura, ProdutosEncalhados
from app.insights.rules.financeiro import (
    CampeaoDeLucro,
    ConcentracaoDeProduto,
    FaturamentoEmMovimento,
    MargemEmMovimento,
    TicketMedioEmMovimento,
)
from app.insights.rules.vendas import MelhorDiaDaSemana, VendasDeBalcao

__all__ = [
    "FaturamentoEmMovimento",
    "MargemEmMovimento",
    "TicketMedioEmMovimento",
    "CampeaoDeLucro",
    "ConcentracaoDeProduto",
    "PrevisaoDeRuptura",
    "ProdutosEncalhados",
    "CapitalParado",
    "ClientesSumidos",
    "ConcentracaoDeClientes",
    "MelhorDiaDaSemana",
    "VendasDeBalcao",
]
