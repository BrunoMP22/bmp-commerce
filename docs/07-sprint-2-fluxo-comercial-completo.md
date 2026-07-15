# Documento 07 — Sprint 2: Fluxo Comercial Completo

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Concluído
**Depende de:** Documentos 01–06, ADRs 0001–0004

---

## 1. Objetivo

Transformar o MVP em um fluxo comercial funcional de ponta a ponta: cadastrar clientes, registrar vendas com baixa automática de estoque, e acompanhar o negócio por um dashboard com dados reais. Cobre, de uma vez, o escopo planejado nas Sprints 2 (Clientes), 3 (Vendas) e a primeira metade da Sprint 4 (Dashboard) do Doc 04.

## 2. Novas entidades (Domain)

### 2.1 Cliente — CRUD honesto (Doc 01 §6)

Sem agregado nem value objects, por decisão documentada: validações simples na própria entidade.

| Campo | Tipo | Regra |
|---|---|---|
| Nome | string | obrigatório |
| CpfCnpj | string? | opcional; normalizado para dígitos; 11 (CPF) ou 14 (CNPJ) |
| Telefone | string? | opcional |
| Email | string? | opcional; formato validado; normalizado minúsculas |
| Cidade | string? | opcional |
| Estado | string? | opcional; UF 2 letras, normalizado maiúsculas |
| Observacoes | string? | opcional |
| Ativo | bool | default true; `Atualizar()` permite inativar |

### 2.2 Venda + ItemVenda — agregado DDD real (Doc 01 §6, Doc 02 §3.6)

`Venda` nasce completa pela factory `Venda.Registrar(usuario, cliente?, itens[], dataHora?)`, que garante todas as invariantes:

| Invariante (Doc 02) | Implementação |
|---|---|
| INV 1: ≥ 1 item | factory lança `DomainException` |
| INV 2: quantidade > 0 | validação por item |
| INV 3: preço/custo congelados | `ItemVenda` copia `PrecoVenda`/`PrecoCusto`/`Nome`/`SKU` no momento |
| INV 4: Total = Σ subtotais | acumulado dentro do agregado |
| INV 5: estoque insuficiente bloqueia a venda inteira | **valida todos os itens antes de debitar qualquer estoque** |
| INV 6: nunca deletada fisicamente | `Cancelar()` = soft delete (`IsDeleted`) |

Campos congelados extras: `ClienteNome` e `UsuarioNome` são snapshots na venda (exibição histórica sem joins; venda de balcão tem cliente nulo). `ItemVenda` congela também `ProdutoNome`/`ProdutoSku`.

`Produto` ganhou `BaixarEstoque(qtd)` (nunca deixa negativo — Doc 01 REGRA 1) e `ReporEstoque(qtd)` (estorno no cancelamento).

### 2.3 Concorrência otimista — RowVersion (Doc 01 REGRA 2)

`Produto` e `Venda` têm coluna `rowversion` do SQL Server (`IsRowVersion()` no EF). Duas vendas simultâneas debitando o mesmo produto: a segunda recebe `DbUpdateConcurrencyException`, convertida pelo middleware em **409 Conflict** com mensagem amigável — nada é persistido parcialmente.

## 3. Fluxo de registro de venda (ponta a ponta)

```
1. Frontend POST /api/vendas { clienteId?, itens: [{produtoId, quantidade}] }
2. VendaService consolida itens duplicados (mesmo produto = soma quantidades)
3. Carrega usuário logado (ICurrentUserService), cliente (se houver) e produtos
4. Venda.Registrar():
   a. valida cliente ativo, itens ≥ 1
   b. valida TODOS os itens (produto ativo, estoque suficiente) — nada debitado ainda
   c. debita estoque de cada produto + congela preço/custo/nome/sku nos itens
   d. calcula Total
5. SaveChangesAsync ÚNICO → EF persiste venda + itens + estoques em UMA transação
   (RowVersion protege contra vendas simultâneas → 409)
6. Falha em qualquer etapa → exceção → middleware → 400/404/409 → nada persiste
7. Sucesso → 201 Created + VendaDto (toast no frontend + redirect para /vendas)
```

**Cancelamento** (`POST /api/vendas/{id}/cancelar`): `venda.Cancelar()` (soft delete) + `ReporEstoque` de cada item, no mesmo `SaveChanges` — histórico preservado, estoque devolvido, venda aparece como "Cancelada" na listagem.

## 4. Novas rotas da API

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| GET | `/api/clientes` | Lista clientes | 200 |
| GET | `/api/clientes/{id}` | Detalhe | 200, 404 |
| POST | `/api/clientes` | Cria | 201, 400 |
| PUT | `/api/clientes/{id}` | Atualiza (inclui ativar/inativar) | 200, 400, 404 |
| DELETE | `/api/clientes/{id}` | Exclui (bloqueado se tem vendas) | 204, 400, 404 |
| GET | `/api/vendas` | Lista vendas (com itens) | 200 |
| GET | `/api/vendas/{id}` | Detalhe com itens | 200, 404 |
| POST | `/api/vendas` | Registra venda (baixa estoque) | 201, 400, 404, 409 |
| POST | `/api/vendas/{id}/cancelar` | Cancela (soft delete + estorno) | 200, 400, 404 |
| GET | `/api/dashboard` | Indicadores + vendas por dia | 200 |

Mudança em rota existente: `DELETE /api/produtos/{id}` agora retorna **400** se o produto tem vendas registradas ("inative-o em vez de excluir") — preserva o histórico (Doc 01 REGRA 4).

## 5. Dashboard (contexto Insights — ADR 0004)

`Application/Insights/Dashboard/DashboardService`: **lê** de Operations (vendas, produtos, clientes), nunca escreve. Nesta fase é agregação simples on-read (volume baixo por tenant); o Motor de Regras de insight cards pluga aqui na sprint de Insights sem quebrar o contrato `IDashboardService`.

Indicadores: receita total, quantidade de vendas, ticket médio, valor do estoque (custo × quantidade), clientes cadastrados, produtos cadastrados, produtos abaixo do mínimo (excluindo zerados), produtos sem estoque, e série "vendas por dia" dos últimos 14 dias (dias sem venda aparecem zerados no gráfico). Vendas canceladas ficam fora de todos os números.

## 6. Seed de demonstração

Cada bloco roda só se a tabela correspondente estiver vazia (idempotente). Em um banco novo:

- **Admin** (`admin@bmpcommerce.com` / `Admin@123`)
- **20 produtos** em 4 categorias — incluindo 2 abaixo do estoque mínimo e 2 sem estoque (para os badges e alertas terem dados)
- **15 clientes** com cidades/UFs reais, CPFs e CNPJs válidos em formato — 2 inativos
- **20 vendas** geradas pelo próprio agregado (`Venda.Registrar` com `Random(42)` determinístico), espalhadas nos últimos 14 dias, ~1/4 de balcão, 2 canceladas com estorno — estoques e totais 100% consistentes

A factory `Venda.Registrar` aceita `dataHora` opcional exatamente para seed/importação de vendas históricas; o fluxo normal usa o horário atual.

## 7. Frontend

- **Clientes**: mesma anatomia de Produtos (indicadores, busca com limpar, filtro de status, paginação, dialogs, toasts). Indicadores: total, ativos, inativos, novos este mês. CPF/CNPJ exibido com máscara.
- **Nova Venda** (`/vendas/nova`): layout POS em 2 colunas — esquerda: seleção de cliente (balcão como default), busca de produtos com clique-para-adicionar (só ativos com estoque; contador de "restante" desconta o carrinho), tabela de itens com stepper de quantidade (±, limitado ao estoque) e remoção; direita: resumo fixo (itens, subtotal, total) atualizado em tempo real + Finalizar Venda. Erro da API (ex: estoque mudou) → toast + refetch de produtos.
- **Vendas** (`/vendas`): filtros por busca de cliente, período (de/até), cliente (select), status (todas/concluídas/canceladas) e ordenação (data/total ↑↓); paginação; dialog de detalhes com itens; cancelamento com confirmação explicando o estorno.
- **Dashboard**: 8 indicadores + gráfico de barras (Recharts) "Vendas dos últimos 14 dias", com cores integradas ao tema via CSS variables (funciona em light/dark).
- **Produtos**: badge de estoque por linha — `Normal` (verde), `Baixo` (âmbar, abaixo do mínimo), `Sem estoque` (vermelho); indicador "abaixo do mínimo" alinhado à definição do dashboard (não conta zerados).

## 8. Decisões arquiteturais

1. **Venda é agregado DDD; Cliente é CRUD honesto** — aplicação direta do Doc 01 §6. Cliente não tem value objects (nem reusa o VO `Email` do Usuario): validações simples na entidade, como o documento manda para CRUD puro.
2. **Transação = SaveChanges único.** Todo o efeito da venda (cabeçalho + itens + baixas de estoque) entra no change tracker e é persistido por um único `SaveChangesAsync` — que o EF Core executa atomicamente. Não há transação manual porque não há múltiplos `SaveChanges` no fluxo.
3. **RowVersion agora, não depois.** O Doc 04 alocava concorrência otimista à Sprint 3; como esta sprint implementa a venda, o RowVersion veio junto — sem ele, duas vendas simultâneas poderiam corromper o estoque silenciosamente (Doc 01 R4). Middleware converte o conflito em 409.
4. **Snapshots de nome (ClienteNome/UsuarioNome/ProdutoNome/ProdutoSku) nas vendas.** Extensão do princípio de congelamento (REGRA 3) para exibição: o histórico exibe o que era verdade no momento da venda, sem joins e imune a renomeações futuras.
5. **Cancelar ≠ excluir.** Venda nunca sai do banco (REGRA 4). Cancelamento é soft delete com estorno de estoque na mesma transação. O filtro "Status" da listagem existe por causa disso (Concluída/Cancelada).
6. **Produto/Cliente com vendas não podem ser excluídos** — o serviço retorna falha ("inative-o em vez de excluir") e o banco tem `Restrict` como defesa em profundidade. Sem isso, exclusões quebrariam o histórico que sustenta os Insights.
7. **Dashboard vive em `Application/Insights/`** — é leitura/analytics (ADR 0004), não uma Operation. É agregação simples on-read por enquanto; o motor de regras pluga atrás do mesmo contrato na sprint de Insights.
8. **Filtros/ordenação de vendas no cliente** — consistente com o padrão documentado na Sprint 1.5: a lista completa é buscada uma vez e filtrada localmente. Volume do MVP comporta; paginação server-side já está registrada como evolução futura.
9. **Seed via domínio** — as vendas de demonstração passam por `Venda.Registrar`, não por INSERT manual, então totais congelados e estoques batem por construção.
10. **Sem TenantId nas novas entidades ainda** — mesma decisão registrada para Produto no Doc 07 do módulo: multi-tenancy de recursos de negócio (Global Query Filter) é um módulo próprio futuro, aplicado a todas as entidades de uma vez.

## 9. Validação executada

- Backend e frontend compilam com 0 erros / 0 warnings.
- Migration `AddClientesEVendas` aplicada em banco recriado do zero; seed completo confirmado (20/15/20).
- curl: CRUD de clientes (com normalização CPF/email/UF), registro de venda (201, estoque 118→113), bloqueio por estoque insuficiente (400, nada debitado), venda sem itens (400), produto sem estoque (400), cancelamento com estorno (113→118), cancelar duas vezes (400), guards de exclusão (400), auth em todas as rotas (401).
- Playwright (fluxo completo no navegador): login → dashboard com indicadores e gráfico → criar cliente → badges de estoque em Produtos → nova venda com cliente + 2 produtos (total em tempo real correto) → venda na listagem → detalhes → estoque reduzido na tela de Produtos → receita do dashboard aumentada exatamente pelo valor da venda → filtros de status/cliente/ordenação → cancelamento pela UI com estorno confirmado → dark mode → responsivo mobile. Zero erros de console.

Screenshots em [screenshots/](screenshots/) (prefixo `sprint2-`).

## 10. Próximas melhorias sugeridas

- **Motor de Insights** (Sprint 4 do Doc 04): regras plugáveis gerando frases de negócio; dashboard por papel (Funcionário sem financeiro).
- **Multi-tenancy de recursos**: TenantId + Global Query Filter em Produto/Cliente/Venda (ADR 0001), quando houver cadastro de mais de um tenant.
- **Code-splitting no frontend**: o bundle passou de 500kB com o Recharts — `import()` dinâmico por rota resolve.
- **Paginação/filtros server-side** para vendas quando o volume crescer.
- **Validação completa de dígitos verificadores** de CPF/CNPJ (hoje valida comprimento).
- **Gestão de usuários** (CRUD de usuários do tenant, Sprint 1 PASSO 7 pendente) e **Perfil da Empresa/Configurações** (Sprint 5).
