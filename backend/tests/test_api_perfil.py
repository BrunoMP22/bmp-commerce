from __future__ import annotations

import base64

from fastapi.testclient import TestClient


def _data_url_png_valida() -> str:
    conteudo = base64.b64encode(b"png-fake-mas-base64-valido").decode()
    return f"data:image/png;base64,{conteudo}"


def test_atualizar_perfil_altera_o_nome(client: TestClient, auth_headers: dict[str, str]):
    response = client.put("/api/auth/perfil", json={"name": "Novo Nome"}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Novo Nome"

    me = client.get("/api/auth/me", headers=auth_headers).json()
    assert me["name"] == "Novo Nome"


def test_atualizar_perfil_com_nome_vazio_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    response = client.put("/api/auth/perfil", json={"name": "   "}, headers=auth_headers)

    assert response.status_code == 400
    assert response.json() == {"message": "Nome do usuário é obrigatório."}


def test_definir_avatar_persiste_e_aparece_no_me(client: TestClient, auth_headers: dict[str, str]):
    data_url = _data_url_png_valida()

    response = client.put("/api/auth/avatar", json={"imagem": data_url}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["avatar"] == data_url

    me = client.get("/api/auth/me", headers=auth_headers).json()
    assert me["avatar"] == data_url


def test_definir_avatar_com_formato_invalido_retorna_400(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.put(
        "/api/auth/avatar",
        json={"imagem": "data:image/gif;base64,R0lGOD"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Formato de imagem inválido" in response.json()["message"]


def test_definir_avatar_com_base64_corrompido_retorna_400(
    client: TestClient, auth_headers: dict[str, str]
):
    response = client.put(
        "/api/auth/avatar",
        json={"imagem": "data:image/png;base64,%%%nao-e-base64%%%"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "corrompida" in response.json()["message"]


def test_definir_avatar_grande_demais_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    conteudo = base64.b64encode(b"x" * (301 * 1024)).decode()

    response = client.put(
        "/api/auth/avatar",
        json={"imagem": f"data:image/jpeg;base64,{conteudo}"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "limite é 300 KB" in response.json()["message"]


def test_remover_avatar_volta_para_null(client: TestClient, auth_headers: dict[str, str]):
    client.put("/api/auth/avatar", json={"imagem": _data_url_png_valida()}, headers=auth_headers)

    response = client.delete("/api/auth/avatar", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["avatar"] is None


def test_perfil_sem_token_retorna_401(client: TestClient):
    assert client.put("/api/auth/perfil", json={"name": "X"}).status_code == 401
    assert client.put("/api/auth/avatar", json={"imagem": "x"}).status_code == 401
    assert client.delete("/api/auth/avatar").status_code == 401
