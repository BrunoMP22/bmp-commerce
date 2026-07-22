# Documento 05 — Estrutura do Monorepo

**Projeto:** BMP Commerce
**Status:** Para validação (estrutura de diretórios — sem código)
**Versão:** 1.0

> **Nota (2026-07-22):** a árvore de diretórios abaixo reflete a estrutura original em
> .NET (Sprint 0). O backend foi migrado para Python/FastAPI — a estrutura atual de
> `backend/` está descrita no [README raiz](../README.md#arquitetura) e em
> [backend/README.md](../backend/README.md); o mapeamento completo está em
> [ADR 0005](ADR/0005-migracao-backend-dotnet-para-python-fastapi.md) e
> [docs/08](08-migracao-backend-python-fastapi.md). `frontend/`, `docs/` e `infra/`
> continuam como descrito aqui. Preservado abaixo como registro histórico.

---

## 1. Ajustes incorporados

```
AJUSTE 1: Monorepo → backend + frontend + docs + infra juntos.
AJUSTE 2: Pasta docs/ADR para decisões arquiteturais.
AJUSTE 3: Frontend evolui junto com cada sprint (não só no fim).
AJUSTE 4: Sprint 0 prioriza rodar LOCAL (compilar + conectar banco)
          antes da configuração completa de containers.
```

---

## 2. Estrutura completa do monorepo

```
bmp-commerce/
│
├── README.md
├── .gitignore
├── .editorconfig
├── LICENSE
│
├── backend/
│   ├── BMPCommerce.sln
│   │
│   ├── src/
│   │   ├── BMPCommerce.Domain/
│   │   │   ├── Entities/
│   │   │   ├── Enums/
│   │   │   ├── ValueObjects/
│   │   │   ├── Interfaces/            (contratos de repositório)
│   │   │   └── BMPCommerce.Domain.csproj
│   │   │
│   │   ├── BMPCommerce.Application/
│   │   │   ├── Operations/           (casos de uso transacionais)
│   │   │   │   ├── Usuarios/
│   │   │   │   ├── Categorias/
│   │   │   │   ├── Produtos/
│   │   │   │   ├── Clientes/
│   │   │   │   └── Vendas/
│   │   │   ├── Insights/             (motor + regras)
│   │   │   │   ├── Motor/
│   │   │   │   └── Regras/
│   │   │   ├── Common/               (DTOs, interfaces de serviço)
│   │   │   └── BMPCommerce.Application.csproj
│   │   │
│   │   ├── BMPCommerce.Infrastructure/
│   │   │   ├── Persistence/
│   │   │   │   ├── DbContext/
│   │   │   │   ├── Configurations/   (mapeamentos EF)
│   │   │   │   ├── Repositories/
│   │   │   │   └── Migrations/
│   │   │   ├── Security/             (JwtService, PasswordHasher)
│   │   │   ├── Tenancy/              (TenantContext)
│   │   │   ├── Services/             (e-mail, upload)
│   │   │   └── BMPCommerce.Infrastructure.csproj
│   │   │
│   │   └── BMPCommerce.API/
│   │       ├── Controllers/
│   │       ├── Middlewares/
│   │       ├── appsettings.json
│   │       ├── appsettings.Development.json
│   │       ├── Program.cs
│   │       └── BMPCommerce.API.csproj
│   │
│   └── tests/                        (preparado, preenchido nas sprints)
│       ├── BMPCommerce.UnitTests/
│       └── BMPCommerce.IntegrationTests/
│
├── frontend/
│   └── bmp-commerce-web/
│       ├── public/
│       ├── src/
│       │   ├── api/                  (chamadas à REST API)
│       │   ├── components/           (componentes reutilizáveis)
│       │   ├── features/             (por domínio: produtos, vendas...)
│       │   │   ├── auth/
│       │   │   ├── produtos/
│       │   │   ├── clientes/
│       │   │   ├── vendas/
│       │   │   └── dashboard/
│       │   ├── layouts/
│       │   ├── hooks/
│       │   ├── types/                (tipos TypeScript)
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── index.html
│       ├── package.json
│       ├── tsconfig.json
│       ├── tailwind.config.js
│       └── vite.config.ts
│
├── docs/
│   ├── 01-visao-produto-e-contextos.md
│   ├── 02-modelo-de-dominio-e-entidades.md
│   ├── 03-arquitetura-de-solucao.md
│   ├── 04-plano-de-implementacao-sprints.md
│   ├── 05-estrutura-monorepo.md
│   └── ADR/
│       ├── README.md                 (índice das ADRs + template)
│       ├── 0001-banco-unico-com-tenantid.md
│       ├── 0002-clean-architecture-4-camadas.md
│       ├── 0003-servicos-simples-sem-mediatr.md
│       └── 0004-insights-como-motor-de-regras.md
│
└── infra/
    ├── docker-compose.yml            (API + SQL Server + web)
    ├── backend.Dockerfile
    ├── frontend.Dockerfile
    └── .env.example
```

---

## 3. Regras da estrutura (o que cada raiz significa)

| Pasta raiz | Papel |
|---|---|
| `backend/` | Solução .NET (4 projetos Clean Architecture + testes) |
| `frontend/` | App React + TypeScript + Tailwind |
| `docs/` | Documentação técnica (Docs 01–05) |
| `docs/ADR/` | Registro de decisões arquiteturais |
| `infra/` | Docker, compose e variáveis de ambiente |

---

## 4. Como o AJUSTE 3 (frontend junto) aparece na estrutura

O frontend é organizado por **feature**, espelhando os módulos do backend:

```
Sprint 1 (backend: auth)      → frontend/features/auth/
Sprint 2 (backend: cadastros) → frontend/features/produtos, clientes/
Sprint 3 (backend: vendas)    → frontend/features/vendas/
Sprint 4 (backend: dashboard) → frontend/features/dashboard/
```

Cada sprint entrega **backend + a tela correspondente**, não só a API.

---

## 5. Como o AJUSTE 4 (local antes de container) aparece na Sprint 0

```
PASSO 1: Rodar backend local (dotnet run) → API sobe.
PASSO 2: Conectar no SQL Server local (string em appsettings.Development).
PASSO 3: Aplicar migration → banco criado.
PASSO 4: Abrir Swagger local → confirmado.
PASSO 5: Rodar frontend local (npm run dev) → tela abre.
PASSO 6: SÓ ENTÃO → configurar infra/docker-compose.yml.
```

Container é o último passo da Sprint 0 — primeiro garante que roda na máquina.

---

## 6. ADR — como vamos registrar decisões

Cada decisão importante vira um arquivo em `docs/ADR/` seguindo um template curto:

```
TEMPLATE ADR:
  - Título
  - Status (proposta / aceita / substituída)
  - Contexto (o problema)
  - Decisão (o que foi escolhido)
  - Consequências (prós e contras)
```

As 4 primeiras ADRs já saem das decisões que tomamos nos Docs 01–03.

---

## 7. Validação

```
DECISÃO 1: Aprova a estrutura raiz (backend/frontend/docs/infra)?
DECISÃO 2: Aprova a organização interna do backend (src/ + tests/)?
DECISÃO 3: Aprova o frontend organizado por feature?
DECISÃO 4: Aprova a pasta docs/ADR com o template?
```

Aprovado, inicio a execução da Sprint 0 seguindo esta estrutura.
