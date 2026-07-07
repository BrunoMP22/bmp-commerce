# 0002 - Clean Architecture em 4 camadas

**Status:** aceita
**Data:** 2026-07-06

## Contexto

O produto tem dois bounded contexts com ritmos de mudança diferentes:
Operations (núcleo transacional, estável) e Insights (leitura/analytics, muda
toda semana) — Doc 01 §5. Era preciso uma organização de código que:

- Isole regra de negócio de detalhe técnico (banco, JWT, HTTP), para que
  Insights e Operations evoluam sem se acoplar (Doc 01 §5, §6).
- Evite overengineering em partes que são CRUD simples (Categoria, Cliente,
  Perfil da Empresa) — Doc 01 §6.

## Decisão

Adotar Clean Architecture com 4 camadas e uma única direção de dependência,
sempre apontando para o Domain (Doc 03 §1):

```
API → Application → Domain ← Infrastructure
```

- **Domain**: entidades, enums, value objects e as interfaces de repositório
  (`IProdutoRepository` etc.). Não depende de nada externo — sem EF Core, sem
  HTTP (Doc 03 §2.1).
- **Application**: casos de uso (`RegistrarVenda`, `CalcularInsights`...),
  DTOs, interfaces de serviço (`ITenantContext`, `IJwtService`). Depende só do
  Domain (Doc 03 §2.2). Aqui moram os dois bounded contexts, isolados por
  pasta: `Operations/` e `Insights/` (Doc 03 §4).
- **Infrastructure**: implementação dos repositórios, DbContext + Global Query
  Filter, JWT, hashing de senha, e-mail, upload (Doc 03 §2.3).
- **API**: controllers REST, middlewares, configuração de DI/JWT/CORS/Swagger
  (Doc 03 §2.4).

DDD é aplicado só onde há regra de negócio real (Venda, Estoque, Insights);
o resto é CRUD honesto, sem aggregate/value object desnecessário (Doc 01 §6,
Doc 03 §10 DECIDIDO 2).

## Consequências

**Prós:**
- Domain nunca sabe que existe SQL Server, EF Core ou React — trocar
  Infrastructure não exige tocar em regra de negócio.
- Insights pode evoluir (nova regra por semana) sem tocar em Operations,
  porque vivem em pastas isoladas dentro do mesmo Application e a regra de
  isolamento é explícita: Insights lê de Operations, nunca escreve
  (Doc 03 §4).
- Isolamento de tenant fica concentrado na Infrastructure (Global Query
  Filter), então nenhuma camada acima precisa se lembrar de filtrar
  manualmente (ver [0001](0001-banco-unico-com-tenantid.md)).

**Contras / riscos aceitos:**
- Mais projetos e indireção do que um monolito de camada única — aceito
  como custo para manter a regra de dependência única (Doc 03 §1) e o
  isolamento Operations/Insights.
- Exige disciplina do time para não vazar Infrastructure para dentro do
  Domain/Application (ex.: usar tipos do EF Core em uma entidade de Domain).
