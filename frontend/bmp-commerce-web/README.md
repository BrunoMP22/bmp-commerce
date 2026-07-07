# BMP Commerce — Web

Frontend do BMP Commerce: React 19 + TypeScript + Vite + Tailwind CSS v4.

## Stack

- **React Router** — roteamento e rotas protegidas
- **TanStack Query** — estado de servidor (cache, loading, erro)
- **React Hook Form + Zod** — formulários e validação
- **Lucide React** — ícones
- **Componentes estilo shadcn/ui** — Radix UI + `class-variance-authority` + `tailwind-merge`, escritos manualmente em `src/components/ui/`

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
  api/              Cliente HTTP (fetch) e chamadas à API (auth)
  components/
    ui/             Primitivas de UI (button, input, label, card)
    layout/         Sidebar, Header, Breadcrumb, StatCard, ProtectedRoute
  features/         Uma pasta por área de negócio (auth, dashboard, produtos, clientes, vendas, insights, configuracoes, perfil)
  hooks/            Hooks reutilizáveis (ex: use-theme)
  layouts/          Shells de página (AppLayout: sidebar + header + conteúdo)
  lib/              Utilitários, contexto de autenticação, storage local
  types/            Tipos TypeScript compartilhados
```

## Autenticação

O JWT retornado pelo login é persistido em `localStorage` (via `src/lib/auth-context.tsx` + `src/lib/auth-storage.ts`) e anexado automaticamente como header `Authorization: Bearer` em todas as chamadas autenticadas (`src/api/client.ts`). Rotas protegidas usam `ProtectedRoute`/`PublicOnlyRoute` (`src/components/layout/ProtectedRoute.tsx`).
