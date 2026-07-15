# BMP Commerce — Backend

API REST em .NET 9, seguindo Clean Architecture em 4 camadas.

## Camadas

```
BMPCommerce.API              → controllers, middlewares, Program.cs (DI, JWT, Swagger, CORS)
BMPCommerce.Application      → casos de uso, contratos (interfaces), DTOs
BMPCommerce.Domain           → entidades, enums, value objects, exceções de domínio
BMPCommerce.Infrastructure   → EF Core, migrations, JWT/BCrypt, repositórios
```

Regra de dependência: `API → Application → Domain ← Infrastructure`. O Domain não depende de nenhuma outra camada. A Application depende só do Domain. Infrastructure e API dependem "para dentro".

## Padrão de um módulo (vertical slice)

Cada recurso de negócio (ex: Produto) segue o mesmo esqueleto, usado como referência para novos módulos:

```
Domain/
  Entities/<Recurso>.cs             entidade com invariantes (lança DomainException)
  Interfaces/I<Recurso>Repository.cs contrato do repositório (não genérico)

Application/Operations/<Recurso>s/
  <Recurso>Dtos.cs                  records de request/response
  I<Recurso>Service.cs              contrato do caso de uso
  <Recurso>Service.cs               implementação (orquestra repositório + regras)

Infrastructure/Persistence/
  Configurations/<Recurso>Configuration.cs   mapeamento EF Core
  Repositories/<Recurso>Repository.cs        implementação do repositório

API/Controllers/<Recurso>sController.cs      endpoints REST
```

**Onde há regra de negócio real, o Domain usa agregado DDD** (Doc 01 §6): `Venda` nasce pela
factory `Venda.Registrar(...)` que valida todas as invariantes (estoque, itens, congelamento de
preço/custo) e é persistida por um único `SaveChangesAsync` — uma transação. CRUDs simples
(Cliente, Categoria) não ganham agregado. Leitura/analytics vive em `Application/Insights/`
(nunca escreve — ADR 0004); hoje abriga o `DashboardService`.

**Concorrência:** `Produto` e `Venda` têm `RowVersion` (SQL Server `rowversion`). Conflito de
escrita simultânea vira `DbUpdateConcurrencyException` → middleware responde 409.

## Tratamento de erros

Centralizado em `API/Middlewares/ExceptionHandlingMiddleware.cs`, que captura exceções lançadas pelas camadas internas e converte para uma resposta HTTP consistente no formato `{ "message": "..." }`:

| Exceção | Onde é lançada | Status HTTP |
|---|---|---|
| `Domain.Common.DomainException` | Entidades, ao violar uma invariante (ex: preço negativo) | 400 |
| `Application.Common.Exceptions.NotFoundException` | Services, quando um recurso não existe | 404 |
| Qualquer outra `Exception` | Inesperado | 500 (mensagem genérica, sem stack trace) |

Falhas de model binding automático do ASP.NET Core (JSON malformado, campo com tipo errado) também são normalizadas para o mesmo formato `{ message }` via `ApiBehaviorOptions.InvalidModelStateResponseFactory` em `Program.cs`, em vez do `ValidationProblemDetails` padrão do framework.

**`Result<T>` / `Result`** (`Domain/Common/Result.cs`) são usados apenas para falhas de regra de negócio **esperadas e recuperáveis pelo chamador** (ex: "SKU já cadastrado", "email ou senha inválidos) — casos em que o controller decide o status HTTP (geralmente 400) e devolve a mensagem para o usuário corrigir o input. "Não encontrado" **nunca** usa `Result` — sempre `NotFoundException`, tratada uma única vez no middleware.

## Convenções de nomenclatura

- **Entidades de domínio em português** (`Tenant`, `Usuario`, `Produto`) — refletem a linguagem do negócio (o time e os documentos de produto são em pt-BR).
- **Termos técnicos/infraestrutura em inglês** (`UserRole`, `IJwtService`, `IPasswordHasher`, `NotFoundException`) — seguem a convenção do próprio ecossistema .NET.
- **Métodos de caso de uso em português, verbo + substantivo** (`ObterPorIdAsync`, `CriarAsync`, `AtualizarAsync`, `ExcluirAsync`), exceto termos já consagrados em inglês mesmo em times brasileiros (`LoginAsync`).

Essa mistura é intencional, não uma inconsistência a ser corrigida — está documentada aqui para que não seja "normalizada" para um único idioma sem essa discussão.

## Logs

- `ExceptionHandlingMiddleware`: `LogWarning` para `DomainException`/`NotFoundException` (erros esperados do cliente), `LogError` para exceções não tratadas.
- `AuthService`: `LogInformation` em login bem-sucedido, `LogWarning` em tentativa de login falha ou tenant inativo (trilha de auditoria mínima; nunca loga a senha).

## Rodando localmente

Ver [README raiz](../README.md#backend) para pré-requisitos e comandos.
