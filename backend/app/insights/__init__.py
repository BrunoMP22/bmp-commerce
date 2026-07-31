"""Contexto Insights (ADR 0004) — "Não mostramos dados. Explicamos o negócio."

Regras de leitura deste pacote:
  - Insights LÊ dos dados de Operations (Venda, ItemVenda, Produto, Cliente),
    mas NUNCA escreve (Doc 03 §4 REGRA).
  - Cada insight é uma regra independente registrada no motor; adicionar um
    insight novo = adicionar uma classe nova em `rules/` e registrá-la em
    `engine.motor_padrao()`. Nada mais muda.
  - Cálculo on-read no MVP: cada requisição roda as regras sobre os dados do
    momento. O contrato do motor permite trocar por pré-cálculo sem quebrar nada.
"""

from app.insights.contracts import Insight, InsightContext, RegraDeInsight, Severidade
from app.insights.engine import MotorDeInsights, motor_padrao

__all__ = [
    "Insight",
    "InsightContext",
    "RegraDeInsight",
    "Severidade",
    "MotorDeInsights",
    "motor_padrao",
]
