from __future__ import annotations

from fastapi.testclient import TestClient

_PAYLOAD = {
    "nome": "Caneta Azul",
    "sku": "PAP-100",
    "unidadeMedida": "Unidade",
    "precoCusto": 0.8,
    "precoVenda": 1.9,
    "estoqueAtual": 100,
    "estoqueMinimo": 10,
}


def test_criar_e_listar_produto(client: TestClient, auth_headers: dict[str, str]):
    create = client.post("/api/produtos", json=_PAYLOAD, headers=auth_headers)
    assert create.status_code == 201
    body = create.json()
    assert body["sku"] == "PAP-100"
    assert body["ativo"] is True

    listar = client.get("/api/produtos", headers=auth_headers)
    assert listar.status_code == 200
    assert any(p["sku"] == "PAP-100" for p in listar.json())


def test_criar_produto_com_sku_duplicado_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    client.post("/api/produtos", json=_PAYLOAD, headers=auth_headers)

    duplicado = client.post("/api/produtos", json=_PAYLOAD, headers=auth_headers)

    assert duplicado.status_code == 400
    assert duplicado.json() == {"message": "Já existe um produto com esse SKU."}


def test_criar_produto_com_unidade_medida_invalida_retorna_400(
    client: TestClient, auth_headers: dict[str, str]
):
    payload = {**_PAYLOAD, "sku": "PAP-101", "unidadeMedida": "Tonelada"}

    response = client.post("/api/produtos", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.json() == {"message": "Unidade de medida inválida."}


def test_obter_produto_inexistente_retorna_404(client: TestClient, auth_headers: dict[str, str]):
    response = client.get(
        "/api/produtos/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Produto não encontrado."}


def test_atualizar_produto(client: TestClient, auth_headers: dict[str, str]):
    created = client.post("/api/produtos", json=_PAYLOAD, headers=auth_headers).json()

    update_payload = {**_PAYLOAD, "nome": "Caneta Azul Editada", "precoVenda": 2.5, "ativo": True}
    response = client.put(f"/api/produtos/{created['id']}", json=update_payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["nome"] == "Caneta Azul Editada"
    assert response.json()["precoVenda"] == 2.5


def test_excluir_produto_sem_vendas_retorna_204(client: TestClient, auth_headers: dict[str, str]):
    created = client.post("/api/produtos", json=_PAYLOAD, headers=auth_headers).json()

    response = client.delete(f"/api/produtos/{created['id']}", headers=auth_headers)

    assert response.status_code == 204

    obter = client.get(f"/api/produtos/{created['id']}", headers=auth_headers)
    assert obter.status_code == 404
