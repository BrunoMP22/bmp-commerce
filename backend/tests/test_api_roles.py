"""Gating por papel (Doc 02 §6.1, ADR 0004): Funcionário não recebe dado financeiro
nem insight financeiro — o filtro é do back-end, não da tela."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _criar_produto(client: TestClient, headers: dict[str, str], **overrides) -> dict:
    payload = {
        "nome": "Produto Papel",
        "sku": "ROL-001",
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


def _registrar_venda(client: TestClient, headers: dict[str, str], produto_id: str, quantidade: int) -> None:
    response = client.post(
        "/api/vendas",
        json={"clienteId": None, "itens": [{"produtoId": produto_id, "quantidade": quantidade}]},
        headers=headers,
    )
    assert response.status_code == 201


def test_funcionario_pode_logar_e_ver_o_proprio_perfil(
    client: TestClient, employee_headers: dict[str, str]
):
    me = client.get("/api/auth/me", headers=employee_headers)

    assert me.status_code == 200
    body = me.json()
    assert body["role"] == "Employee"
    assert body["tenantName"] == "Empresa Teste"


def test_dashboard_do_funcionario_vem_sem_financeiro(
    client: TestClient, auth_headers: dict[str, str], employee_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers)
    _registrar_venda(client, auth_headers, produto["id"], quantidade=3)

    body = client.get("/api/dashboard", headers=employee_headers).json()

    # Financeiro bloqueado no back-end.
    assert body["receita30Dias"] is None
    assert body["ticketMedio30Dias"] is None
    assert body["valorEstoque"] is None
    assert body["receitaTotal"] is None
    assert body["receitaPorCategoria"] == []
    assert all(dia["total"] is None for dia in body["vendasPorDia"])
    assert all(produto_top["receita"] is None for produto_top in body["topProdutos"])

    # Operacional preservado.
    assert body["vendas30Dias"]["atual"] == 1.0
    assert body["vendasPorDia"][-1]["quantidade"] == 1
    assert body["topProdutos"][0]["quantidade"] == 3


def test_dashboard_do_admin_permanece_completo(
    client: TestClient, auth_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers, sku="ROL-ADM")
    _registrar_venda(client, auth_headers, produto["id"], quantidade=2)

    body = client.get("/api/dashboard", headers=auth_headers).json()

    assert body["receita30Dias"]["atual"] == 20.0
    assert body["vendasPorDia"][-1]["total"] == 20.0
    assert body["topProdutos"][0]["receita"] == 20.0


def test_insights_do_funcionario_nao_incluem_financeiros(
    client: TestClient, auth_headers: dict[str, str], employee_headers: dict[str, str]
):
    produto = _criar_produto(client, auth_headers, sku="ROL-INS")
    _registrar_venda(client, auth_headers, produto["id"], quantidade=5)

    tipos_admin = {i["tipo"] for i in client.get("/api/insights", headers=auth_headers).json()["insights"]}
    tipos_funcionario = {
        i["tipo"] for i in client.get("/api/insights", headers=employee_headers).json()["insights"]
    }

    financeiros = {
        "faturamento-em-movimento",
        "margem-em-movimento",
        "ticket-medio-em-movimento",
        "campeao-de-lucro",
        "concentracao-de-produto",
        "concentracao-de-clientes",
        "capital-parado",
    }
    assert not tipos_funcionario & financeiros
    assert tipos_funcionario <= tipos_admin
