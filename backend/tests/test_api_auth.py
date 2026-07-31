from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.usuario import Usuario


def test_login_com_credenciais_validas_retorna_token(client: TestClient, admin_usuario: Usuario):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin.teste@bmpcommerce.com", "password": "Senha@123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == "admin.teste@bmpcommerce.com"
    assert body["user"]["role"] == "SuperAdmin"


def test_login_com_senha_errada_retorna_401_email_ou_senha_invalidos(
    client: TestClient, admin_usuario: Usuario
):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin.teste@bmpcommerce.com", "password": "errada"},
    )

    assert response.status_code == 401
    assert response.json() == {"message": "Email ou senha inválidos."}


def test_login_com_email_inexistente_retorna_401(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={"email": "ninguem@bmpcommerce.com", "password": "qualquer"},
    )

    assert response.status_code == 401


def test_me_sem_token_retorna_401(client: TestClient):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {"message": "Não autenticado."}


def test_me_com_token_valido_retorna_usuario_atual(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "admin.teste@bmpcommerce.com"


def test_rota_protegida_sem_token_retorna_401(client: TestClient):
    response = client.get("/api/produtos")

    assert response.status_code == 401


def test_alterar_senha_com_senha_atual_correta_retorna_204_e_troca_a_senha(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.put(
        "/api/auth/senha",
        headers=auth_headers,
        json={"senhaAtual": "Senha@123", "novaSenha": "NovaSenha@456"},
    )

    assert response.status_code == 204

    login_com_nova = client.post(
        "/api/auth/login",
        json={"email": "admin.teste@bmpcommerce.com", "password": "NovaSenha@456"},
    )
    assert login_com_nova.status_code == 200

    login_com_antiga = client.post(
        "/api/auth/login",
        json={"email": "admin.teste@bmpcommerce.com", "password": "Senha@123"},
    )
    assert login_com_antiga.status_code == 401


def test_alterar_senha_com_senha_atual_errada_retorna_400(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.put(
        "/api/auth/senha",
        headers=auth_headers,
        json={"senhaAtual": "errada", "novaSenha": "NovaSenha@456"},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Senha atual incorreta."}


def test_alterar_senha_igual_a_atual_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    response = client.put(
        "/api/auth/senha",
        headers=auth_headers,
        json={"senhaAtual": "Senha@123", "novaSenha": "Senha@123"},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "A nova senha deve ser diferente da senha atual."}


def test_alterar_senha_curta_demais_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    response = client.put(
        "/api/auth/senha",
        headers=auth_headers,
        json={"senhaAtual": "Senha@123", "novaSenha": "curta"},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "A nova senha deve ter pelo menos 8 caracteres."}


def test_alterar_senha_sem_token_retorna_401(client: TestClient):
    response = client.put(
        "/api/auth/senha",
        json={"senhaAtual": "Senha@123", "novaSenha": "NovaSenha@456"},
    )

    assert response.status_code == 401
