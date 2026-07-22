# 0005 - Migração do backend de .NET/ASP.NET Core para Python/FastAPI

**Status:** aceita
**Data:** 2026-07-22

## Contexto

O backend original (Sprints 0-2) foi implementado em C#/.NET 9 com ASP.NET Core, EF
Core e Clean Architecture em 4 camadas (ver [0002](0002-clean-architecture-4-camadas.md)).
Após refletir sobre os objetivos do projeto, a decisão foi trocar a tecnologia de
implementação do backend para Python 3.13 com FastAPI, mantendo produto, domínio e
frontend intactos.

Restrições explícitas dessa decisão:

- Todo o domínio, regras de negócio, fluxos, entidades, documentação, ADRs e UX devem
  ser preservados integralmente — só a tecnologia de implementação do backend muda.
- O frontend React não deveria ser reescrito; apenas adaptado se alguma rota mudasse
  (no fim, nenhuma rota mudou).
- O comportamento observável do sistema (contratos HTTP, mensagens de erro, status
  codes, regras de negócio) deve continuar idêntico.

## Decisão

Reescrever a API mantendo a mesma Clean Architecture em 4 camadas (Doc
[0002](0002-clean-architecture-4-camadas.md)), traduzindo cada camada para um
equivalente Python idiomático:

| Camada (C#) | Camada (Python) | Observação |
|---|---|---|
| `Domain/Entities`, `Domain/Common`, `Domain/Enums`, `Domain/ValueObjects` | `app/domain/` | Portado 1:1 — mesmas invariantes, mesmas mensagens de `DomainException`, mesmo padrão de factory (`Venda.registrar()`) |
| `Domain/Interfaces` + `Infrastructure/Persistence/Repositories` | `app/repositories/` | Ver decisão de arquitetura abaixo |
| (implícito no EF Core: entidade = registro do banco) | `app/models/` (SQLAlchemy ORM) | Novo: no C# a entidade de domínio E o mapeamento EF Core eram o mesmo objeto; no Python são objetos distintos (ver Consequências) |
| `Application/Operations/*`, `Application/Insights/*` | `app/services/` | Mesma orquestração, mesma ordem de validação, mesmas mensagens |
| DTOs em `Application/Operations/*/*.Dtos.cs` + model binding do ASP.NET | `app/schemas/` (Pydantic v2) | Uma única camada faz o papel dos dois — records C# + binding automático viram schemas Pydantic com alias `camelCase` |
| `Infrastructure/Security`, `Infrastructure/Persistence/DbContext` | `app/core/security.py`, `app/database/` | JWT (PyJWT), hash de senha (bcrypt), engine/sessão SQLAlchemy |
| `API/Controllers/*` | `app/api/routers/*` | Mesmas rotas, mesmos status codes |
| `API/Middlewares/ExceptionHandlingMiddleware.cs` | `app/middleware/exception_handling.py` | Mesmo mapeamento de exceção → status HTTP → `{"message": "..."}` |
| EF Core Migrations | Alembic | Uma migration inicial consolidada em vez de 3 incrementais (histórico não precisava ser preservado, só o schema final) |
| `DbSeeder.cs` | `app/database/seed.py` | Mesmos dados de demonstração, mesma lógica, `random.Random(42)` no lugar de `System.Random(42)` (ver Consequências) |

Tecnologias adotadas: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PyJWT, bcrypt,
pyodbc, Uvicorn, Pytest — mantendo o **mesmo SQL Server** como banco (troca de banco
teria sido escopo não solicitado).

## Consequências

**Prós:**
- Contrato HTTP com o frontend preservado byte a byte (mesmas rotas, mesmo shape JSON
  camelCase, mesmos status codes e mensagens de erro) — o frontend React não precisou
  de nenhuma alteração de código, só de configuração de porta de desenvolvimento.
- Regras de negócio, mensagens de validação e ordem de checagens replicadas
  deliberadamente 1:1 a partir do código C# original (não reescritas "de memória").
- Suite de testes (pytest) cobrindo domínio + integração dá confiança equivalente à
  que o time tinha antes (o projeto .NET não chegou a ter testes reais, só o
  `UnitTest1.cs` gerado pelo template).

**Contras / riscos aceitos:**
- **Entidade de domínio ≠ entidade de persistência.** No C#/EF Core, a mesma classe
  (`Produto`, `Venda`...) era entidade de domínio e entidade rastreada pelo
  change-tracker do EF. Em Python, `app/domain/Produto` é um objeto puro (sem
  SQLAlchemy) e `app/models/ProdutoModel` é o mapeamento ORM — a camada
  `app/repositories/` faz a ponte. Consequência prática: todo método de serviço que
  muta uma entidade já carregada precisa terminar com uma chamada explícita a
  `repositorio.update(entidade)` para copiar o novo estado de volta no objeto
  rastreado pela sessão (o C# fazia isso implicitamente via change-tracking). Essa
  chamada extra é o único padrão novo que não tem equivalente direto no código
  original — documentado em `app/repositories/produto_repository.py`.
- **Concorrência otimista:** o `rowversion` binário nativo do SQL Server (usado pelo
  EF Core) foi trocado pelo mecanismo `version_id_col` do SQLAlchemy (contador
  inteiro). Comportamento observável idêntico (segunda escrita concorrente no mesmo
  registro → 409 Conflict), implementação mais portável.
- **Seed determinístico não é bit-a-bit idêntico entre os dois backends:**
  `System.Random(42)` (C#) e `random.Random(42)` (Python) são PRNGs diferentes — cada
  um gera sua própria sequência de números, então os dados de demonstração exatos
  (quais produtos entram em qual venda, em que dia) não são os mesmos entre uma
  instalação com seed .NET antiga e uma com seed Python nova. O processo continua
  igualmente determinístico (mesmo resultado a cada execução) e reproduz a mesma
  *distribuição* de cenários (produtos com estoque baixo/zerado, clientes inativos,
  vendas de balcão, vendas canceladas, distribuição pelos últimos 14 dias) — só os
  valores exatos sorteados diferem.
- **`ON DELETE RESTRICT` não existe no dialeto T-SQL:** descoberto durante a primeira
  tentativa de `alembic upgrade head` (o SQL Server só aceita `CASCADE`, `SET NULL`,
  `SET DEFAULT` ou `NO ACTION` em `ON DELETE`). Corrigido removendo o `ondelete`
  explícito nas FKs que antes usavam `RESTRICT` — o padrão do SQL Server sem cláusula
  já é `NO ACTION`, com o mesmo efeito observável (bloqueia o DELETE se houver
  referências).
- **`ITenantProvider`/multi-tenant query filter não foi portado:** confirmado, por
  inspeção do C# original, que essa interface estava registrada no container de DI mas
  nunca era de fato injetada em nenhum service/controller — não havia filtro de tenant
  ativo em Produtos/Clientes/Vendas no MVP. Preservar o comportamento observável
  significa *não* introduzir um filtro que não existia; a interface não foi recriada em
  Python.
