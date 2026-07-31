# 10 — Configurações (Sprint 4)

Entrega da aba Configurações (Doc 04 Sprint 5 PASSO 2-3, antecipada): aparência,
segurança da conta, idioma/região e informações do sistema.

## O que foi entregue

### Aparência — tema Claro / Escuro / Sistema

- O tema deixou de ser um hook com estado duplicado (`hooks/use-theme.ts`, um estado
  por componente) e virou um **ThemeProvider** (`src/lib/theme-context.tsx`), no mesmo
  padrão do `AuthProvider`: uma única fonte de verdade compartilhada por header,
  toaster e página de Configurações.
- Três preferências: `light`, `dark` e **`system`** (nova) — a opção Sistema
  acompanha o `prefers-color-scheme` do dispositivo **em tempo real** (listener de
  mudança, não só leitura inicial).
- Persistência em `localStorage` (chave `bmp_theme`, compatível com valores antigos).
  Preferência de tema é do **dispositivo**, não da conta — por isso não vai ao banco
  no MVP.
- O toggle do header continua funcionando: alterna o tema resolvido e grava uma
  preferência explícita.

### Segurança — alteração de senha

- `PUT /api/auth/senha` (`{ senhaAtual, novaSenha }` → 204): exige a **senha atual**
  mesmo com o usuário autenticado — um token vazado sozinho não toma a conta.
- Regras no `AuthService` (mensagens pt-BR, padrão do projeto): senha atual incorreta
  → 400; nova senha igual à atual → 400; nova senha com menos de 8 caracteres → 400.
- Domínio já tinha `Usuario.change_password()`; foi adicionado o
  `UsuarioRepository.update()` (mesmo padrão de sincronização dos outros repositórios).
- Formulário na tela com validação Zod espelhando as regras + confirmação de senha,
  toasts de sucesso/erro e reset após alterar.

### Idioma e região

- pt-BR e R$ exibidos como valores fixos, com aviso honesto: único idioma do MVP —
  sem select desabilitado fingindo opção que não existe.

### Sobre o sistema

- `GET /api/sistema/info` → `{ nome, versao, ambiente }` (autenticado).
- A tela mostra versão da API, ambiente (badge) e link para a documentação
  (`/docs` do FastAPI).

## Testes

- +5 testes de integração em `tests/test_api_auth.py`: troca com sucesso (login com a
  senha nova passa, com a antiga falha), senha atual errada, nova igual à atual,
  nova curta demais (mensagem exata) e sem token.
- O `conftest.py` agora usa `os.environ.setdefault("DATABASE_URL", ...)`: máquinas sem
  a instância padrão `localhost` (ex: só LocalDB) rodam a suíte exportando
  `DATABASE_URL` para o banco de teste da sua instância. Suíte completa: **60 testes**.

## Fora de escopo (fica para o Perfil)

- Nome/foto do usuário e perfil da empresa (upload de logo) — Doc 04 Sprint 5 PASSO 1.
- Revogação de sessões ativas (JWT é stateless no MVP; expira em 8h).
