# Documento 06 — Sprint 1.5: Refinamento do MVP

**Projeto:** BMP Commerce
**Área:** BMP | Data & Analytics
**Status:** Concluído
**Depende de:** Marco 1 (executável) e módulo Produtos (vertical slice)

---

## 1. Objetivo

Sprint intermediária, sem novas funcionalidades de negócio. Consolidar o que já existe: revisar arquitetura, consistência, código duplicado e elevar a qualidade visual do frontend a um nível de "software comercial", antes de iniciar o módulo Clientes.

## 2. Auditoria realizada

Revisão sistemática de todo o código escrito até aqui (Domain, Application, Infrastructure, API e todo o frontend), procurando por:

- Inconsistências entre o módulo de Auth (primeiro construído) e o módulo de Produtos (construído depois, com um padrão mais maduro de tratamento de erros)
- Código duplicado no frontend (tratamento de erro de API, toggle de tema, links de navegação da sidebar)
- Nomenclatura divergente entre arquivos que deveriam seguir o mesmo padrão
- Oportunidades de UX que o módulo de Produtos ainda não explorava (estados vazios, paginação, filtros, indicadores)

## 3. Changelog

### Backend

| Mudança | Arquivo(s) | Tipo |
|---|---|---|
| `AuthService.ObterUsuarioAtualAsync` agora lança `NotFoundException` em vez de devolver `Result<T>.Failure` | `AuthService.cs`, `IAuthService.cs` | Consistência |
| `AuthController.Me()` simplificado (sem checagem manual de `IsFailure`, delega ao middleware) | `AuthController.cs` | Consistência |
| Renomeado `GetCurrentUserAsync` → `ObterUsuarioAtualAsync` | `IAuthService.cs`, `AuthService.cs` | Nomenclatura |
| Renomeado `AuthModels.cs` → `AuthDtos.cs` (padroniza com `ProdutoDtos.cs`) | `Operations/Usuarios/` | Nomenclatura |
| Logs adicionados: `LogWarning` em `NotFoundException`/`DomainException`, `LogInformation`/`LogWarning` em login bem-sucedido/malsucedido | `ExceptionHandlingMiddleware.cs`, `AuthService.cs` | Observabilidade |
| Erros de model binding automático (JSON malformado, tipo de campo errado) agora respondem no mesmo formato `{ message }` do resto da API, via `ApiBehaviorOptions.InvalidModelStateResponseFactory` | `Program.cs` | Consistência |
| Novo pacote `Microsoft.Extensions.Logging.Abstractions` na Application (só abstração, sem provider concreto) | `BMPCommerce.Application.csproj` | Infraestrutura |
| Criado `backend/README.md`: convenções de camadas, padrão de vertical slice, política de erros (`Result` vs exceções), justificativa da nomenclatura PT/EN | `backend/README.md` (novo) | Documentação |

### Frontend

| Mudança | Arquivo(s) | Tipo |
|---|---|---|
| Extraído `getErrorMessage()`, eliminando 3 repetições de `error instanceof ApiError ? ... : ...` | `lib/errors.ts` (novo) | Duplicação |
| Extraído `<ThemeToggle />`, eliminando duplicação entre `LoginPage` e `Header` | `components/layout/ThemeToggle.tsx` (novo) | Duplicação |
| Extraído `<SidebarNavLink />` dentro do `Sidebar`, eliminando duplicação entre os itens de navegação e o link de Perfil; adicionada barra de destaque (accent bar) no item ativo | `Sidebar.tsx` | Duplicação + UX |
| `StatCard` ganhou prop `tone` (cores por contexto: azul/verde/âmbar) e `tabular-nums` nos valores | `StatCard.tsx` | Visual |
| `Card` ganhou `hover:shadow-md` com transição | `card.tsx` | Visual |
| `DashboardPage`: copy revisado ("Bem-vindo de volta, {nome}" no lugar do texto temporário de marco executável), cards com tom de cor | `DashboardPage.tsx` | Visual/Copy |
| `ProdutosPage`: 4 cards de indicadores no topo (Total cadastrados, Produtos ativos, Abaixo do estoque mínimo, Valor total em estoque) — calculados localmente, sem novo endpoint | `ProdutosPage.tsx` | Funcionalidade visual |
| `ProdutosPage`: filtro de Status (Todos/Ativos/Inativos) | `ProdutosPage.tsx` | Funcionalidade |
| `ProdutosPage`: busca ganhou botão de limpar (×) | `ProdutosPage.tsx` | UX |
| `ProdutosPage`: paginação client-side (10 por página) com legenda "Mostrando X–Y de N produtos" | `ProdutosPage.tsx` | Funcionalidade |
| `ProdutosPage`: colunas Preço/Estoque alinhadas à direita (convenção de tabelas numéricas) | `ProdutosPage.tsx` | Visual |
| Removido `hooks/use-debounced-value.ts` (ficou sem uso após a migração da busca para client-side) | — | Limpeza |

## 4. Decisões arquiteturais

### 4.1 `Result<T>`/`Result` só para regras de negócio; "não encontrado" é sempre exceção

Esta foi a inconsistência mais importante encontrada na auditoria: o módulo de Auth (construído primeiro) usava `Result<T>.Failure("Usuário não encontrado.")`, enquanto o módulo de Produtos (construído depois, quando o padrão já tinha amadurecido) usa `NotFoundException` capturada pelo middleware. Alinhei o Auth ao padrão mais novo, e documentei a regra explicitamente no `backend/README.md` para não regredir em módulos futuros: **`Result` é só para falhas de regra de negócio que o usuário pode corrigir no input** (SKU duplicado, credenciais inválidas). "Não encontrado" nunca usa `Result` — é sempre `NotFoundException`, tratada uma única vez no middleware.

### 4.2 Nomenclatura mista PT/EN mantida — documentada, não "corrigida"

Cheguei a considerar padronizar tudo em português ou tudo em inglês, mas decidi **não tocar nisso**. Entidades de domínio em português (`Usuario`, `Produto`) refletem a linguagem do negócio; termos técnicos em inglês (`IJwtService`, `NotFoundException`) seguem a convenção do ecossistema .NET. Renomear qualquer um dos dois lados agora seria invasivo (tocaria migrations, rotas, contratos já em uso) sem ganho real — e o pedido era para não quebrar decisões arquiteturais existentes. Documentei a convenção no `backend/README.md` para que não seja "corrigida" por engano numa sprint futura.

Fiz uma correção pontual, mais estreita: os **métodos de serviço** do Auth (`GetCurrentUserAsync`) estavam em inglês enquanto os do Produto (`ObterPorIdAsync`, `CriarAsync`...) estão em português — isso não era a mistura intencional documentada acima, era só o Auth não ter acompanhado o padrão que se consolidou depois. Alinhei.

### 4.3 Stats de Produtos calculados a partir do dataset completo, não da lista filtrada

Decisão importante para os 4 cards de indicadores: eles precisavam refletir o catálogo inteiro, não a view filtrada pela busca/status — senão "Total cadastrados" mudaria toda vez que o usuário digitasse algo na busca, o que seria confuso. Isso exigiu uma mudança de arquitetura na página: em vez de mandar o termo de busca para a API (`GET /produtos?search=...`) a cada tecla digitada, a página agora **busca a lista completa uma única vez** e faz busca, filtro de status e paginação inteiramente no cliente. Isso bate com a orientação explícita do pedido ("calculados localmente utilizando os dados já existentes").

O endpoint `GET /produtos?search=` **continua existindo e funcionando** no backend — não removi capacidade nenhuma da API, só troquei a estratégia de consumo desta tela específica. Consequência boa: a busca ficou instantânea (sem round-trip de rede), e o hook de debounce que existia só para isso virou código morto, então removi.

### 4.4 Skeleton loading no Dashboard: avaliado e descartado

Cheguei a planejar um skeleton para os 3 cards de status (API/Banco/Autenticação) do Dashboard enquanto a chamada a `/auth/me` está pendente. Na prática, isso nunca seria visível: a query usa `initialData` vindo do contexto de autenticação (que já está populado antes da página renderizar, já que a rota é protegida), então `isPending` nunca fica `true` de forma perceptível. Implementar o skeleton seria código morto. Não fiz.

### 4.5 "Valor total em estoque" usa preço de custo, não preço de venda

Ambiguidade possível no pedido. Optei por **preço de custo × estoque atual** por ser a interpretação contábil padrão de "valor do estoque" (valor do ativo imobilizado em mercadoria) — preço de venda representaria "receita potencial", um indicador diferente. Se a intenção era outra, é só avisar que troco.

### 4.6 Paginação client-side, não server-side

"Paginação preparada" foi interpretado como paginação real (não um placeholder desabilitado), mas client-side: o catálogo é pequeno neste estágio do MVP, e paginar no cliente sobre os dados já carregados é mais simples do que adicionar parâmetros de paginação à API, sem perda de funcionalidade percebida pelo usuário. Se o catálogo crescer muito (centenas/milhares de produtos), a paginação deveria migrar para server-side — fica registrado como gatilho para uma sprint futura.

## 5. O que ficou para sprints futuras

- **Paginação server-side** — só necessária se o catálogo crescer muito; client-side resolve bem o volume atual do MVP.
- **Logging estruturado por operação de CRUD** (ex: log de cada criação/edição/exclusão de Produto) — hoje só o fluxo de autenticação tem log de auditoria explícito; write-operations de Produto não têm log dedicado (ficam cobertas pelo log padrão de request do ASP.NET Core). Avaliar se faz sentido quando houver necessidade real de trilha de auditoria de negócio.
- **Tooltip customizado nos ícones da sidebar recolhida** — hoje usa o `title` nativo do navegador (funcional, mas não estilizado).
- **Radix Select completo** no lugar do `<select>` nativo estilizado — o nativo é suficiente para as poucas opções existentes (Unidade de Medida, filtro de Status); o dropdown nativo não é 100% estilizável em todos os navegadores.
- Qualquer coisa relacionada a Categorias, Clientes, Vendas ou estoque avançado — fora do escopo desta sprint por definição.

## 6. Como validar

Build de backend e frontend limpos (0 erros/warnings). Testes manuais via curl (backend) e navegador automatizado (frontend) cobrindo: login, CRUD completo de Produtos, filtro de status, busca com limpar, paginação, dark/light mode, responsividade em desktop/tablet/mobile. Capturas de tela em [docs/screenshots/](screenshots/).
