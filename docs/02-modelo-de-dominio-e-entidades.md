# Documento 02 — Modelo de Domínio & Entidades

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Aprovado (base para modelagem física)
**Versão:** 1.0
**Depende de:** Documento 01 — Visão de Produto & Contextos

---

## 1. Convenções aplicadas a TODAS as entidades

```
PADRÃO 1: Toda entidade de tenant tem  → TenantId
PADRÃO 2: Toda entidade tem            → Id (identificador único)
PADRÃO 3: Toda entidade tem auditoria  → CreatedAt, UpdatedAt
PADRÃO 4: Entidades com histórico têm  → IsDeleted (soft delete)
PADRÃO 5: Venda e Produto têm          → RowVersion (concorrência otimista)
```

**Exceção:** `Tenant` e `Usuário Super Admin` pertencem à plataforma, não a um tenant → não têm `TenantId`.

---

## 2. Mapa das Entidades

```
PLATAFORMA (sem TenantId)
├── Tenant
└── Usuário (Super Admin)

TENANT (Operations — com TenantId)
├── Usuário (Admin / Funcionário)
├── Categoria
├── Produto ──────────┐
├── Cliente           │
├── Venda             │
│   └── ItemVenda ────┘ (referencia Produto)
├── PerfilEmpresa (1 por tenant)
└── Configuração (1 por tenant / por usuário)

INSIGHTS (leitura — não cria entidade nova no MVP)
└── lê de Venda, ItemVenda, Produto, Cliente
```

---

## 3. Agregados e Entidades

### 3.1 Tenant *(plataforma)*

Representa a empresa cliente. Unidade de isolamento.

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| Nome | string | obrigatório |
| Plan | enum | MVP: valor único (`Standard`) |
| Status | enum | `Ativo` / `Suspenso` |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Invariantes:**
```
INV 1: Tenant Suspenso → usuários do tenant não autenticam.
INV 2: Nome é obrigatório.
```

---

### 3.2 Usuário *(plataforma OU tenant)*

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid? | null se Super Admin |
| Nome | string | obrigatório |
| Email | string | único, obrigatório |
| SenhaHash | string | nunca guardar senha pura |
| Role | enum | `SuperAdmin` / `Admin` / `Funcionario` |
| FotoPerfil | string? | URL/caminho |
| Status | enum | `Ativo` / `Inativo` |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Invariantes:**
```
INV 1: Role = SuperAdmin  → TenantId é null.
INV 2: Role = Admin/Funcionario → TenantId é obrigatório.
INV 3: Email é único (globalmente).
INV 4: Senha sempre armazenada como hash.
```

---

### 3.3 Categoria *(CRUD simples)*

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid | obrigatório |
| Nome | string | obrigatório, único no tenant |
| Status | enum | `Ativa` / `Inativa` |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Invariantes:**
```
INV 1: Nome único dentro do tenant.
INV 2: Categoria com produtos NÃO pode ser excluída (apenas inativada).
```

---

### 3.4 Produto *(Operations — tem regra de estoque)*

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid | obrigatório |
| Nome | string | obrigatório |
| SKU | string | obrigatório, único no tenant |
| CodigoBarras | string? | **opcional** |
| UnidadeMedida | enum | `Unidade`, `Caixa`, `Pacote`, `Kg`, `Litro`, `Metro`... |
| CategoriaId | Guid | referência |
| PrecoCusto | decimal | ≥ 0 |
| PrecoVenda | decimal | ≥ 0 |
| QuantidadeEstoque | int | ≥ 0 |
| EstoqueMinimo | int | ≥ 0 |
| Status | enum | `Ativo` / `Inativo` |
| RowVersion | byte[] | concorrência |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Invariantes:**
```
INV 1: SKU único no tenant.
INV 2: QuantidadeEstoque nunca fica negativa (MVP).
INV 3: PrecoCusto e PrecoVenda ≥ 0.
INV 4: Produto Inativo não pode ser vendido.
INV 5: UnidadeMedida é obrigatória (default: Unidade).
INV 6: CodigoBarras, se preenchido, é único no tenant.
```

---

### 3.5 Cliente *(CRUD simples)*

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid | obrigatório |
| Nome | string | obrigatório |
| Telefone | string? | opcional |
| Email | string? | opcional |
| CpfCnpj | string? | opcional, válido se preenchido |
| Observacoes | string? | opcional |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Invariantes:**
```
INV 1: Nome é obrigatório.
INV 2: CpfCnpj, se preenchido, deve ser válido.
```

**Permissões (decisão fechada):**
```
Funcionário → cadastrar, editar
Admin       → cadastrar, editar, EXCLUIR
```

---

### 3.6 Venda *(AGGREGATE — raiz)*

Uma venda = **um pedido** = cabeçalho + itens. Cliente é **opcional** (venda de balcão).

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid | obrigatório |
| ClienteId | Guid? | **opcional** (null = balcão) |
| UsuarioId | Guid | quem registrou |
| DataHora | datetime | momento da venda |
| Total | decimal | soma dos itens |
| IsDeleted | bool | soft delete |
| RowVersion | byte[] | concorrência |
| CreatedAt / UpdatedAt | datetime | auditoria |

**Itens (parte do agregado):**

#### ItemVenda

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| VendaId | Guid | pertence à venda |
| ProdutoId | Guid | referência |
| Quantidade | int | > 0 |
| PrecoVendaMomento | decimal | **congelado** na venda |
| PrecoCustoMomento | decimal | **congelado** na venda |
| Subtotal | decimal | Quantidade × PrecoVendaMomento |

**Invariantes do agregado Venda:**
```
INV 1: Venda tem ao menos 1 item.
INV 2: Quantidade de cada item > 0.
INV 3: PrecoVendaMomento e PrecoCustoMomento são copiados
       do produto NO MOMENTO da venda (imutáveis depois).
INV 4: Total = soma dos subtotais dos itens.
INV 5: Venda só conclui se TODOS os itens tiverem estoque suficiente.
       Estoque insuficiente → venda BLOQUEADA (nada é baixado).
INV 6: Venda nunca é deletada fisicamente (IsDeleted).
```

**Fluxo de registro de venda (exemplo completo):**

```
Cenário: vender 3× Produto A (estoque 10, preço R$50, custo R$30)
                    e 2× Produto B (estoque 1, preço R$80, custo R$60)

PASSO 1: Abrir transação.
PASSO 2: Validar Produto A → precisa 3, tem 10 ✔
PASSO 3: Validar Produto B → precisa 2, tem 1 �’
PASSO 4: Estoque insuficiente em B → BLOQUEIA a venda inteira.
         Rollback. Nada é baixado. Usuário informado (INV 5).

--- Repetindo com Produto B tendo estoque 5 ---

PASSO 1: Abrir transação.
PASSO 2: Validar A (3≤10) ✔ e B (2≤5) ✔
PASSO 3: Congelar valores nos itens:
           Item A → preço 50, custo 30, subtotal 150
           Item B → preço 80, custo 60, subtotal 160
PASSO 4: Total = 150 + 160 = R$ 310
PASSO 5: Baixar estoque: A → 10-3=7 ; B → 5-2=3
PASSO 6: Gravar venda + itens.
PASSO 7: Commit (RowVersion protege venda simultânea).
```

---

### 3.7 PerfilEmpresa *(1 por tenant)*

| Campo | Tipo | Regra |
|---|---|---|
| Id | Guid | PK |
| TenantId | Guid | único (1:1) |
| Nome | string | obrigatório |
| Logo | string? | URL/caminho |
| Telefone | string? | opcional |
| Email | string? | opcional |
| Cnpj | string? | opcional |
| Endereco | string? | **opcional** |
| CreatedAt / UpdatedAt | datetime | auditoria |

---

### 3.8 Configuração

Escopo enxuto do MVP.

**Sistema (por tenant ou por usuário):**
| Campo | Valores |
|---|---|
| Tema | `Claro` / `Escuro` |
| Idioma | `pt-BR` (único no MVP) |

**Usuário:**
```
- Alteração de senha
- Foto de perfil (já em Usuário.FotoPerfil)
```

> Nada além disso no MVP.

---

## 4. Relacionamentos

```
Tenant 1 ─── N Usuário
Tenant 1 ─── N Categoria
Tenant 1 ─── N Produto
Tenant 1 ─── N Cliente
Tenant 1 ─── N Venda
Tenant 1 ─── 1 PerfilEmpresa

Categoria 1 ─── N Produto
Cliente   0..1 ─── N Venda     (cliente OPCIONAL)
Usuário   1 ─── N Venda        (quem registrou)
Venda     1 ─── N ItemVenda
Produto   1 ─── N ItemVenda    (referência histórica)
```

---

## 5. Matriz de Permissões (MVP)

| Recurso | Super Admin | Admin | Funcionário |
|---|:---:|:---:|:---:|
| Tenants (todos) | ✔ | — | — |
| Assinaturas | ✔ | — | — |
| Usuários do tenant | — | ✔ | — |
| Produtos | — | ✔ | consultar |
| Categorias | — | ✔ | consultar |
| Estoque | — | ✔ | consultar |
| Clientes | — | ✔ (inclui excluir) | cadastrar/editar |
| Vendas | — | ✔ | registrar |
| Dashboard / Insights | — | ✔ (completo) | ✔ (resumido, sem financeiro) |
| Perfil da Empresa | — | ✔ | — |
| Configurações do sistema | — | ✔ | — |
| Config. próprias (senha/foto) | ✔ | ✔ | ✔ |

---

## 6. Insights do MVP (baseados em regras simples)

Sem previsão, IA ou recomendação avançada nesta versão. Cada item é uma regra sobre dados já existentes.

| Insight | Tipo | Fórmula / origem |
|---|---|---|
| Receita do mês | info | Σ Total das vendas do mês |
| Ticket médio | info | Receita ÷ nº de vendas |
| Produto mais vendido | info | ranking por Σ quantidade |
| Produtos abaixo do estoque mínimo | alerta | QuantidadeEstoque < EstoqueMinimo |
| Produtos sem venda há +30 dias | alerta | última venda por produto |
| Evolução das vendas | info | vendas por período |
| Total de clientes | info | count de Cliente |
| Total vendido | info | Σ Total (acumulado) |

**Exemplo de cálculo — Ticket médio:**
```
Vendas do mês: R$310, R$150, R$540  →  nº vendas = 3
Receita = 310 + 150 + 540 = R$ 1.000
Ticket médio = 1000 ÷ 3 = R$ 333,33
```

**Exemplo — Produtos abaixo do mínimo:**
```
Produto A: estoque 7,  mínimo 5  → OK
Produto B: estoque 3,  mínimo 5  → ALERTA
Produto C: estoque 0,  mínimo 2  → ALERTA
Resultado: [B, C]
```

---

## 6.1 Dashboard por papel (visibilidade)

O mesmo motor de dados, dois níveis de exibição.

```
Admin      → Dashboard COMPLETO
Funcionário → Dashboard RESUMIDO (operacional, sem financeiro)
```

| Indicador | Admin | Funcionário |
|---|:---:|:---:|
| Vendas do dia (qtd) | ✔ | ✔ |
| Quantidade vendida | ✔ | ✔ |
| Produto mais vendido | ✔ | ✔ |
| Produtos abaixo do mínimo | ✔ | ✔ |
| Faturamento consolidado | ✔ | ❌ |
| Margem / Lucro | ✔ | ❌ |
| Ticket médio (R$) | ✔ | ❌ |
| Receita do mês | ✔ | ❌ |

**Regra:**
```
REGRA: Indicadores FINANCEIROS estratégicos (margem, lucro,
       faturamento, receita, ticket em R$) são bloqueados para
       o Funcionário no back-end, não apenas escondidos na tela.
```

---

## 7. Regras transversais (recap crítico)

```
REGRA 1: Todo acesso a dados de tenant filtra por TenantId
         automaticamente (Global Query Filter). Dev não escreve manualmente.

REGRA 2: Super Admin fura o filtro apenas em contexto administrativo.

REGRA 3: Venda que deixaria estoque negativo é bloqueada (MVP).

REGRA 4: Preço e custo são congelados no ItemVenda.

REGRA 5: Vendas usam soft delete — histórico preservado.

REGRA 6: Concorrência otimista (RowVersion) em Produto e Venda.
```

---

## 8. Próximo documento

**Documento 03 — Arquitetura de Solução (Clean Architecture)**: divisão em camadas (Domain, Application, Infrastructure, API), responsabilidades de cada uma, onde vive o Motor de Insights, e como Operations e Insights convivem no mesmo projeto sem acoplamento.
