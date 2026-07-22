from __future__ import annotations

import pytest

from app.core.exceptions import DomainException
from app.domain.cliente import Cliente


def test_normaliza_cpf_removendo_pontuacao():
    cliente = Cliente(
        nome="Ana Souza",
        cpf_cnpj="390.533.447-05",
        telefone=None,
        email=None,
        cidade=None,
        estado=None,
        observacoes=None,
    )

    assert cliente.cpf_cnpj == "39053344705"


def test_cpf_cnpj_com_tamanho_invalido_levanta_domain_exception():
    with pytest.raises(DomainException, match="CPF/CNPJ inválido"):
        Cliente(
            nome="Ana Souza",
            cpf_cnpj="123",
            telefone=None,
            email=None,
            cidade=None,
            estado=None,
            observacoes=None,
        )


def test_normaliza_email_para_minusculas():
    cliente = Cliente(
        nome="Ana Souza",
        cpf_cnpj=None,
        telefone=None,
        email="ANA@Example.COM",
        cidade=None,
        estado=None,
        observacoes=None,
    )

    assert cliente.email == "ana@example.com"


def test_estado_deve_ter_duas_letras():
    with pytest.raises(DomainException, match="sigla UF"):
        Cliente(
            nome="Ana Souza",
            cpf_cnpj=None,
            telefone=None,
            email=None,
            cidade=None,
            estado="São Paulo",
            observacoes=None,
        )


def test_estado_normalizado_para_maiuscula():
    cliente = Cliente(
        nome="Ana Souza",
        cpf_cnpj=None,
        telefone=None,
        email=None,
        cidade=None,
        estado="sp",
        observacoes=None,
    )

    assert cliente.estado == "SP"


def test_nome_vazio_levanta_domain_exception():
    with pytest.raises(DomainException, match="Nome do cliente é obrigatório"):
        Cliente(
            nome="",
            cpf_cnpj=None,
            telefone=None,
            email=None,
            cidade=None,
            estado=None,
            observacoes=None,
        )


def test_atualizar_desativa_cliente():
    cliente = Cliente(
        nome="Ana Souza",
        cpf_cnpj=None,
        telefone=None,
        email=None,
        cidade=None,
        estado=None,
        observacoes=None,
    )
    assert cliente.ativo is True

    cliente.atualizar(
        nome=cliente.nome,
        cpf_cnpj=None,
        telefone=None,
        email=None,
        cidade=None,
        estado=None,
        observacoes=None,
        ativo=False,
    )

    assert cliente.ativo is False
    assert cliente.updated_at is not None
