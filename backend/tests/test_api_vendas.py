from __future__ import annotations

from fastapi.testclient import TestClient


def _criar_produto(client: TestClient, headers: dict[str, str], **overrides) -> dict:
    payload = {
        "nome": "Produto Venda",
        "sku": "VDA-001",
        "unidadeMedida": "Unidade",
        "precoCusto": 5.0,
        "precoVenda": 10.0,
        "estoqueAtual": 10,
        "estoqueMinimo": 2,
        **overrides,
    }
    response = client.post("/api/produtos", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_registrar_venda_debita_estoque_e_retorna_total(client: TestClient, auth_headers: dict[str, str]):
    produto = _criar_produto(client, auth_headers, estoqueAtual=10)

    response = client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto["id"], "quantidade": 3}]},
        headers=auth_headers,
    )

    assert response.status_code == 201
    venda = response.json()
    assert venda["total"] == 30.0
    assert venda["quantidadeItens"] == 3
    assert venda["cancelada"] is False

    produto_atualizado = client.get(f"/api/produtos/{produto['id']}", headers=auth_headers).json()
    assert produto_atualizado["estoqueAtual"] == 7


def test_registrar_venda_consolida_itens_duplicados_do_mesmo_produto(
    client: TestClient, auth_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers, sku="VDA-002", estoqueAtual=10)

    response = client.post(
        "/api/vendas",
        json={
            "clienteId": None,
            "itens": [
                {"produtoId": produto["id"], "quantidade": 2},
                {"produtoId": produto["id"], "quantidade": 3},
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    venda = response.json()
    assert len(venda["itens"]) == 1
    assert venda["itens"][0]["quantidade"] == 5
    assert venda["total"] == 50.0


def test_registrar_venda_sem_itens_retorna_400(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/vendas", json={"clienteId": None, "itens": []}, headers=auth_headers
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Venda deve ter ao menos um item."}


def test_registrar_venda_com_estoque_insuficiente_retorna_400_e_nao_debita(
    client: TestClient, auth_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers, sku="VDA-003", estoqueAtual=2)

    response = client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto["id"], "quantidade": 999}]},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Estoque insuficiente" in response.json()["message"]

    produto_atualizado = client.get(f"/api/produtos/{produto['id']}", headers=auth_headers).json()
    assert produto_atualizado["estoqueAtual"] == 2


def test_cancelar_venda_estorna_estoque_e_bloqueia_segundo_cancelamento(
    client: TestClient, auth_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers, sku="VDA-004", estoqueAtual=10)

    venda = client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto["id"], "quantidade": 4}]},
        headers=auth_headers,
    ).json()

    produto_apos_venda = client.get(f"/api/produtos/{produto['id']}", headers=auth_headers).json()
    assert produto_apos_venda["estoqueAtual"] == 6

    cancelar = client.post(f"/api/vendas/{venda['id']}/cancelar", headers=auth_headers)
    assert cancelar.status_code == 200
    assert cancelar.json()["cancelada"] is True

    produto_apos_cancelamento = client.get(f"/api/produtos/{produto['id']}", headers=auth_headers).json()
    assert produto_apos_cancelamento["estoqueAtual"] == 10

    segundo_cancelamento = client.post(f"/api/vendas/{venda['id']}/cancelar", headers=auth_headers)
    assert segundo_cancelamento.status_code == 400
    assert segundo_cancelamento.json() == {"message": "Venda já está cancelada."}


def test_excluir_produto_com_vendas_e_bloqueado(client: TestClient, auth_headers: dict[str, str]):
    produto = _criar_produto(client, auth_headers, sku="VDA-005", estoqueAtual=10)

    client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto["id"], "quantidade": 1}]},
        headers=auth_headers,
    )

    response = client.delete(f"/api/produtos/{produto['id']}", headers=auth_headers)

    assert response.status_code == 400
    assert response.json() == {
        "message": "Produto possui vendas registradas e não pode ser excluído. Inative-o em vez de excluir."
    }


def test_obter_venda_inexistente_retorna_404(client: TestClient, auth_headers: dict[str, str]):
    response = client.get(
        "/api/vendas/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Venda não encontrada."}
