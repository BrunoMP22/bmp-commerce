# Documento 03 — Arquitetura de Solução (Clean Architecture)

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Aprovado (base para estruturação do projeto)
**Versão:** 1.0
**Depende de:** Documentos 01 e 02

---

## 1. As 4 camadas (visão geral)

```
PASSO 1: Domain          → regras de negócio puras (o coração)
PASSO 2: Application      → casos de uso (orquestra o Domain)
PASSO 3: Infrastructure   → banco, JWT, e-mail, arquivos (detalhes técnicos)
PASSO 4: API              → entrada HTTP (controllers REST)
```

**Regra de dependência (a mais importante):**
```
API ──▶ Application ──▶ Domain ◀── Infrastructure

- Domain NÃO depende de ninguém.
- Application depende só do Domain.
- Infrastructure e API dependem para dentro.
- A seta SEMPRE aponta para o Domain.
```

Traduzindo: o Domain não sabe que existe SQL Server, EF Core, JWT ou React. Ele só conhece as regras do negócio.

---

## 2. O que vive em cada camada

### 2.1 Domain (BMPCommerce.Domain)

Regras puras. Sem EF Core, sem HTTP, sem nada externo.

```
- Entidades:        Tenant, Usuario, Produto, Categoria,
                    Cliente, Venda, ItemVenda, PerfilEmpresa
- Value Objects:    CpfCnpj, Dinheiro (opcional no MVP)
- Enums:            Role, StatusProduto, UnidadeMedida, Tema...
- Invariantes:      as regras INV do Documento 02
- Interfaces de repositório:  IProdutoRepository, IVendaRepository...
```

> As **interfaces** dos repositórios ficam no Domain. As **implementações** ficam na Infrastructure. Assim o Domain define o contrato sem conhecer o SQL.

### 2.2 Application (BMPCommerce.Application)

Casos de uso. Orquestra as entidades para realizar uma ação.

```
- Casos de uso:     RegistrarVenda, CadastrarProduto,
                    ListarProdutosAbaixoDoMinimo, CalcularInsights...
- DTOs:             entrada/saída dos casos de uso
- Interfaces de serviços:  ITenantContext, IJwtService, IPasswordHasher
- Validações de aplicação (FluentValidation)
- MOTOR DE INSIGHTS (ver §5)
```

### 2.3 Infrastructure (BMPCommerce.Infrastructure)

Os "detalhes" técnicos. Implementa o que o Domain e a Application pediram.

```
- DbContext (EF Core) + Global Query Filter por TenantId
- Implementação dos repositórios
- Migrations
- JwtService, PasswordHasher (BCrypt)
- Serviços de e-mail, upload de logo/foto
- TenantContext (resolve TenantId do usuário logado)
```

### 2.4 API (BMPCommerce.API)

Porta de entrada REST.

```
- Controllers (endpoints REST)
- Middlewares (autenticação, tenant, erros)
- Configuração de DI, JWT, CORS, Swagger
- Program.cs
```

---

## 3. Onde cada regra crítica é implementada

| Regra (Doc 01/02) | Camada | Como |
|---|---|---|
| Filtro automático por TenantId | Infrastructure | Global Query Filter no DbContext |
| Resolver TenantId do usuário | Infrastructure | `TenantContext` (lê do JWT) |
| Bloquear estoque negativo | Domain + Application | invariante no agregado Venda + transação |
| Congelar preço/custo no item | Domain | dentro do agregado Venda |
| Concorrência otimista | Infrastructure | `RowVersion` mapeado no EF |
| Super Admin fura o filtro | Application | contexto administrativo separado |
| Funcionário sem financeiro | Application | caso de uso do dashboard filtra por Role |

---

## 4. Contextos Operations x Insights na prática

Os dois bounded contexts (Doc 01) **não** viram dois projetos separados no MVP. Convivem no mesmo Application, mas **isolados por pasta e sem acoplamento**.

```
Application/
├── Operations/     ← casos de uso transacionais
│   ├── Produtos/
│   ├── Vendas/
│   ├── Clientes/
│   └── ...
└── Insights/       ← motor de leitura/analytics
    ├── Regras/
    └── MotorDeInsights
```

**Regra de isolamento:**
```
REGRA: Insights LÊ dos dados de Operations, mas nunca escreve.
       Operations NÃO conhece Insights.
       Adicionar/alterar um insight não toca em nenhum caso de uso
       de venda, produto ou estoque.
```

---

## 5. Motor de Insights (detalhe da implementação)

Cada insight = uma regra independente que segue um contrato comum.

```
PASSO 1: Definir um contrato:  toda regra recebe os dados do tenant
         e devolve, ou não, um Insight.
PASSO 2: Cada insight vira uma classe que implementa esse contrato.
PASSO 3: O Motor tem a LISTA de regras registradas.
PASSO 4: Ao pedir insights, o Motor roda todas as regras e junta o resultado.
PASSO 5: Novo insight = nova classe registrada. O Motor não muda.
```

**Estrutura de um Insight (saída):**
```
Insight {
    Tipo         → ex: "ProdutoSemVenda"
    Severidade   → info | alerta | oportunidade
    Mensagem     → "Produto X sem venda há 32 dias"
    Valor        → número associado (ex: 32)
}
```

**Exemplo completo — regra "Produtos abaixo do estoque mínimo":**
```
ENTRADA: produtos do tenant
  Produto A: estoque 7, mínimo 5
  Produto B: estoque 3, mínimo 5
  Produto C: estoque 0, mínimo 2

PASSO 1: Filtrar produtos onde estoque < mínimo → [B, C]
PASSO 2: Se lista vazia → não gera insight.
PASSO 3: Lista tem itens → gerar:
         Insight {
           Tipo: "EstoqueAbaixoDoMinimo",
           Severidade: alerta,
           Mensagem: "2 produtos abaixo do estoque mínimo",
           Valor: 2
         }
SAÍDA: 1 insight de alerta.
```

**Como o dashboard resumido do Funcionário se encaixa:**
```
REGRA: O caso de uso "ObterDashboard" recebe a Role do usuário.
       - Admin       → roda TODAS as regras (inclui financeiras).
       - Funcionário → roda apenas regras OPERACIONAIS.
       O bloqueio é no back-end, nunca só na tela.
```

---

## 6. Fluxo de uma requisição (exemplo ponta a ponta)

Cenário: Funcionário registra uma venda via `POST /api/vendas`.

```
PASSO 1:  API recebe a requisição.
PASSO 2:  Middleware de autenticação valida o JWT.
PASSO 3:  Middleware/serviço de tenant extrai o TenantId do token.
PASSO 4:  Controller chama o caso de uso RegistrarVenda (Application).
PASSO 5:  Application carrega os produtos via IProdutoRepository.
PASSO 6:  Domain valida invariantes:
            - todos os itens têm estoque? (INV 5)
            - quantidade > 0? congela preço/custo?
PASSO 7:  Falhou estoque → retorna erro, nada é salvo (rollback).
PASSO 8:  OK → Application abre transação, baixa estoque, grava venda.
PASSO 9:  Infrastructure persiste (EF Core) com Global Query Filter
          garantindo o TenantId. RowVersion protege concorrência.
PASSO 10: Controller devolve 201 Created + dados da venda.
```

---

## 7. Isolamento de Tenant (segurança) — a espinha dorsal

```
PASSO 1: Usuário faz login → recebe JWT contendo TenantId e Role.
PASSO 2: A cada requisição, o TenantContext lê o TenantId do token.
PASSO 3: O DbContext aplica Global Query Filter:
           toda query recebe "WHERE TenantId = {atual}" automaticamente.
PASSO 4: O desenvolvedor NUNCA escreve o filtro manualmente.
PASSO 5: Super Admin usa contexto administrativo que ignora o filtro
           (IgnoreQueryFilters), isolado do app da empresa.
```

**Por que isso protege:** mesmo que um caso de uso esqueça de filtrar, o banco só devolve dados do tenant atual. É defesa em profundidade.

---

## 8. Stack por camada (recap)

| Camada | Tecnologias |
|---|---|
| Domain | C# puro (sem dependências externas) |
| Application | C#, FluentValidation, MediatR (opcional) |
| Infrastructure | EF Core, SQL Server, BCrypt, JWT |
| API | ASP.NET Core 9, Swagger, JWT middleware |
| Frontend | React + TypeScript + Tailwind (consome a REST API) |
| Deploy | Docker |

> **Nota sobre MediatR:** opcional. Se o time achar que adiciona complexidade sem ganho no MVP, os casos de uso podem ser serviços simples. Decisão a registrar no Documento 04.

---

## 9. Estrutura de projetos (.sln) — visão lógica

> Ainda **não** é estrutura de pastas de código. É a divisão lógica de projetos.

```
BMPCommerce.sln
├── BMPCommerce.Domain          (núcleo, sem dependências)
├── BMPCommerce.Application      (depende de Domain)
├── BMPCommerce.Infrastructure   (depende de Application + Domain)
├── BMPCommerce.API              (depende de Application + Infrastructure)
└── bmp-commerce-web/            (React + TS, projeto separado)
```

---

## 10. Decisões fechadas

```
DECIDIDO 1: Casos de uso = SERVIÇOS SIMPLES (sem MediatR no MVP).
DECIDIDO 2: Value Objects (CpfCnpj, Dinheiro) → opcionais, avaliar na
            implementação. Não bloqueiam o MVP.
DECIDIDO 3: Insights on-read confirmado.
DECIDIDO 4: Metas FORA do MVP. Dashboard do Funcionário mostra apenas
            indicadores operacionais das próprias atividades, sem metas.
```

---

## 11. Próximo documento

**Documento 04 — Especificação da API REST**: endpoints, verbos, contratos de request/response, códigos de status e regras de autorização por papel para cada rota.
