"""Seed de demonstração — equivalente a Infrastructure/Persistence/Seed/DbSeeder.cs.

Cada bloco só roda se a tabela correspondente estiver vazia, então reexecutar a API
nunca duplica dados. As vendas são criadas pelo próprio agregado (Venda.registrar()),
garantindo estoque e totais consistentes.

Nota sobre determinismo: usamos `random.Random(42)` (PRNG do Python) em vez do
`System.Random(42)` do C# — os algoritmos são diferentes, então a sequência de números
não é bit-a-bit idêntica entre os dois backends, mas o processo continua igualmente
determinístico (mesmo resultado a cada execução) e reproduz a mesma distribuição de
cenários: produtos com estoque baixo/zerado, clientes inativos, vendas de balcão,
vendas canceladas, tudo espalhado pelos últimos 14 dias (janela do gráfico do
dashboard).
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domain.cliente import Cliente
from app.domain.enums import UnidadeMedida, UserRole
from app.domain.produto import Produto
from app.domain.tenant import Tenant
from app.domain.usuario import Usuario
from app.domain.value_objects import Email
from app.domain.venda import Venda
from app.models.cliente import ClienteModel
from app.models.produto import ProdutoModel
from app.models.venda import VendaModel
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.venda_repository import VendaRepository

_ADMIN_EMAIL = "admin@bmpcommerce.com"
_ADMIN_PASSWORD = "Admin@123"

# (nome, sku, descricao, codigo_barras, categoria, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo)
_PRODUTOS_SEED = [
    ("Caneta Esferográfica Azul", "PAP-001", "Caixa com escrita macia 1.0mm", None, "Papelaria", UnidadeMedida.UNIDADE, "0.80", "1.90", 250, 50),
    ("Caderno Universitário 200 folhas", "PAP-002", "Capa dura, 10 matérias", None, "Papelaria", UnidadeMedida.UNIDADE, "12.50", "24.90", 80, 20),
    ("Papel A4 500 folhas", "PAP-003", "Resma 75g/m²", None, "Papelaria", UnidadeMedida.PACOTE, "18.50", "32.90", 90, 25),
    ("Mouse Sem Fio 2.4GHz", "ELE-001", "Receptor USB, 1600 DPI", "7891000100011", "Eletrônicos", UnidadeMedida.UNIDADE, "28.00", "59.90", 60, 15),
    ("Teclado Mecânico RGB", "ELE-002", "Switch blue, layout ABNT2", "7891000100028", "Eletrônicos", UnidadeMedida.UNIDADE, "145.00", "289.90", 25, 8),
    ("Headset Gamer 7.1", "ELE-003", "Drivers 50mm, microfone removível", "7891000100035", "Eletrônicos", UnidadeMedida.UNIDADE, "95.00", "199.90", 40, 10),
    ("Monitor 24\" Full HD", "ELE-004", "Painel IPS, 75Hz, HDMI", "7891000100042", "Eletrônicos", UnidadeMedida.UNIDADE, "520.00", "899.90", 15, 5),
    ("Webcam Full HD 1080p", "ELE-005", "Foco automático, microfone embutido", "7891000100059", "Eletrônicos", UnidadeMedida.UNIDADE, "78.00", "149.90", 30, 10),
    ("Hub USB-C 6 em 1", "ELE-006", "HDMI 4K, 2x USB 3.0, leitor SD", "7891000100066", "Eletrônicos", UnidadeMedida.UNIDADE, "62.00", "129.90", 45, 12),
    ("Cabo HDMI 2 metros", "ELE-007", "Versão 2.0, 4K@60Hz", "7891000100073", "Eletrônicos", UnidadeMedida.UNIDADE, "9.50", "24.90", 120, 30),
    ("Carregador Turbo 30W", "ELE-008", "USB-C Power Delivery", "7891000100080", "Eletrônicos", UnidadeMedida.UNIDADE, "32.00", "69.90", 70, 20),
    ("Fone Bluetooth TWS", "ELE-009", "Estojo com carga extra, IPX4", "7891000100097", "Eletrônicos", UnidadeMedida.UNIDADE, "55.00", "119.90", 55, 15),
    ("Mochila Executiva Notebook", "ACC-001", "Compartimento acolchoado até 15.6\"", None, "Acessórios", UnidadeMedida.UNIDADE, "89.00", "179.90", 35, 10),
    ("Suporte Notebook Alumínio", "ACC-002", "Altura regulável, dobrável", None, "Acessórios", UnidadeMedida.UNIDADE, "48.00", "99.90", 28, 8),
    ("Cadeira Ergonômica Office", "MOV-001", "Apoio lombar, braços 3D", None, "Móveis", UnidadeMedida.UNIDADE, "480.00", "949.90", 12, 4),
    ("Mesa Escritório 120cm", "MOV-002", "Tampo em MDF, estrutura em aço", None, "Móveis", UnidadeMedida.UNIDADE, "310.00", "649.90", 10, 4),
    # Abaixo do estoque mínimo — demonstram o badge "Baixo" e o alerta do dashboard.
    ("Luminária LED de Mesa", "ACC-003", "3 tons de luz, USB recarregável", None, "Acessórios", UnidadeMedida.UNIDADE, "35.00", "79.90", 3, 10),
    ("Organizador de Cabos", "ACC-004", "Kit com 20 clipes adesivos", None, "Acessórios", UnidadeMedida.PACOTE, "6.00", "15.90", 4, 15),
    # Sem estoque — demonstram o badge "Sem estoque" e o alerta do dashboard.
    ("Mousepad Gamer XL", "ACC-005", "90x40cm, borda costurada", None, "Acessórios", UnidadeMedida.UNIDADE, "22.00", "49.90", 0, 10),
    ("Filtro de Linha 6 Tomadas", "ELE-010", "Proteção contra surtos, 1.5m", "7891000100103", "Eletrônicos", UnidadeMedida.UNIDADE, "27.00", "59.90", 0, 8),
]

# (nome, cpf_cnpj, telefone, email, cidade, estado, observacoes)
_CLIENTES_SEED = [
    ("Ana Souza", "39053344705", "(11) 98877-1234", "ana.souza@gmail.com", "São Paulo", "SP", None),
    ("Bruno Lima", "28963236885", "(21) 99655-4321", "bruno.lima@outlook.com", "Rio de Janeiro", "RJ", "Prefere contato por WhatsApp"),
    ("Carla Mendes", None, "(31) 98444-8765", "carla.mendes@gmail.com", "Belo Horizonte", "MG", None),
    ("Daniel Rocha", "84121994077", "(41) 99733-2211", None, "Curitiba", "PR", None),
    ("Eduarda Farias", None, "(51) 98122-9090", "eduarda.farias@yahoo.com", "Porto Alegre", "RS", None),
    ("Felipe Andrade", "51786881006", "(61) 99511-3344", "felipe.andrade@gmail.com", "Brasília", "DF", "Cliente corporativo"),
    ("Gabriela Nunes", None, "(71) 98833-6677", "gabi.nunes@gmail.com", "Salvador", "BA", None),
    ("Henrique Castro", "05137518000198", "(11) 3322-4455", "compras@castrotech.com.br", "São Paulo", "SP", "CNPJ — Castro Tech Ltda"),
    ("Isabela Martins", "16899535009", "(19) 99877-5544", "isa.martins@gmail.com", "Campinas", "SP", None),
    ("João Pedro Alves", None, "(27) 98456-7788", None, "Vitória", "ES", None),
    ("Larissa Costa", "72681465034", "(85) 99612-8899", "larissa.costa@gmail.com", "Fortaleza", "CE", None),
    ("Marcos Vinícius", None, "(62) 98177-2233", "marcos.vinicius@outlook.com", "Goiânia", "GO", None),
    ("Natália Pereira", "36130372027", "(48) 99933-4466", "natalia.pereira@gmail.com", "Florianópolis", "SC", None),
    ("Otávio Ramos", "45723174000110", "(11) 4002-8922", "financeiro@ramosdistribuidora.com.br", "Guarulhos", "SP", "CNPJ — Ramos Distribuidora"),
    ("Patrícia Gomes", None, "(81) 98722-1100", "patricia.gomes@gmail.com", "Recife", "PE", None),
]

# Índices (0-based) dos dois clientes inativos no seed — para os indicadores e o
# filtro de status terem dados.
_CLIENTES_INATIVOS = (9, 11)


def seed_database(session: Session) -> None:
    tenants = TenantRepository(session)
    usuarios = UsuarioRepository(session)
    produtos_repo = ProdutoRepository(session)
    clientes_repo = ClienteRepository(session)
    vendas_repo = VendaRepository(session)

    if tenants.get_by_name("BMP Demo") is None:
        tenants.add(Tenant("BMP Demo", "Standard"))

    admin = usuarios.get_by_email(_ADMIN_EMAIL)
    if admin is None:
        admin = Usuario(
            name="Administrador",
            email=Email.create(_ADMIN_EMAIL),
            password_hash=hash_password(_ADMIN_PASSWORD),
            role=UserRole.SUPER_ADMIN,
            tenant_id=None,
        )
        usuarios.add(admin)

    produtos = _seed_produtos(session, produtos_repo)
    clientes = _seed_clientes(session, clientes_repo)

    session.commit()

    _seed_vendas(session, vendas_repo, produtos_repo, admin, produtos, clientes)

    session.commit()


def _seed_produtos(session: Session, repo: ProdutoRepository) -> list[Produto]:
    if session.query(ProdutoModel.id).first() is not None:
        return repo.get_all(search=None)

    produtos: list[Produto] = []

    for nome, sku, descricao, codigo_barras, categoria, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo in _PRODUTOS_SEED:
        produto = Produto(
            nome=nome,
            sku=sku,
            descricao=descricao,
            codigo_barras=codigo_barras,
            categoria=categoria,
            unidade_medida=unidade,
            preco_custo=Decimal(preco_custo),
            preco_venda=Decimal(preco_venda),
            estoque_atual=estoque_atual,
            estoque_minimo=estoque_minimo,
        )
        repo.add(produto)
        produtos.append(produto)

    return produtos


def _seed_clientes(session: Session, repo: ClienteRepository) -> list[Cliente]:
    if session.query(ClienteModel.id).first() is not None:
        return repo.get_all()

    clientes: list[Cliente] = []

    for nome, cpf_cnpj, telefone, email, cidade, estado, observacoes in _CLIENTES_SEED:
        cliente = Cliente(
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            email=email,
            cidade=cidade,
            estado=estado,
            observacoes=observacoes,
        )
        clientes.append(cliente)

    for indice in _CLIENTES_INATIVOS:
        cliente = clientes[indice]
        cliente.atualizar(
            nome=cliente.nome,
            cpf_cnpj=None,
            telefone=cliente.telefone,
            email=cliente.email,
            cidade=cliente.cidade,
            estado=cliente.estado,
            observacoes=cliente.observacoes,
            ativo=False,
        )

    for cliente in clientes:
        repo.add(cliente)

    return clientes


def _seed_vendas(
    session: Session,
    vendas_repo: VendaRepository,
    produtos_repo: ProdutoRepository,
    admin: Usuario,
    produtos: list[Produto],
    clientes: list[Cliente],
) -> None:
    if session.query(VendaModel.id).first() is not None:
        return

    # PRNG com semente fixa: o seed é determinístico entre execuções (ver nota de
    # módulo sobre não ser bit-a-bit idêntico ao `System.Random(42)` do C#).
    rng = random.Random(42)

    # Só produtos com estoque folgado entram nas vendas de demonstração, para
    # preservar os cenários de "estoque baixo" e "sem estoque" dos badges.
    produtos_vendaveis = [p for p in produtos if p.ativo and p.estoque_atual >= 20]
    clientes_ativos = [c for c in clientes if c.ativo]

    agora = datetime.now(timezone.utc)
    hoje = datetime(agora.year, agora.month, agora.day, tzinfo=timezone.utc)

    vendas: list[Venda] = []

    for _ in range(20):
        # Espalha as vendas pelos últimos 14 dias (janela do gráfico do dashboard).
        dias_atras = rng.randint(0, 13)
        data_hora = (
            hoje
            - timedelta(days=dias_atras)
            + timedelta(hours=rng.randint(8, 18), minutes=rng.randint(0, 59))
        )

        # ~1/4 das vendas são de balcão (sem cliente).
        cliente = None if rng.randrange(4) == 0 else rng.choice(clientes_ativos)

        quantidade_itens = rng.randint(1, 4)
        itens: list[tuple[Produto, int]] = []
        usados: set[UUID] = set()

        for _ in range(quantidade_itens):
            produto = rng.choice(produtos_vendaveis)

            if produto.id in usados:
                continue
            usados.add(produto.id)

            quantidade = min(rng.randint(1, 3), produto.estoque_atual)

            if quantidade > 0:
                itens.append((produto, quantidade))

        if not itens:
            continue

        venda = Venda.registrar(admin, cliente, itens, data_hora)
        vendas.append(venda)

        vendas_repo.add(venda)
        for produto, _quantidade in itens:
            produtos_repo.update(produto)

    # Sem isso, `vendas_repo.update()` abaixo não encontraria as vendas recém-criadas:
    # objetos só entram no identity map da sessão como "persistent" após o INSERT
    # realmente rodar — `add()` sozinho só os deixa "pending".
    session.flush()

    # Duas vendas canceladas (com estorno de estoque) para o filtro de status ter dados.
    for venda in vendas[:2]:
        venda.cancelar()

        for item in venda.itens:
            produto = next(p for p in produtos if p.id == item.produto_id)
            produto.repor_estoque(item.quantidade)
            produtos_repo.update(produto)

        vendas_repo.update(venda)
