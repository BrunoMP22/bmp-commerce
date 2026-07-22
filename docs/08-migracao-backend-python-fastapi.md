# 08 — Migração do backend: .NET/ASP.NET Core → Python/FastAPI

Este documento descreve a migração completa do backend do BMP Commerce de
C#/.NET 9/ASP.NET Core para Python 3.13/FastAPI, realizada em 2026-07-22. A decisão e
suas justificativas de arquitetura estão registradas em
[ADR 0005](ADR/0005-migracao-backend-dotnet-para-python-fastapi.md); este documento foca
no "como" — mapeamento de código, o que mudou, o que foi preservado, e a validação
executada.

## Objetivo e escopo

Trocar **apenas a tecnologia de implementação do backend**, preservando:

- Todo o domínio e regras de negócio (Docs [01](01-visao-produto-e-contextos.md),
  [02](02-modelo-de-dominio-e-entidades.md))
- Todos os fluxos (autenticação, produtos, clientes, vendas, dashboard)
- O contrato HTTP exato consumido pelo frontend (rotas, shape JSON, status codes,
  mensagens de erro)
- O frontend React, sem reescrita (só a porta de desenvolvimento do backend mudou de
  configuração — nenhuma linha de código do frontend foi alterada)
- A documentação, ADRs e estrutura do monorepo

O que foi **substituído**: toda a implementação do backend (`backend/src/*`,
`backend/tests/BMPCommerce.*`, `BMPCommerce.sln`, todos os `.csproj`) e a infraestrutura
Docker do backend.

## Mapeamento de arquitetura

A Clean Architecture em 4 camadas ([ADR 0002](ADR/0002-clean-architecture-4-camadas.md))
foi preservada; o texto completo da tabela de correspondência camada a camada está em
[ADR 0005](ADR/0005-migracao-backend-dotnet-para-python-fastapi.md). Resumo da estrutura
final:

```
backend/
  app/
    core/           config (pydantic-settings), security (JWT+bcrypt), exceptions
    domain/         entidades puras — Tenant, Usuario, Produto, Cliente, Venda+ItemVenda
    models/         SQLAlchemy ORM (mapeamento de persistência)
    repositories/   ponte entre models (ORM) e domain (puro)
    schemas/        Pydantic v2, alias camelCase — contrato HTTP
    services/       orquestração de caso de uso (equivalente a Application/Operations)
    dependencies/   sessão de DB por requisição, extração do usuário JWT
    middleware/      exception handling centralizado ({"message": "..."})
    api/routers/    rotas — auth, produtos, clientes, vendas, dashboard
    database/       engine/sessão SQLAlchemy, seed de demonstração
    main.py         equivalente a Program.cs (CORS, lifespan, wiring)
  alembic/          migrations (uma migration inicial consolidada)
  tests/            pytest — domínio (unitário) + integração (API + SQL Server real)
  requirements.txt
  alembic.ini
```

## O que mudou de fato (decisões técnicas)

1. **Entidade de domínio ≠ entidade de persistência.** No C#, a mesma classe era
   entidade de domínio e entidade EF Core rastreada pelo change-tracker. Em Python,
   `app/domain/` é puro (sem import de SQLAlchemy) e `app/models/` é o mapeamento ORM
   burro; `app/repositories/` faz a ponte, inclusive um `update()` explícito que não
   tinha equivalente direto no C# (o EF Core detectava mutações sozinho).
2. **Concorrência otimista**: `rowversion` binário do SQL Server → `version_id_col` do
   SQLAlchemy (contador inteiro). Mesmo comportamento observável: segunda escrita
   concorrente no mesmo `Produto`/`Venda` → conflito → 409 com a mesma mensagem
   (`"Os dados foram alterados por outra operação ao mesmo tempo. Tente novamente."`).
3. **Timezone**: domínio e API trabalham com `datetime` timezone-aware em UTC; o banco
   guarda `datetime` naive UTC (mesma semântica do `datetime2` do schema original).
   Conversão isolada em `app/models/base.py` (`to_naive_utc`/`to_aware_utc`), só na
   fronteira do repositório.
4. **Dinheiro**: `Decimal` no domínio/banco (precisão exata), convertido para `float`
   nos schemas Pydantic (contrato JSON) — o frontend já esperava `number`, não string.
5. **Migrations**: uma migration Alembic inicial consolidada (schema final completo) no
   lugar das 3 migrations incrementais do EF Core — o histórico incremental não
   precisava ser preservado, só o schema resultante.
6. **`ON DELETE RESTRICT` não existe em T-SQL.** Descoberto ao rodar
   `alembic upgrade head` pela primeira vez: SQL Server só aceita `CASCADE`,
   `SET NULL`, `SET DEFAULT` ou `NO ACTION`. Corrigido removendo o `ondelete`
   explícito — o padrão sem cláusula já é `NO ACTION`, com o mesmo efeito de bloquear
   o DELETE quando há linhas filhas.
7. **Seed de demonstração**: mesma lógica e mesmos dados-base (20 produtos, 15
   clientes, ~20 vendas, 2 canceladas, distribuídas nos últimos 14 dias) que
   `DbSeeder.cs`, reimplementada com `random.Random(42)`. A sequência exata sorteada
   difere de `System.Random(42)` (PRNGs diferentes entre as duas linguagens), mas o
   processo continua determinístico e reproduz a mesma distribuição de cenários
   (produtos com estoque baixo/zerado para os badges, clientes inativos, vendas de
   balcão, vendas canceladas).
8. **`ITenantProvider` não foi portado.** Confirmado por inspeção do C# original que
   essa interface era registrada no DI mas nunca injetada em nenhum service/controller
   — não havia filtro de tenant ativo no MVP. Não recriar esse hook morto preserva o
   comportamento observável real, em vez do comportamento "pretendido mas nunca
   ligado".

## O que **não** mudou

- Banco de dados: continua SQL Server (mesma engine, só o driver de acesso mudou de
  `Microsoft.Data.SqlClient`/EF Core para `pyodbc`/SQLAlchemy).
- Todas as rotas, verbos HTTP e status codes (`GET/POST/PUT/DELETE /api/{auth,produtos,
  clientes,vendas,dashboard}`, `201` em criação, `204` em exclusão, `409` em conflito de
  concorrência, `401` sem token, `404`/`400` conforme o tipo de erro).
- O shape JSON de toda request/response (camelCase, mesmos nomes de campo — conferido
  campo a campo contra `frontend/bmp-commerce-web/src/types/*.ts` antes de escrever os
  schemas Pydantic).
- Toda regra de negócio e suas mensagens de erro exatas: SKU duplicado, unidade de
  medida inválida, estoque insuficiente (com os números "Disponível: X, solicitado: Y"),
  produto/cliente inativo, venda sem itens, exclusão bloqueada por vendas registradas,
  cancelamento duplicado, CPF/CNPJ inválido, email/UF inválidos.
- Autenticação JWT: mesmos claims (`sub`, `name`, `email`, `role`, `iss`, `aud`, `iat`,
  `exp`), mesmo issuer/audience/expiração (480 min), mesma chave de assinatura de
  desenvolvimento.
- CORS: qualquer origem `localhost`/`127.0.0.1` em qualquer porta.
- Credenciais do seed (`admin@bmpcommerce.com` / `Admin@123`, SuperAdmin sem tenant).
- Estrutura do monorepo, documentação de produto/domínio/ADRs, frontend React (zero
  mudanças de código).

## Validação executada

1. **Testes automatizados** (`backend/tests/`, `pytest`): 41 testes — invariantes de
   domínio de `Produto`, `Cliente` e `Venda` (incluindo a validação em duas fases da
   INV5: nenhum estoque é debitado se qualquer item da venda for inválido) e testes de
   integração de API rodando contra um SQL Server real dedicado
   (`BMPCommerceTestDb`), cobrindo login, `/me`, CRUD de produtos, fluxo completo de
   venda (registro → débito de estoque → cancelamento → estorno → bloqueio de
   cancelamento duplicado), e os guards de exclusão. Todos os 41 passam.
2. **Validação manual via curl** contra o backend rodando isolado com o banco de
   desenvolvimento semeado: login válido/inválido, `/me` com e sem token, CRUD completo
   de produtos e clientes, venda com consolidação de itens duplicados, estoque
   insuficiente, venda vazia, cancelamento com estorno, duplo cancelamento, exclusão
   bloqueada por vendas/produto vinculado, SKU duplicado, CPF/CNPJ inválido, dashboard.
3. **Frontend**: `tsc --noEmit` sem erros (código do frontend inalterado), Vite dev
   server subindo normalmente, preflight e requisição real de CORS a partir da origem
   real do frontend (`http://localhost:5173`) bem-sucedidos contra o backend Python.
   *(Este ambiente não tem uma ferramenta de automação de navegador disponível, então a
   validação final "clique a clique" em UI real fica registrada aqui como
   recomendação ao time antes do primeiro deploy — a validação de contrato HTTP e de
   fluxo de negócio via testes automatizados + curl já cobre o comportamento que a UI
   exercita.)*

## Como rodar localmente

Ver [backend/README.md](../backend/README.md) e o [README raiz](../README.md) para o
passo a passo atualizado (pré-requisitos Python 3.13 + SQL Server, `pip install -r
requirements.txt`, `alembic upgrade head`, `uvicorn app.main:app`).
