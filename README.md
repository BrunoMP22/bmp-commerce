# BMP Commerce

Sistema de e-commerce/gestão comercial multi-tenant, com backend em .NET (Clean Architecture) e frontend em React + TypeScript.

## Status atual: Sprint 0 concluída

O projeto está na fundação do desenvolvimento — ambiente e estrutura prontos, ainda sem regras de negócio implementadas.

- ✅ Solução .NET com 4 camadas: `Domain`, `Application`, `Infrastructure`, `API`
- ✅ Frontend Vite + React + TypeScript + Tailwind, com pastas de features (`auth`, `clientes`, `dashboard`, `produtos`, `vendas`)
- ✅ Docker Compose (API + SQL Server + web)
- ✅ EF Core configurado, com migration inicial (`InitialCreate`)
- ✅ Documentação de arquitetura e decisões técnicas (ver [`docs/`](docs/))
- ⏳ Próximo passo: **Sprint 1** — Autenticação + Multi-tenancy + Usuários

O plano completo de sprints está em [docs/04-plano-de-implementacao-sprints.md](docs/04-plano-de-implementacao-sprints.md).

## Arquitetura

Clean Architecture com 4 camadas (API → Application → Domain ← Infrastructure), sem MediatR. Multi-tenancy por banco único com `TenantId`. Decisões registradas em [ADRs](docs/ADR/).

```
backend/
  src/
    BMPCommerce.API/             API REST (controllers, middlewares)
    BMPCommerce.Application/     Casos de uso (Operations/) e motor de insights (Insights/)
    BMPCommerce.Domain/          Entidades, enums, interfaces, value objects
    BMPCommerce.Infrastructure/  EF Core, repositórios, segurança, tenancy
  tests/
    BMPCommerce.UnitTests/
    BMPCommerce.IntegrationTests/

frontend/
  bmp-commerce-web/              SPA React + TS + Vite (organizada por features)

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

## Como rodar

Requisitos: Docker (recomendado) ou .NET 9 + Node.js + SQL Server local.

```bash
cd infra
cp .env.example .env
docker compose up
```

- API: `http://localhost:<API_PORT>`
- Web: `http://localhost:<WEB_PORT>`
