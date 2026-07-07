# Documento 01 — Visão de Produto & Contextos

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Aprovado (base para modelagem)
**Versão:** 1.0

---

## 1. Visão do Produto

BMP Commerce é uma plataforma **SaaS B2B** de gestão comercial e inteligência de dados para pequenas e médias empresas.

Não competimos com grandes ERPs. Entregamos uma solução simples, moderna e intuitiva para o empresário controlar o negócio e decidir com base em dados.

### Lema do produto

> **Não mostramos dados. Explicamos o negócio.**

### Filtro de escopo (regra das 3 perguntas)

Toda funcionalidade candidata precisa responder **sim** a pelo menos uma:

1. Ajuda o cliente a **vender mais**?
2. Ajuda o cliente a **economizar tempo**?
3. Ajuda o cliente a **tomar uma decisão melhor**?

Se a resposta for não → não entra no MVP.

---

## 2. Modelo de Negócio

| Item | Definição MVP | Futuro |
|---|---|---|
| Tipo | SaaS B2B | — |
| Cobrança | Assinatura mensal | Basic / Pro / Enterprise |
| Planos | 1 plano único | Múltiplos planos |
| Acesso | `bmpcommerce.com` (login) | Subdomínios por empresa |

**Decisão:** não construir motor de planos agora. Apenas um campo `Plan` no Tenant.

---

## 3. Personas e Papéis

```
PASSO 1: Super Admin BMP   → administra a plataforma (todos os tenants)
PASSO 2: Admin da Empresa  → controle total de UM tenant
PASSO 3: Funcionário       → operação limitada, sem acesso administrativo
```

| Papel | Escopo | Pode fazer |
|---|---|---|
| **Super Admin BMP** | Plataforma | Ver todos os tenants, gerenciar assinaturas, gerenciar usuários, métricas gerais |
| **Admin da Empresa** | 1 tenant | Usuários, produtos, vendas, estoque, dashboard, clientes, configurações |
| **Funcionário** | 1 tenant | Registrar vendas, consultar produtos, consultar clientes |

**Regra de acesso:** Super Admin vive em contexto administrativo separado. Não compartilha a camada de acesso do "app da empresa".

---

## 4. Escopo do MVP

### Dentro do MVP

- Autenticação (JWT)
- Gestão de Usuários
- Produtos
- Categorias
- Estoque
- Clientes (simples)
- Registro de Vendas
- Dashboard Executivo
- **Insights** (diferencial da BMP)
- Perfil da Empresa
- Configurações

### Fora do MVP (registrado, não construído)

Compras · Fornecedores · Financeiro · Fluxo de Caixa · Contas a Pagar/Receber · Nota Fiscal · Integrações · API Pública · Marketplace · App Mobile · IA · Alertas Inteligentes

---

## 5. Bounded Contexts (o coração da arquitetura)

O produto tem **dois contextos**. É isso que separa a BMP de "qualquer sistema".

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   OPERATIONS                │     │   INSIGHTS                  │
│   (núcleo transacional)     │ ──▶ │   (leitura / analytics)     │
│                             │     │                             │
│ Escrever dados corretos     │     │ Interpretar e explicar      │
│                             │     │                             │
│ Produtos, Categorias,       │     │ Consome dados de Operations │
│ Estoque, Vendas, Clientes,  │     │ e produz frases de negócio  │
│ Usuários                    │     │                             │
└─────────────────────────────┘     └─────────────────────────────┘
```

| | Operations | Insights |
|---|---|---|
| **Foco** | Correção dos dados | Interpretação dos dados |
| **Ritmo de mudança** | Estável | Muda rápido (nova regra toda semana) |
| **Padrão** | DDD onde há regra; CRUD onde não há | Motor de regras plugáveis |
| **Direção do dado** | Fonte da verdade | Somente leitura |

**Por que separar:** adicionar um novo insight **não pode tocar** no código de vendas/estoque. Insights isolados = evolução barata do diferencial.

---

## 6. Onde aplicar DDD (evitar overengineering)

```
PASSO 1: DDD real     → Venda, Estoque, Insights   (têm regra de negócio)
PASSO 2: CRUD honesto → Categoria, Cliente, Perfil da Empresa, Configurações
PASSO 3: Nunca        → aggregate/value object/domain event em CRUD puro
```

---

## 7. Agregados e Entidades (definidos)

### 7.1 Produto *(Operations)*

| Campo | Observação |
|---|---|
| Nome | |
| SKU | |
| Categoria | referência |
| Preço de custo | necessário p/ margem/lucro |
| Preço de venda | |
| Quantidade em estoque | |
| Estoque mínimo | base p/ alertas |
| Status | ativo/inativo |

> Guardar **custo e preço** é obrigatório: sem custo, não há Insight de margem.

### 7.2 Cliente *(Operations — simples)*

| Campo |
|---|
| Nome |
| Telefone |
| E-mail |
| CPF/CNPJ |
| Observações |

> Sem endereço, crédito ou limite no MVP.

### 7.3 Venda *(Operations — aggregate)*

Uma venda representa **um pedido** = cabeçalho + coleção de itens.

```
Venda (raiz do agregado)
├── Cliente (opcional?)   ← decisão pendente, ver §10
├── Data/hora
├── Total
└── Itens[]
    ├── Produto
    ├── Quantidade
    ├── Preço de venda no momento
    └── Custo no momento   ← "congela" custo p/ margem histórica
```

**Regra crítica:** preço e custo são **copiados no momento da venda**. Se o produto mudar de preço depois, a margem histórica não pode mudar.

### 7.4 Categoria · Usuário · Perfil da Empresa · Configurações

CRUD simples. Sem agregado.

---

## 8. Regras de Negócio já decididas

```
REGRA 1 (Estoque bloqueante):
  Venda que deixaria estoque negativo é BLOQUEADA.
  Estoque insuficiente → venda não conclui + usuário informado.
  (Configuração p/ permitir negativo = fora do MVP.)

REGRA 2 (Baixa de estoque):
  A baixa ocorre dentro da mesma transação da venda.
  Concorrência otimista (RowVersion) evita estoque errado
  em vendas simultâneas.

REGRA 3 (Congelamento de valores):
  Cada item de venda grava preço e custo do momento.
  Histórico é imutável — base para todo Insight de margem/lucro.

REGRA 4 (Histórico preservado):
  Vendas nunca são deletadas fisicamente (soft delete).
  Sem histórico não existe Insight nem previsão.
```

---

## 9. Motor de Insights (visão funcional)

Cada insight é uma **regra independente**.

```
PASSO 1: Cada insight = 1 regra isolada (uma classe/função).
PASSO 2: A regra recebe os dados do tenant e devolve — ou não — um Insight.
PASSO 3: Um Insight tem: tipo, severidade, mensagem, valor numérico.
PASSO 4: O motor roda todas as regras e devolve a lista para a tela.
PASSO 5: Adicionar insight novo = adicionar 1 regra. Nada mais muda.
```

**Severidades:** `info` · `alerta` · `oportunidade`

Mapa dos insights de referência (todos passam na regra das 3 perguntas → "decidir melhor"):

| Insight | Severidade | Dado necessário |
|---|---|---|
| Faturamento +14% no mês | oportunidade | vendas mês atual vs anterior |
| "Capacete X" sem venda há 47 dias | alerta | última venda por produto |
| Produto = 28% do faturamento | info | ranking de lucro |
| Sem estoque do Produto A em ~12 dias | alerta (previsão) | estoque + velocidade de venda |
| 8 clientes = 42% da receita | info | concentração de receita |
| Margem caiu 6% no mês | alerta | margem mês atual vs anterior |

**Decisão MVP — cálculo on-read:** insights são calculados na hora, com queries agregadas bem feitas (pouco dado por tenant no início). A interface do motor será desenhada para trocar por **pré-cálculo (job)** no futuro **sem quebrar nada**.

---

## 10. Linguagem Ubíqua (glossário)

| Termo | Significado no BMP Commerce |
|---|---|
| **Tenant** | Empresa cliente. Unidade de isolamento de dados. |
| **Produto** | Item vendável, com custo, preço, estoque e mínimo. |
| **Categoria** | Agrupador de produtos. |
| **Cliente** | Quem compra da empresa (não o usuário do sistema). |
| **Usuário** | Pessoa que acessa o sistema (Super Admin / Admin / Funcionário). |
| **Venda** | Pedido com um ou mais itens. Baixa estoque. |
| **Item de Venda** | Linha da venda: produto + qtd + preço/custo congelados. |
| **Estoque** | Quantidade disponível de um produto. |
| **Estoque mínimo** | Limite que dispara alerta. |
| **Insight** | Frase de negócio interpretada a partir dos dados. |
| **Dashboard** | Visão executiva com números e gráficos. |

---

## 11. Riscos & Mitigações (registro)

| # | Risco | Mitigação |
|---|---|---|
| R1 | Vazamento de dados entre tenants | TenantId do JWT + Global Query Filter automático no EF Core |
| R2 | Super Admin precisa furar o filtro | Bypass explícito e restrito ao contexto administrativo |
| R3 | DDD virar overengineering | DDD só em Venda/Estoque/Insights; resto é CRUD |
| R4 | Estoque errado em venda simultânea | Transação + concorrência otimista (RowVersion) |
| R5 | Insights degradarem o banco | Separar leitura (analytics) da escrita; on-read agora, pré-cálculo depois |
| R6 | Previsão sem histórico | Soft delete de vendas + data/hora precisa |

---

## 12. Decisões pendentes (para o Documento 02)

```
PENDENTE 1: Venda exige Cliente ou o cliente é opcional?
            (Ex.: venda de balcão sem identificar o cliente.)

PENDENTE 2: Funcionário pode CADASTRAR cliente ou só consultar?

PENDENTE 3: O que exatamente entra em "Configurações" no MVP?

PENDENTE 4: Insights aparecem já no MVP ou entram logo após?
            (Impacta ordem de construção, não a arquitetura.)
```

---

## 13. Próximo documento

**Documento 02 — Modelo de Domínio & Entidades**: detalhamento dos agregados, atributos, invariantes e relacionamentos, já com TenantId em todas as entidades e as regras de estoque/venda formalizadas.
