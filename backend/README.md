# BMP Commerce — Backend

API REST em Python 3.13 com FastAPI, seguindo Clean Architecture em 4 camadas. Migrado
de C#/.NET 9/ASP.NET Core — ver [ADR 0005](../docs/ADR/0005-migracao-backend-dotnet-para-python-fastapi.md)
e [docs/08](../docs/08-migracao-backend-python-fastapi.md) para o histórico completo da
migração.

## Camadas

```
app/api/routers/   → rotas FastAPI, equivalente aos Controllers (JWT/CORS/wiring em main.py)
app/services/       → casos de uso, orquestração (equivalente a Application/Operations)
app/domain/         → entidades, enums, value objects, exceções de domínio — puro Python
app/repositories/   → ponte entre app/models (ORM) e app/domain (puro)
app/models/         → mapeamento SQLAlchemy (persistência)
app/schemas/        → contratos HTTP (Pydantic v2, alias camelCase)
```

Regra de dependência: `api/routers → services → domain ← repositories ← models`. O
`domain/` não importa nada de `sqlalchemy`/`fastapi`/`pydantic` — é Python puro, testável
sem banco. `services/` depende só de `domain/` + `repositories/` (nunca de `models/`
diretamente, nem de `schemas/` para escrever, só para receber requests já validados).

## Por que domain/ e models/ são pastas separadas

No backend C# original, a mesma classe (`Produto`, `Venda`...) era entidade de domínio
**e** entidade EF Core rastreada pelo change-tracker — mutar um campo e chamar
`SaveChangesAsync()` bastava. Em Python isso teria acoplado regra de negócio pura ao
SQLAlchemy, então:

- `app/domain/Produto` — objeto Python puro, valida invariantes no construtor/métodos,
  levanta `DomainException`. Testável sem qualquer banco (ver `tests/test_domain_*.py`).
- `app/models/ProdutoModel` — mapeamento SQLAlchemy burro, sem regra de negócio.
- `app/repositories/ProdutoRepository` — converte um para o outro. Consequência prática:
  todo método de serviço que muta uma entidade **já carregada** (ex: `produto.atualizar(...)`,
  `venda.cancelar()`) precisa terminar com uma chamada explícita a
  `repositorio.update(entidade)` para copiar o novo estado de volta no `Model` rastreado
  pela sessão — é essa chamada que faz a mutação sair no `UPDATE` do commit. Isso é o
  único padrão sem equivalente direto no C# original (lá era implícito).

## Padrão de um módulo (vertical slice)

```
app/domain/<recurso>.py                  entidade com invariantes (levanta DomainException)
app/models/<recurso>.py                  mapeamento SQLAlchemy
app/repositories/<recurso>_repository.py mapeamento model ↔ domain + persistência
app/schemas/<recurso>.py                 Pydantic: Dto de resposta + Request de criar/atualizar
app/services/<recurso>_service.py        orquestra repositório + regras, monta o Dto de resposta
app/api/routers/<recurso>s.py            endpoints REST
```

**Onde há regra de negócio real, o domínio usa agregado DDD** (Doc 01 §6): `Venda` nasce
pela factory `Venda.registrar(...)`, que valida todas as invariantes (estoque, itens,
congelamento de preço/custo) **antes** de debitar qualquer estoque, e é persistida em um
único `session.commit()` — uma transação. CRUDs simples (`Cliente`) não ganham agregado.
`DashboardService` (equivalente a `Application/Insights/`) só lê, nunca escreve (ADR
0004).

**Concorrência:** `Produto` e `Venda` usam o mecanismo `version_id_col` do SQLAlchemy
(equivalente funcional ao `RowVersion`/`rowversion` do SQL Server usado pelo EF Core).
Conflito de escrita simultânea levanta `sqlalchemy.orm.exc.StaleDataError` →
`app/middleware/exception_handling.py` responde 409.

## Tratamento de erros

Centralizado em `app/middleware/exception_handling.py`, que registra exception handlers
do FastAPI e converte tudo para o formato `{"message": "..."}`:

| Exceção | Onde é levantada | Status HTTP |
|---|---|---|
| `app.core.exceptions.DomainException` | Entidades de domínio, ao violar uma invariante (ex: preço negativo) | 400 |
| `app.core.exceptions.NotFoundException` | Services, quando um recurso não existe | 404 |
| `sqlalchemy.orm.exc.StaleDataError` | Conflito de concorrência otimista (`version_id_col`) | 409 |
| `fastapi.exceptions.RequestValidationError` | Corpo/parâmetros inválidos (equivalente ao model binding do ASP.NET) | 400 (primeira mensagem de validação) |
| `starlette.exceptions.HTTPException` | Ex: 401 sem token válido (`app/dependencies/auth.py`) | conforme levantado |
| Qualquer outra `Exception` | Inesperado | 500 (mensagem genérica, sem stack trace) |

`Result`/`Result[T]` (`app/domain/common.py`) são usados só para falhas de regra de
negócio **esperadas e recuperáveis pelo chamador** (ex: "SKU já cadastrado", "email ou
senha inválidos") — o router decide o status HTTP (geralmente 400, 401 no login) e
devolve a mensagem para o usuário corrigir o input. "Não encontrado" **nunca** usa
`Result` — sempre `NotFoundException`.

## Rodando localmente

Ver [README raiz](../README.md#backend) para pré-requisitos e comandos completos.
Resumo:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows; source .venv/bin/activate no Linux/macOS
pip install -r requirements.txt

# banco: SQL Server acessível em localhost (ver DATABASE_URL em app/core/config.py
# ou .env), então:
alembic upgrade head

uvicorn app.main:app --reload --port 5050
```

Em ambiente de desenvolvimento (`ENVIRONMENT=Development`, o padrão), o boot da API
executa automaticamente o seed de demonstração (idempotente — não duplica dados em
re-execuções). As migrations **não** rodam automaticamente no boot (nem em dev nem em
produção) — rode `alembic upgrade head` manualmente antes de subir a API pela primeira
vez, ou depois de criar uma nova migration.

- API: http://localhost:5050
- Swagger/OpenAPI: http://localhost:5050/docs

## Testes

```bash
pytest tests/ -v
```

`tests/test_domain_*.py` — testes de domínio, puro Python, sem banco.
`tests/test_api_*.py` — testes de integração via `fastapi.testclient.TestClient`,
rodando contra um SQL Server real dedicado (`BMPCommerceTestDb` por padrão — ver
`tests/conftest.py`), com cada teste isolado em uma transação revertida no final.
