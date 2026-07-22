# BMP Commerce

Sistema de e-commerce/gestão comercial multi-tenant, com backend em Python/FastAPI (Clean Architecture) e frontend em React + TypeScript.

## Status atual: Sprint 2 — Fluxo comercial completo

O sistema executa o ciclo comercial inteiro: login → cadastro de produtos e clientes → **registro de venda com baixa automática de estoque** → dashboard com indicadores e gráfico alimentados por dados reais.

- ✅ **Produtos**: CRUD completo com indicadores, busca, filtro, paginação e badges de estoque (Normal/Baixo/Sem estoque)
- ✅ **Clientes**: CRUD completo com indicadores (total, ativos, inativos, novos no mês), CPF/CNPJ validado e formatado
- ✅ **Vendas**: fluxo de venda estilo PDV (`/vendas/nova`) — cliente opcional (balcão), busca de produtos, carrinho com quantidades, resumo em tempo real; listagem com filtros por período/cliente/status, ordenação, detalhes e **cancelamento com estorno de estoque**
- ✅ **Estoque**: baixa automática na venda, nunca negativo (venda bloqueada), concorrência otimista (409 em conflito), preço/custo **congelados** no item para margem histórica
- ✅ **Dashboard**: receita total, vendas, ticket médio, valor do estoque, clientes, produtos, alertas de estoque + gráfico de vendas dos últimos 14 dias (Recharts)
- ✅ **Seed de demonstração**: admin + 20 produtos + 15 clientes + 20 vendas consistentes criados automaticamente em banco vazio
- ⏳ **Próximo passo**: Motor de Insights (frases de negócio) e dashboard por papel

Detalhes da sprint em [docs/07-sprint-2-fluxo-comercial-completo.md](docs/07-sprint-2-fluxo-comercial-completo.md). O plano completo de sprints está em [docs/04-plano-de-implementacao-sprints.md](docs/04-plano-de-implementacao-sprints.md).

## Arquitetura

Clean Architecture com 4 camadas (api/routers → services → domain ← repositories/models), sem MediatR. Multi-tenancy por banco único com `TenantId`. Decisões registradas em [ADRs](docs/ADR/), incluindo a migração do backend de .NET para Python ([ADR 0005](docs/ADR/0005-migracao-backend-dotnet-para-python-fastapi.md)). Convenções de código e o padrão de "vertical slice" para novos módulos estão documentados em [backend/README.md](backend/README.md).

```
backend/
  app/
    api/routers/    Rotas REST — auth, produtos, clientes, vendas, dashboard
    services/       Casos de uso (equivalente a Application/Operations)
    domain/         Entidades, enums, value objects, exceções e regras de negócio puras
    repositories/   Ponte entre app/models (SQLAlchemy) e app/domain (puro)
    models/         Mapeamento SQLAlchemy (persistência)
    schemas/        Contratos HTTP (Pydantic v2, alias camelCase)
    core/           Config, JWT/BCrypt, exceções centrais
    dependencies/   Sessão de DB por requisição, extração do usuário JWT
    middleware/     Exception handling centralizado
    main.py         Wiring (CORS, lifespan, routers) — equivalente a Program.cs
  alembic/          Migrations
  tests/            pytest — domínio (unitário) + integração (API + SQL Server real)

frontend/
  bmp-commerce-web/              SPA React + TS + Vite (organizada por features) — ver README próprio

infra/                           Docker Compose e Dockerfiles
docs/                            Documentação de produto, domínio e arquitetura (+ ADRs, screenshots)
```

## Documentação

- [Visão de produto e contextos](docs/01-visao-produto-e-contextos.md)
- [Modelo de domínio e entidades](docs/02-modelo-de-dominio-e-entidades.md)
- [Arquitetura de solução](docs/03-arquitetura-de-solucao.md)
- [Plano de implementação (sprints)](docs/04-plano-de-implementacao-sprints.md)
- [Estrutura do monorepo](docs/05-estrutura-monorepo.md)
- [Sprint 1.5 — Refinamento do MVP](docs/06-sprint-1.5-refinamento-mvp.md) (changelog + decisões + screenshots)
- [Sprint 2 — Fluxo comercial completo](docs/07-sprint-2-fluxo-comercial-completo.md) (Clientes, Vendas, Estoque, Dashboard)
- [Migração do backend: .NET → Python/FastAPI](docs/08-migracao-backend-python-fastapi.md)
- [ADRs](docs/ADR/)
- [Backend — arquitetura e convenções](backend/README.md)
- [Frontend — stack e estrutura](frontend/bmp-commerce-web/README.md)

## Como rodar localmente

### Pré-requisitos

- [Python 3.13](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- SQL Server acessível em `localhost` (instância local ou container), com o "ODBC Driver 17" ou "18 for SQL Server" instalado — **ou** ajuste `DATABASE_URL` conforme sua instalação (ver `backend/app/core/config.py`)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows; source .venv/bin/activate no Linux/macOS
pip install -r requirements.txt

alembic upgrade head          # cria o schema no banco BMPCommerceDb (só na primeira vez / após novas migrations)

uvicorn app.main:app --reload --port 5050
```

Ao subir em ambiente de desenvolvimento (`ENVIRONMENT=Development`, o padrão), a API
executa automaticamente o seed inicial (tenant de demonstração + usuário administrador +
produtos/clientes/vendas de exemplo) — idempotente, não duplica dados em re-execuções.
As migrations não rodam automaticamente no boot; use `alembic upgrade head`.

- API: http://localhost:5050
- Swagger/OpenAPI: http://localhost:5050/docs

### Frontend

```bash
cd frontend/bmp-commerce-web
npm install
npm run dev
```

- Frontend: http://localhost:5173 (se a porta estiver ocupada, o Vite escolhe outra automaticamente — a API aceita qualquer origem `localhost`/`127.0.0.1` em desenvolvimento)

### Credenciais do usuário administrador (seed)

| Campo | Valor |
|---|---|
| Email | `admin@bmpcommerce.com` |
| Senha | `Admin@123` |
| Papel | SuperAdmin (usuário de plataforma, sem tenant) |

> Credencial de desenvolvimento local, criada automaticamente pelo seed. Não usar em produção.

### Alternativa: Docker Compose

```bash
cd infra
cp .env.example .env
docker compose up
```

Sobe SQL Server + API + frontend em containers (configuração de portas em `infra/.env`).
As migrations não rodam automaticamente no container (mesma característica preservada
do backend original) — rode `alembic upgrade head` manualmente contra o banco do
container antes do primeiro uso.
