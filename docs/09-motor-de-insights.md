# 09 — Motor de Insights (Sprint 3)

> "Não mostramos dados. Explicamos o negócio." — Doc 01 §1

Implementação da área de Insights conforme o ADR 0004: cada insight é uma **regra
independente**, um **motor** roda todas e agrega, Insights **só lê** de Operations,
cálculo **on-read** no MVP.

## O que foi entregue

- **Contrato** (`app/insights/contracts.py`): `Insight { tipo, severidade, titulo,
  mensagem, destaque, acao, valor }` + `InsightContext` (fotografia dos dados do
  tenant) + `RegraDeInsight` (classe base com `avaliar(contexto) -> Insight | None`).
- **Motor** (`app/insights/engine.py`): mantém a lista de regras registradas, roda
  todas sobre o mesmo contexto e devolve ordenado por urgência
  (Alerta → Oportunidade → Info). `motor_padrao()` é o catálogo de regras ativas.
- **12 regras** (`app/insights/rules/`), organizadas por tema:

| Regra | Tipo | Severidade | Financeira? |
|---|---|---|---|
| Faturamento em movimento | `faturamento-em-movimento` | dinâmica (alta/queda/estável) | sim |
| Margem em movimento | `margem-em-movimento` | dinâmica | sim |
| Ticket médio em movimento | `ticket-medio-em-movimento` | dinâmica | sim |
| Campeão de lucro | `campeao-de-lucro` | Info | sim |
| Concentração de produto | `concentracao-de-produto` | Info/Alerta | sim |
| Concentração de clientes | `concentracao-de-clientes` | Info | sim |
| Capital parado | `capital-parado` | Info/Alerta | sim |
| Previsão de ruptura | `previsao-de-ruptura` | Alerta | não |
| Produtos encalhados | `produtos-encalhados` | Alerta | não |
| Clientes sumidos | `clientes-sumidos` | Oportunidade | não |
| Vendas de balcão | `vendas-de-balcao` | Oportunidade | não |
| Melhor dia da semana | `melhor-dia-da-semana` | Info | não |

- **Papel do usuário decide o alcance** (bloqueio no back-end): Admin/SuperAdmin
  recebem tudo; Funcionário só recebe as regras operacionais (`financeiro=False`).
  O papel vem do claim `role` do JWT (`get_current_user_role`); claim desconhecido
  degrada para Funcionário — na dúvida, o menor privilégio.
- **Endpoint**: `GET /api/insights` → `{ geradoEm, resumo, insights[] }`.
- **Aba Insights no frontend**: feed de cards com acento por severidade, destaque
  numérico, frase de negócio e **ação sugerida**; filtros por severidade com
  contagem; estados de loading/erro/vazio; botão de atualizar.
- **Seed**: vendas agora cobrem 90 dias em três faixas de volume crescente
  (18 → 24 → 30), então as janelas móveis do motor encontram crescimento real; dois
  produtos de baixo giro nascem com `created_at` retroativo (75 dias) para o cenário
  de "produto encalhado" existir desde o primeiro boot.
- **Testes**: `tests/test_insights_rules.py` — 14 testes puros (sem banco) cobrindo
  disparo, silêncio, severidade, exclusão de vendas canceladas, filtro por papel e
  ordenação do motor.

## Decisões de projeto das regras

1. **Janelas móveis, não mês-calendário**: comparações usam "últimos 30 dias vs 30
   anteriores". Comparar um mês parcial com o mês fechado anterior geraria "quedas"
   falsas o mês inteiro.
2. **Silêncio é melhor que ruído**: toda regra tem guarda de significância (mínimo de
   vendas, limiar de variação). Uma regra sem nada relevante a dizer devolve `None`
   — a tela não vira um mural de obviedades.
3. **Frase pronta sai do backend**: `mensagem`, `destaque` e `acao` já saem formatados
   (pt-BR) — a tela só dá ênfase, nunca recompõe frase. Formatação centralizada em
   `app/insights/format.py`.
4. **Ação sugerida**: além de explicar o dado, cada insight relevante diz o que fazer
   a seguir — é o que transforma "número" em "decisão" (a régua das 3 perguntas do
   Doc 01).
5. **Severidade é decidida pela regra, não pelo tipo**: o mesmo insight de faturamento
   é oportunidade num mês de alta e alerta num mês de queda.

## Como adicionar um insight novo

1. Crie uma classe em `app/insights/rules/<tema>.py` herdando de `RegraDeInsight`,
   com `tipo` único (kebab-case) e `financeiro = True` se falar de dinheiro.
2. Implemente `avaliar(contexto)` lendo apenas do `InsightContext`; devolva `None`
   quando não houver nada relevante.
3. Registre a instância em `motor_padrao()` (`app/insights/engine.py`).
4. Adicione testes em `tests/test_insights_rules.py` (disparo + silêncio).
5. (Opcional) Mapeie um ícone para o `tipo` novo em
   `frontend/.../features/insights/InsightsPage.tsx` (`iconePorTipo`) — sem
   mapeamento, a tela usa o ícone da severidade como fallback.

Nada mais muda: nem motor, nem service, nem endpoint, nem contrato HTTP.

## O que ficou de fora (de propósito)

- **Pré-cálculo/job**: on-read segue suficiente no volume atual (ADR 0004 aceita o
  risco e já prevê a troca atrás do mesmo contrato).
- **Previsão estatística/IA**: a "previsão" de ruptura é aritmética honesta
  (velocidade de venda × estoque), como o Doc 01 §5 pede para o MVP.
- **Dashboard por papel**: o filtro por papel nasceu aqui (motor); estender ao
  dashboard é o próximo passo natural.
