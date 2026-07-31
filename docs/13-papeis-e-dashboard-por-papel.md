# 13 — Papéis na prática: a vendedora e o dashboard por papel

O papel Funcionário existia no domínio desde a Sprint 1 e o Motor de Insights já
filtrava regras financeiras por papel desde a Sprint 3 — mas nada disso era
**visível**, porque o único login era o SuperAdmin. Esta entrega cria a persona
que faltava e completa o "dashboard por papel" do roadmap (Doc 02 §6.1).

## A persona

| Campo | Valor |
|---|---|
| Nome | Sofia Oliveira |
| Email | `vendedor@bmpcommerce.com` |
| Senha | `Vendedor@123` |
| Papel | Employee (Funcionário) |
| Vínculo | tenant BMP Demo |

Criada pelo seed (idempotente — bancos existentes ganham a usuária no próximo
boot). As vendas de demonstração agora são repartidas aleatoriamente entre o
Administrador e a Sofia — a listagem de vendas mostra vendedores diferentes.

## Dashboard por papel — bloqueio no back-end

`GET /api/dashboard` recebe o papel do JWT e decide **no serviço** o que entregar
(mesma régua `_PAPEIS_FINANCEIROS` do Motor de Insights):

| Dado | Admin/SuperAdmin | Funcionário |
|---|---|---|
| Receita 30d / Ticket médio / Valor de estoque / Receita total | ✔ | `null` |
| Receita por categoria | ✔ | `[]` |
| Série diária | receita + nº de vendas | só nº de vendas (`total: null`) |
| Top produtos | por receita | **por unidades vendidas** (`receita: null`) |
| Vendas 30d (contagem + variação), últimas vendas, estoque em alerta | ✔ | ✔ |

A tela apenas **reage à ausência**: para Funcionário a linha de KPIs vira
Vendas 30d (com sparkline de contagem) + Clientes + Produtos + Estoque em alerta;
o gráfico plota o nº de vendas por dia; o ranking mostra unidades. Nenhum dado
financeiro chega ao navegador para ser "escondido" — a decisão é do servidor.

Insights para a vendedora (já existia, agora demonstrável): apenas regras
operacionais — ruptura, encalhados, clientes sumidos, vendas de balcão, melhor
dia da semana.

## Login

A tela de login ganhou uma seção discreta "contas de demonstração" com dois
atalhos (Administrador / Vendedora) que preenchem o formulário — o fluxo de
autenticação em si não mudou em nada.

## Testes

`tests/test_api_roles.py` (+4, com fixtures de Employee no conftest): login e
perfil da funcionária, dashboard sem financeiro (e com operacional preservado),
dashboard do admin intacto, insights sem tipos financeiros. Suíte completa:
**75 testes**.
