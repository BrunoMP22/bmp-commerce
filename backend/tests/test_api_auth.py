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
