# BMP Commerce — Web

Frontend do BMP Commerce: React 19 + TypeScript + Vite + Tailwind CSS v4.

## Stack

- **React Router** — roteamento e rotas protegidas
- **TanStack Query** — estado de servidor (cache, loading, erro)
- **React Hook Form + Zod** — formulários e validação
- **Lucide React** — ícones
- **Sonner** — toasts de sucesso/erro
- **Recharts** — gráfico de vendas do dashboard (cores via CSS variables do tema)
- **Componentes estilo shadcn/ui** — Radix UI + `class-variance-authority` + `tailwind-merge`, escritos manualmente em `src/components/ui/` (button, input, label, card, table, dialog, alert-dialog, badge, textarea, select, checkbox)

## Rodando localmente

Pré-requisito: a API do backend rodando (ver [README raiz](../../README.md)).

```bash
npm install
npm run dev
```

A URL da API é lida de `VITE_API_URL` (já configurada em `.env.development` para `http://localhost:5050`).

## Scripts

| Comando | Descrição |
|---|---|
| `npm run dev` | Sobe o servidor de desenvolvimento (Vite) |
| `npm run build` | Type-check (`tsc -b`) + build de produção |
| `npm run preview` | Serve o build de produção localmente |
| `npm run lint` | Lint com Oxlint |

## Estrutura

```
src/
  api/              Cliente HTTP (fetch) e chamadas à API (auth, produtos)
  components/
    ui/             Primitivas de UI (button, input, label, card, table, dialog, alert-dialog, badge, textarea, select, checkbox)
    layout/         Sidebar, Header, Breadcrumb, StatCard, ThemeToggle, ProtectedRoute
  features/         Uma pasta por área de negócio (auth, dashboard, produtos, clientes, vendas, insights, configuracoes, perfil)
  hooks/            Hooks reutilizáveis (ex: use-theme)
  layouts/          Shells de página (AppLayout: sidebar + header + conteúdo)
  lib/              Utilitários, contexto de autenticação, storage local, tratamento de erro de API
  types/            Tipos TypeScript compartilhados
```

## Autenticação

O JWT retornado pelo login é persistido em `localStorage` (via `src/lib/auth-context.tsx` + `src/lib/auth-storage.ts`) e anexado automaticamente como header `Authorization: Bearer` em todas as chamadas autenticadas (`src/api/client.ts`). Rotas protegidas usam `ProtectedRoute`/`PublicOnlyRoute` (`src/components/layout/ProtectedRoute.tsx`).

## Padrão de um módulo CRUD (referência: Produtos)

Cada área de negócio com CRUD segue o mesmo esqueleto, usado como referência para novos módulos (ex: Clientes):

```
types/<recurso>.ts                          Tipos compartilhados (entidade + payloads)
api/<recurso>s.ts                            Chamadas à API (list/get/create/update/delete)
features/<recurso>s/
  <Recurso>sPage.tsx                         Página: header, indicadores, busca/filtro, tabela, paginação
  <Recurso>FormDialog.tsx                    Dialog de criar/editar (mesmo formulário para os dois fluxos)
  Delete<Recurso>Dialog.tsx                  AlertDialog de confirmação de exclusão
  <recurso>-schema.ts                        Schema Zod do formulário
```

Busca, filtro e paginação são feitos no cliente sobre a lista completa (buscada uma única vez), não a cada requisição — ver [docs/06-sprint-1.5-refinamento-mvp.md](../../docs/06-sprint-1.5-refinamento-mvp.md) para o racional.

**Exceção ao padrão — Vendas:** além da listagem (`VendasPage`, com filtros de período/cliente/status e ordenação), o módulo tem uma página dedicada de fluxo (`NovaVendaPage` em `/vendas/nova`, layout estilo PDV com carrinho e resumo em tempo real) e usa `CancelarVendaDialog` no lugar de exclusão — venda nunca é excluída, apenas cancelada com estorno de estoque (ver [docs/07-sprint-2-fluxo-comercial-completo.md](../../docs/07-sprint-2-fluxo-comercial-completo.md)).
