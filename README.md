# BMP Commerce

Sistema de e-commerce/gestão comercial multi-tenant, com backend em .NET (Clean Architecture) e frontend em React + TypeScript.

## Status atual: Sprint 2 — Fluxo comercial completo

O sistema executa o ciclo comercial inteiro: login → cadastro de produtos e clientes → **registro de venda com baixa automática de estoque** → dashboard com indicadores e gráfico alimentados por dados reais.

- ✅ **Produtos**: CRUD completo com indicadores, busca, filtro, paginação e badges de estoque (Normal/Baixo/Sem estoque)
- ✅ **Clientes**: CRUD completo com indicadores (total, ativos, inativos, novos no mês), CPF/CNPJ validado e formatado
- ✅ **Vendas**: fluxo de venda estilo PDV (`/vendas/nova`) — cliente opcional (balcão), busca de produtos, carrinho com quantidades, resumo em tempo real; listagem com filtros por período/cliente/status, ordenação, detalhes e **cancelamento com estorno de estoque**
- ✅ **Estoque**: baixa automática na venda, nunca negativo (venda bloqueada), concorrência otimista com RowVersion (409 em conflito), preço/custo **congelados** no item para margem histórica
- ✅ **Dashboard**: receita total, vendas, ticket médio, valor do estoque, clientes, produtos, alertas de estoque + gráfico de vendas dos últimos 14 dias (Recharts)
- ✅ **Seed de demonstração**: admin + 20 produtos + 15 clientes + 20 vendas consistentes criados automaticamente em banco vazio
- ⏳ **Próximo passo**: Motor de Insights (frases de negócio) e dashboard por papel

Detalhes da sprint em [docs/07-sprint-2-fluxo-comercial-completo.md](docs/07-sprint-2-fluxo-comercial-completo.md). O plano completo de sprints está em [docs/04-plano-de-implementacao-sprints.md](docs/04-plano-de-implementacao-sprints.md).

## Arquitetura

Clean Architecture com 4 camadas (API → Application → Domain ← Infrastructure), sem MediatR. Multi-tenancy por banco único com `TenantId`. Decisões registradas em [ADRs](docs/ADR/). Convenções de código e o padrão de "vertical slice" para novos módulos estão documentados em [backend/README.md](backend/README.md).

```
backend/
  src/
    BMPCommerce.API/             API REST — controllers, middlewares, Program.cs (JWT/Swagger/CORS)
    BMPCommerce.Application/     Casos de uso (Operations/), contratos (Common/)
    BMPCommerce.Domain/          Entidades, enums, value objects, exceções e regras de negócio puras
    BMPCommerce.Infrastructure/  EF Core, migrations, seed, JWT/BCrypt, repositórios, tenancy
  tests/
    BMPCommerce.UnitTests/
    BMPCommerce.IntegrationTests/

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
- [ADRs](docs/ADR/)
- [Backend — arquitetura e convenções](backend/README.md)
- [Frontend — stack e estrutura](frontend/bmp-commerce-web/README.md)

## Como rodar localmente

### Pré-requisitos

- [.NET SDK 9](https://dotnet.microsoft.com/download)
- [Node.js 20+](https://nodejs.org/)
- SQL Server acessível em `localhost` (instância local, LocalDB ou container) com autenticação do Windows, **ou** ajuste a connection string conforme sua instalação

### Backend

```bash
cd backend/src/BMPCommerce.API
cp appsettings.Development.json.example appsettings.Development.json
# edite a Jwt:Key no arquivo copiado (qualquer string com 32+ caracteres serve para dev local)

dotnet run --launch-profile http
```

Ao subir em ambiente de desenvolvimento, a API automaticamente:
1. Aplica as migrations do EF Core (cria o banco `BMPCommerceDb` se não existir)
2. Executa o seed inicial (tenant de demonstração + usuário administrador)

- API: http://localhost:5050
- Swagger: http://localhost:5050/swagger

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
