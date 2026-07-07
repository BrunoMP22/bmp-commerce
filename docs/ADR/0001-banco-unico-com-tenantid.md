# 0001 - Banco único com TenantId

**Status:** aceita
**Data:** 2026-07-06

## Contexto

BMP Commerce é um SaaS B2B multi-tenant: cada empresa cliente (Tenant) precisa
ter seus dados completamente isolados dos demais. As alternativas clássicas de
multi-tenancy são: banco de dados por tenant, schema por tenant, ou banco único
com uma coluna discriminadora (`TenantId`) em cada tabela.

Banco/schema por tenant dá isolamento físico mais forte, mas custa caro em
operação (migrations, backups e monitoração multiplicados por tenant) e é
overengineering para o estágio do MVP (Doc 01 §6, Doc 02 §1).

## Decisão

Um único banco de dados para todos os tenants. Toda entidade de tenant carrega
um `TenantId` obrigatório (Doc 02 §1, PADRÃO 1). O isolamento é garantido em
tempo de execução por um **Global Query Filter** no EF Core, que aplica
`WHERE TenantId = {atual}` automaticamente em toda query (Doc 02 §7 REGRA 1,
Doc 03 §7). O desenvolvedor nunca escreve esse filtro manualmente.

O `TenantId` é resolvido a partir do JWT do usuário autenticado, via
`TenantContext` na Infrastructure (Doc 03 §2.3, §7). `Tenant` e `Super Admin`
não têm `TenantId` — pertencem à plataforma, não a um tenant (Doc 02 §1,
exceção).

Super Admin acessa dados fora do filtro através de um contexto administrativo
explícito e separado (`IgnoreQueryFilters`), nunca pelo app comum da empresa
(Doc 01 §11 R2, Doc 03 §7 Passo 5).

## Consequências

**Prós:**
- Operação simples: uma única infraestrutura de banco para manter.
- Migrations e deploys não se multiplicam por tenant.
- Barato de escalar horizontalmente no início do produto.

**Contras / riscos aceitos:**
- Isolamento é lógico, não físico — um bug que ignore o filtro pode vazar
  dados entre tenants (Doc 01 §11 R1). Mitigado pelo Global Query Filter
  automático, não opcional.
- Todas as tabelas de tenant carregam a coluna extra `TenantId` e um índice
  correspondente.
- Se o produto crescer para exigir isolamento físico por cliente grande
  (compliance, contrato), essa decisão precisará ser revisitada.
