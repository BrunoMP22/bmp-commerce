# 0004 - Insights como motor de regras

**Status:** aceita
**Data:** 2026-07-06

## Contexto

Insights é o diferencial do produto ("Não mostramos dados. Explicamos o
negócio." — Doc 01 §1) e o contexto que muda mais rápido: nova regra de
negócio toda semana, sem previsão, IA ou recomendação avançada no MVP
(Doc 01 §5, §9). Era preciso uma forma de adicionar/alterar um insight **sem
tocar** no código de vendas, estoque ou produtos (Doc 01 §5), e sem transformar
cada novo insight em uma mudança estrutural no motor.

## Decisão

Cada insight é uma regra independente que implementa um contrato comum: recebe
os dados do tenant e devolve, ou não, um `Insight { Tipo, Severidade, Mensagem,
Valor }` (Doc 01 §9, Doc 03 §5). Um **Motor de Insights** mantém a lista de
regras registradas, roda todas ao ser solicitado e agrega o resultado
(Doc 03 §5 Passo 3-4). Adicionar um insight novo = adicionar uma classe nova
registrada no motor; o motor em si não muda (Doc 01 §9 Passo 5, Doc 03 §5
Passo 5).

Isolamento de contexto: Insights lê de Operations (Venda, ItemVenda, Produto,
Cliente) mas nunca escreve; Operations não conhece Insights (Doc 02 §2,
Doc 03 §4 REGRA).

Cálculo é **on-read** no MVP — cada insight roda como query agregada no
momento da consulta, sem pré-cálculo/job. A interface do motor é desenhada
para trocar isso por pré-cálculo no futuro sem quebrar contrato (Doc 01 §9,
Doc 03 §10 DECIDIDO 3).

O caso de uso `ObterDashboard` recebe a Role do usuário: Admin roda todas as
regras (inclui financeiras); Funcionário roda só as operacionais — bloqueio no
back-end, nunca só na tela (Doc 02 §6.1, Doc 03 §5).

## Consequências

**Prós:**
- Novo insight nunca é uma mudança arriscada: é uma classe nova, isolada,
  registrada no motor.
- Insights não pode corromper dados de Operations, porque só lê.
- Trocar on-read por pré-cálculo no futuro é uma mudança de implementação
  atrás do mesmo contrato, não uma reescrita.

**Contras / riscos aceitos:**
- Cálculo on-read pode degradar performance conforme o volume de dados por
  tenant cresce (Doc 01 §11 R5) — aceito no MVP porque o volume inicial é
  baixo; mitigação futura já prevista (pré-cálculo/job) sem mudar o contrato
  do motor.
- Exige disciplina do time para não deixar nenhuma regra de Insights escrever
  dado — a regra de isolamento (Doc 03 §4) não é imposta pelo compilador,
  é uma convenção de code review.
