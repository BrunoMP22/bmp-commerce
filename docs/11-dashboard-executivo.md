# 11 — Repaginada de UI: Dashboard executivo

Primeira entrega da repaginada visual do produto: o Dashboard deixou de ser uma
grade de contadores acumulados e virou uma visão executiva de 30 dias.

## O que mudou

### Backend — um endpoint, todos os dados

`GET /api/dashboard` agora agrega tudo que a tela precisa em uma chamada:

- **KPIs de janela** (`receita30Dias`, `vendas30Dias`, `ticketMedio30Dias`):
  últimos 30 dias vs 30 anteriores, com `variacaoPercentual` (null sem base) —
  a **mesma régua do Motor de Insights**, para dashboard e Insights nunca
  discordarem sobre "crescimento".
- `vendasPorDia`: 30 dias (antes 14).
- `receitaPorCategoria`: top 3 categorias + "Outras" (teto de 4 séries — limite
  validado da paleta categórica), com participação percentual.
- `topProdutos`: top 5 por receita na janela, com quantidade.
- `ultimasVendas`: 6 mais recentes, incluindo canceladas (com flag — o dashboard
  mostra a operação como ela é).
- `estoqueEmAlerta`: produtos ativos abaixo do mínimo, sem estoque primeiro.
- Totais históricos preservados (receita total, contagens) para a linha de rodapé.

### Frontend — desenho guiado por método (dataviz)

- **KPI row**: 4 stat tiles com delta assinado ("+69% vs 30 dias anteriores",
  verde/vermelho por direção) e sparkline de 30 dias no tile de receita.
- **Gráfico de receita (30 dias)**: área com wash de ~10% de opacidade, linha 2px,
  grid hairline sólido só horizontal, tooltip com crosshair mostrando receita e
  nº de vendas do dia. Série única → sem legenda (o título nomeia a série).
- **Receita por categoria**: barra empilhada horizontal (part-to-whole) com vãos
  de 2px na cor da superfície + legenda com swatch, % e valor — os rótulos
  visíveis são a "relief rule" da paleta clara.
- **Top produtos**: lista ranqueada com barra de magnitude (um matiz único) e
  valores à direita; **Últimas vendas** e **Estoque em alerta** como listas com
  badges de status (ícone + texto, nunca cor sozinha).
- Saudação por horário + data, atalhos "Nova venda" / "Ver insights",
  skeletons/erro/vazio em todos os blocos.

### Paleta dos gráficos — validada, não estimada

Slots categóricos definidos como CSS vars (`--chart-1..4`) em `index.css`, um
conjunto por tema, **validados com o script de checagem de paleta** (banda de
luminosidade, croma, separação para daltonismo, piso de visão normal, contraste)
sobre as superfícies reais do app:

- Claro (`#ffffff`): `#2563eb, #eb6834, #1baf7a, #eda100` — tudo PASS; aviso de
  contraste em aqua/amarelo mitigado por rótulos visíveis na legenda.
- Escuro (`#14171d`): `#3b82f6, #d95926, #199e70, #c98500` — tudo PASS.

Regra: ordem fixa, nunca ciclar além dos 4 slots — categorias excedentes dobram
em "Outras" (o serviço já entrega assim).

## Testes

`tests/test_api_dashboard.py` (+3): dashboard vazio (zeros, 30 pontos, listas
vazias), agregação com vendas (janela, top, categorias somando 100%, gráfico) e
ordenação do estoque em alerta. Suíte completa: **63 testes**.
