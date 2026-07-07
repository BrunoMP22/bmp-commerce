# Documento 04 — Plano de Implementação (Sprints)

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Para aprovação
**Versão:** 1.0
**Depende de:** Documentos 01, 02 e 03

---

## 1. Visão geral das sprints

```
SPRINT 0 → Fundação: solução, projetos, convenções, ambiente, repositório
SPRINT 1 → Autenticação + Multi-tenancy + Usuários
SPRINT 2 → Cadastros base: Categorias, Produtos, Clientes
SPRINT 3 → Vendas + baixa de estoque + regras
SPRINT 4 → Dashboard + Motor de Insights
SPRINT 5 → Perfil da Empresa + Configurações + refinamento
SPRINT 6 → Frontend integrado + Docker + entrega do MVP
```

> Ordem por **dependência técnica**: cada sprint só usa o que a anterior entregou.

---

## 2. SPRINT 0 — Fundação (esta é a que você aprova primeiro)

Objetivo: repositório pronto para receber código, com padrões definidos. **Nenhuma regra de negócio ainda.**

```
PASSO 1:  Criar a solução BMPCommerce.sln
PASSO 2:  Criar os 4 projetos backend:
            - BMPCommerce.Domain
            - BMPCommerce.Application
            - BMPCommerce.Infrastructure
            - BMPCommerce.API
PASSO 3:  Configurar as referências entre projetos (regra de dependência).
PASSO 4:  Criar o projeto frontend bmp-commerce-web (React + TS + Tailwind).
PASSO 5:  Definir convenções (nomes, pastas, commits) — ver §8.
PASSO 6:  Configurar EF Core + string de conexão SQL Server.
PASSO 7:  Criar o DbContext vazio + primeira migration (banco base).
PASSO 8:  Configurar Docker (API + SQL Server + frontend).
PASSO 9:  Configurar Swagger na API.
PASSO 10: Configurar Git: .gitignore, README, estrutura de branches.
```

**Entregável da Sprint 0:** projeto que compila, sobe no Docker, conecta no banco e abre o Swagger — vazio, mas de pé.

---

## 3. SPRINT 1 — Autenticação + Multi-tenancy + Usuários

Base de segurança. Tudo depois disso já nasce isolado por tenant.

```
PASSO 1:  Criar entidades Tenant e Usuario (Domain).
PASSO 2:  Implementar PasswordHasher (BCrypt) na Infrastructure.
PASSO 3:  Implementar JwtService (gerar/validar token com TenantId + Role).
PASSO 4:  Implementar TenantContext (lê TenantId do token).
PASSO 5:  Configurar Global Query Filter por TenantId no DbContext.
PASSO 6:  Caso de uso: Login → retorna JWT.
PASSO 7:  Caso de uso: CRUD de Usuário (restrito ao Admin).
PASSO 8:  Middleware de autenticação + autorização por Role.
PASSO 9:  Endpoints REST de auth e usuários.
PASSO 10: Testar isolamento: usuário do Tenant A não vê dados do B.
```

**Entregável:** login funcional, JWT com tenant, isolamento validado.

---

## 4. SPRINT 2 — Cadastros base

CRUD dos dados que a Venda vai precisar.

```
PASSO 1: Categoria (entidade + CRUD + regra: não excluir com produtos).
PASSO 2: Produto (entidade + CRUD).
           - campos: SKU, CodigoBarras, UnidadeMedida, custo, preço,
             estoque, mínimo, status.
           - invariantes: SKU único, estoque ≥ 0, unidade obrigatória.
PASSO 3: Cliente (entidade + CRUD).
           - permissões: Funcionário cadastra/edita; Admin exclui.
PASSO 4: Endpoints REST dos três recursos.
PASSO 5: Validações (FluentValidation).
```

**Entregável:** cadastros completos e isolados por tenant.

---

## 5. SPRINT 3 — Vendas (o coração transacional)

```
PASSO 1: Criar agregado Venda + ItemVenda (Domain).
PASSO 2: Implementar invariantes:
           - venda tem ≥ 1 item
           - quantidade > 0
           - congelar preço/custo no item
           - bloquear se algum item sem estoque (venda inteira)
PASSO 3: Caso de uso RegistrarVenda:
           - transação
           - validar estoque de todos os itens
           - baixar estoque
           - gravar venda + itens
PASSO 4: Configurar RowVersion (concorrência) em Produto e Venda.
PASSO 5: Caso de uso: listar/consultar vendas.
PASSO 6: Soft delete de venda.
PASSO 7: Endpoints REST de vendas.
```

**Entregável:** venda de balcão (sem cliente) e com cliente, com baixa de estoque correta e bloqueio funcionando.

---

## 6. SPRINT 4 — Dashboard + Insights

```
PASSO 1: Definir o contrato do Insight (tipo, severidade, mensagem, valor).
PASSO 2: Criar o Motor de Insights (roda a lista de regras).
PASSO 3: Implementar as 8 regras do MVP (Doc 02 §6):
           receita do mês, ticket médio, mais vendido,
           abaixo do mínimo, sem venda +30 dias, evolução,
           total de clientes, total vendido.
PASSO 4: Caso de uso ObterDashboard recebe a Role:
           - Admin → dashboard completo (com financeiro)
           - Funcionário → resumido (sem financeiro), bloqueio no back-end
PASSO 5: Endpoints REST do dashboard e insights.
```

**Entregável:** área de Insights entregando frases de negócio + dashboard nos dois níveis.

---

## 7. SPRINT 5 e 6

**SPRINT 5 — Perfil + Configurações + refino**
```
PASSO 1: PerfilEmpresa (1 por tenant) + upload de logo.
PASSO 2: Configurações: tema claro/escuro, idioma pt-BR.
PASSO 3: Alteração de senha + foto de perfil do usuário.
PASSO 4: Revisão de erros, mensagens e validações.
```

**SPRINT 6 — Frontend integrado + entrega**
```
PASSO 1: Telas React consumindo a API (login, produtos, vendas, dashboard).
PASSO 2: Tailwind + tema claro/escuro.
PASSO 3: Docker compose final (API + SQL + web).
PASSO 4: Testes de ponta a ponta do fluxo principal.
PASSO 5: Entrega do MVP.
```

---

## 8. Convenções do projeto (definidas na Sprint 0)

```
NOMES:
  - Projetos: BMPCommerce.<Camada>
  - Classes: PascalCase
  - Interfaces: I + PascalCase (IProdutoRepository)
  - Casos de uso: Verbo + Substantivo (RegistrarVenda)

PASTAS (Application):
  - Operations/<Recurso>/  → casos de uso transacionais
  - Insights/              → motor e regras

COMMITS (Conventional Commits):
  - feat: nova funcionalidade
  - fix: correção
  - chore: config/infra
  - docs: documentação
  - refactor: refatoração

BRANCHES:
  - main       → estável
  - develop    → integração
  - feature/*  → cada funcionalidade
```

---

## 9. Exemplo completo — o que a Sprint 0 produz na prática

```
CENÁRIO: rodar o projeto pela primeira vez após a Sprint 0.

PASSO 1: git clone do repositório
PASSO 2: docker compose up
           → sobe SQL Server
           → sobe API (BMPCommerce.API)
           → sobe frontend (bmp-commerce-web)
PASSO 3: API aplica a migration inicial → cria o banco vazio
PASSO 4: abrir https://localhost:xxxx/swagger
           → Swagger abre, sem endpoints de negócio ainda
PASSO 5: abrir o frontend → tela inicial em branco/placeholder

RESULTADO: ambiente 100% de pé, pronto para a Sprint 1.
           Zero regra de negócio. Zero risco acumulado.
```

---

## 10. Dependências entre sprints (resumo visual)

```
Sprint 0 (fundação)
   └─▶ Sprint 1 (auth + tenant)      ← tudo depende de isolamento
          └─▶ Sprint 2 (cadastros)
                 └─▶ Sprint 3 (vendas)   ← precisa de produtos
                        └─▶ Sprint 4 (dashboard/insights) ← precisa de vendas
                               └─▶ Sprint 5 (perfil/config)
                                      └─▶ Sprint 6 (frontend + entrega)
```

---

## 11. Aprovação

Para começarmos, preciso do seu **ok na Sprint 0** (§2 e §8).

```
DECISÃO 1: Aprova a divisão de sprints (§1)?
DECISÃO 2: Aprova o escopo e os 10 passos da Sprint 0 (§2)?
DECISÃO 3: Aprova as convenções (§8)?
```

Aprovado, eu começo a **executar a Sprint 0** (aí sim, criando solução, projetos e arquivos de configuração).
