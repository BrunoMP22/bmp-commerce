from __future__ import annotations

from fastapi.testclient import TestClient


def _criar_produto(client: TestClient, headers: dict[str, str], **overrides) -> dict:
    payload = {
        "nome": "Produto Dash",
        "sku": "DSH-001",
        "unidadeMedida": "Unidade",
        "precoCusto": 5.0,
        "precoVenda": 10.0,
        "estoqueAtual": 50,
        "estoqueMinimo": 2,
        **overrides,
    }
    response = client.post("/api/produtos", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def _registrar_venda(client: TestClient, headers: dict[str, str], produto_id: str, quantidade: int) -> dict:
    response = client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto_id, "quantidade": quantidade}]},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_dashboard_vazio_retorna_zeros_e_listas_vazias(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/dashboard", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["receita30Dias"] == {"atual": 0.0, "anterior": 0.0, "variacaoPercentual": None}
    assert body["quantidadeVendas"] == 0
    assert len(body["vendasPorDia"]) == 30
    assert body["receitaPorCategoria"] == []
    assert body["topProdutos"] == []
    assert body["ultimasVendas"] == []
    assert body["estoqueEmAlerta"] == []


def test_dashboard_agrega_vendas_categorias_e_tops(client: TestClient, auth_headers: dict[str, str]):
    eletronico = _criar_produto(
        client, auth_headers, sku="DSH-ELE", nome="Mouse Dash", categoria="Eletrônicos"
    )
    papelaria = _criar_produto(
        client, auth_headers, sku="DSH-PAP", nome="Caderno Dash", categoria="Papelaria", precoVenda=20.0
    )

    _registrar_venda(client, auth_headers, eletronico["id"], quantidade=3)  # R$ 30
    _registrar_venda(client, auth_headers, papelaria["id"], quantidade=5)  # R$ 100

    body = client.get("/api/dashboard", headers=auth_headers).json()

    # Janela de 30 dias: as duas vendas são de agora; janela anterior vazia → sem variação.
    assert body["receita30Dias"]["atual"] == 130.0
    assert body["receita30Dias"]["variacaoPercentual"] is None
    assert body["vendas30Dias"]["atual"] == 2.0
    assert body["ticketMedio30Dias"]["atual"] == 65.0

    # Top produtos ordenado por receita.
    assert [p["sku"] for p in body["topProdutos"]] == ["DSH-PAP", "DSH-ELE"]
    assert body["topProdutos"][0]["receita"] == 100.0
    assert body["topProdutos"][0]["quantidade"] == 5

    # Categorias com participação somando 100%.
    categorias = {c["categoria"]: c for c in body["receitaPorCategoria"]}
    assert set(categorias) == {"Papelaria", "Eletrônicos"}
    soma = sum(c["participacaoPercentual"] for c in body["receitaPorCategoria"])
    assert abs(soma - 100.0) < 0.01

    # Últimas vendas (mais recente primeiro) e gráfico com o total de hoje.
    assert len(body["ultimasVendas"]) == 2
    assert body["ultimasVendas"][0]["total"] == 100.0
    assert body["vendasPorDia"][-1]["total"] == 130.0


def test_dashboard_lista_estoque_em_alerta_sem_estoque_primeiro(
    client: TestClient, auth_headers: dict[str, str]
):
    _criar_produto(client, auth_headers, sku="DSH-OK", estoqueAtual=50, estoqueMinimo=5)
    _criar_produto(client, auth_headers, sku="DSH-BAIXO", estoqueAtual=2, estoqueMinimo=10)
    _criar_produto(client, auth_headers, sku="DSH-ZERO", estoqueAtual=0, estoqueMinimo=10)

    body = client.get("/api/dashboard", headers=auth_headers).json()

    assert [p["sku"] for p in body["estoqueEmAlerta"]] == ["DSH-ZERO", "DSH-BAIXO"]
    assert body["estoqueEmAlerta"][0]["semEstoque"] is True
    assert body["produtosSemEstoque"] == 1
    assert body["produtosAbaixoMinimo"] == 1
