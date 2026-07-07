# BMP Commerce

Sistema de e-commerce/gestão comercial multi-tenant, com backend em .NET (Clean Architecture) e frontend em React + TypeScript.

## Status atual: Marco 1 — primeira versão executável

Login funcional de ponta a ponta: API + banco de dados + autenticação JWT + frontend consumindo tudo isso.

- ✅ **Domain**: entidades `Tenant` e `Usuario`, value object `Email`, enum `UserRole`, invariantes de negócio
- ✅ **Application**: contratos (`IApplicationDbContext`, `IJwtService`, `IPasswordHasher`, `ITenantProvider`, `ICurrentUserService`) e caso de uso de autenticação (`AuthService`)
- ✅ **Infrastructure**: EF Core + SQL Server, migrations, BCrypt, geração de JWT, seed automático
- ✅ **API**: `POST /api/auth/login`, `GET /api/auth/me`, Swagger com autenticação Bearer, CORS, criação automática do banco no startup
- ✅ **Frontend**: tela de login, dashboard temporário, sidebar/header/breadcrumb, dark mode persistente, layout responsivo
- ⏳ **Próximo passo**: Sprint 1 — CRUD de Categorias/Produtos/Clientes (cadastros base)

O plano completo de sprints está em [docs/04-plano-de-implementacao-sprints.md](docs/04-plano-de-implementacao-sprints.md).

## Arquitetura

Clean Architecture com 4 camadas (API → Application → Domain ← Infrastructure), sem MediatR. Multi-tenancy por banco único com `TenantId`. Decisões registradas em [ADRs](docs/ADR/).

```
backend/
  src/
    BMPCommerce.API/             API REST — controllers, Program.cs, configuração de JWT/Swagger/CORS
    BMPCommerce.Application/     Casos de uso (Operations/), contratos (Common/), motor de insights (Insights/)
    BMPCommerce.Domain/          Entidades, enums, value objects, exceções e regras de negócio puras
    BMPCommerce.Infrastructure/  EF Core, migrations, seed, JWT/BCrypt, tenancy
  tests/
    BMPCommerce.UnitTests/
    BMPCommerce.IntegrationTests/

frontend/
  bmp-commerce-web/              SPA React + TS + Vite (organizada por features) — ver README próprio

infra/                           Docker Compose e Dockerfiles
docs/                            Documentação de produto, domínio e arquitetura (+ ADRs)
```

## Documentação

- [Visão de produto e contextos](docs/01-visao-produto-e-contextos.md)
- [Modelo de domínio e entidades](docs/02-modelo-de-dominio-e-entidades.md)
- [Arquitetura de solução](docs/03-arquitetura-de-solucao.md)
- [Plano de implementação (sprints)](docs/04-plano-de-implementacao-sprints.md)
- [Estrutura do monorepo](docs/05-estrutura-monorepo.md)
- [ADRs](docs/ADR/)

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
