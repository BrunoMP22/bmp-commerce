# 12 — Aba Perfil

Entrega da aba Perfil (Doc 04 Sprint 5 PASSO 3): identidade do usuário — foto de
perfil, edição de nome e visão da conta. Fecha o último placeholder do app.

## O que foi entregue

### Foto de perfil (avatar)

- **Fluxo**: o navegador redimensiona a imagem escolhida (recorte central 256×256,
  JPEG ~85%) via canvas **antes** do upload — o backend nunca recebe uma foto de
  8 MB da câmera.
- **Transporte/armazenamento**: data URL (JSON) persistida na coluna nova
  `usuarios.avatar` (migration `b3f2c9a1d4e7`). Sem multipart, sem serviço de
  arquivos, sem dependência nova — para o tamanho de um avatar (≤ 300 KB
  decodificado, validado no backend), o custo de base64 no banco é aceitável no
  MVP; trocar por storage de arquivos no futuro é uma mudança de implementação
  atrás do mesmo contrato (`avatar: string | null`).
- **Validações no backend** (mensagens pt-BR): formato JPEG/PNG/WebP, base64
  íntegro, limite de 300 KB. `PUT /api/auth/avatar` e `DELETE /api/auth/avatar`
  devolvem o usuário atualizado.
- O avatar aparece no **header** (que agora é um atalho para /perfil) e na aba.

### Dados pessoais

- `PUT /api/auth/perfil` altera o nome (validação no domínio:
  `Usuario.alterar_nome`). Email fica somente leitura — é o login no MVP.
- `AuthenticatedUserResult` ganhou `avatar` e `criadoEm` ("membro desde").

### Conta e acesso

- Papel com descrição do que pode (SuperAdmin/Admin/Employee), vínculo
  (empresa ou Plataforma), membro desde e atalho para alterar senha em
  Configurações → Segurança (sem duplicar o formulário).

### Sessão no frontend

- `AuthContext.updateUser()` atualiza o usuário guardado preservando o token;
  a página ressincroniza com `GET /api/auth/me` ao abrir (sessões gravadas antes
  de `avatar`/`criadoEm` existirem ganham os campos novos sem relogar).

## Fora de escopo (registrado)

- **PerfilEmpresa + logo do tenant** (Doc 04 Sprint 5 PASSO 1): o usuário de
  demonstração é SuperAdmin de plataforma, sem tenant — a seção de empresa não
  teria dado para aparecer. Entra quando houver fluxo de usuários Admin por tenant.

## Testes

`tests/test_api_perfil.py` (+8): renomear (refletido no /me), nome vazio,
avatar válido persistido, formato inválido, base64 corrompido, tamanho excedido,
remoção e rotas sem token. Suíte completa: **71 testes**.
