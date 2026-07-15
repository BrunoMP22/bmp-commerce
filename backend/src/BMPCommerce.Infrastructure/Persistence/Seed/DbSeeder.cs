using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Enums;
using BMPCommerce.Domain.ValueObjects;
using BMPCommerce.Infrastructure.Persistence.DbContext;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.Seed;

// Seed de demonstração: cada bloco só roda se a tabela correspondente estiver
// vazia, então re-executar a API nunca duplica dados. As vendas são criadas
// pelo próprio agregado (Venda.Registrar), garantindo estoque e totais consistentes.
public static class DbSeeder
{
    private const string AdminEmail = "admin@bmpcommerce.com";
    private const string AdminPassword = "Admin@123";

    public static async Task SeedAsync(BMPCommerceDbContext dbContext, IPasswordHasher passwordHasher)
    {
        if (!await dbContext.Tenants.AnyAsync(t => t.Name == "BMP Demo"))
        {
            dbContext.Tenants.Add(new Tenant("BMP Demo", "Standard"));
        }

        var adminEmail = Email.Create(AdminEmail);
        var admin = await dbContext.Usuarios.SingleOrDefaultAsync(u => u.Email == adminEmail);

        if (admin is null)
        {
            var passwordHash = passwordHasher.Hash(AdminPassword);
            admin = new Usuario("Administrador", adminEmail, passwordHash, UserRole.SuperAdmin, tenantId: null);
            dbContext.Usuarios.Add(admin);
        }

        var produtos = await SeedProdutosAsync(dbContext);
        var clientes = await SeedClientesAsync(dbContext);

        await dbContext.SaveChangesAsync(CancellationToken.None);

        await SeedVendasAsync(dbContext, admin, produtos, clientes);

        await dbContext.SaveChangesAsync(CancellationToken.None);
    }

    private static async Task<List<Produto>> SeedProdutosAsync(BMPCommerceDbContext dbContext)
    {
        if (await dbContext.Produtos.AnyAsync())
        {
            return await dbContext.Produtos.ToListAsync();
        }

        List<Produto> produtos =
        [
            new("Caneta Esferográfica Azul", "PAP-001", "Caixa com escrita macia 1.0mm", null, "Papelaria", UnidadeMedida.Unidade, 0.80m, 1.90m, 250, 50),
            new("Caderno Universitário 200 folhas", "PAP-002", "Capa dura, 10 matérias", null, "Papelaria", UnidadeMedida.Unidade, 12.50m, 24.90m, 80, 20),
            new("Papel A4 500 folhas", "PAP-003", "Resma 75g/m²", null, "Papelaria", UnidadeMedida.Pacote, 18.50m, 32.90m, 90, 25),
            new("Mouse Sem Fio 2.4GHz", "ELE-001", "Receptor USB, 1600 DPI", "7891000100011", "Eletrônicos", UnidadeMedida.Unidade, 28.00m, 59.90m, 60, 15),
            new("Teclado Mecânico RGB", "ELE-002", "Switch blue, layout ABNT2", "7891000100028", "Eletrônicos", UnidadeMedida.Unidade, 145.00m, 289.90m, 25, 8),
            new("Headset Gamer 7.1", "ELE-003", "Drivers 50mm, microfone removível", "7891000100035", "Eletrônicos", UnidadeMedida.Unidade, 95.00m, 199.90m, 40, 10),
            new("Monitor 24\" Full HD", "ELE-004", "Painel IPS, 75Hz, HDMI", "7891000100042", "Eletrônicos", UnidadeMedida.Unidade, 520.00m, 899.90m, 15, 5),
            new("Webcam Full HD 1080p", "ELE-005", "Foco automático, microfone embutido", "7891000100059", "Eletrônicos", UnidadeMedida.Unidade, 78.00m, 149.90m, 30, 10),
            new("Hub USB-C 6 em 1", "ELE-006", "HDMI 4K, 2x USB 3.0, leitor SD", "7891000100066", "Eletrônicos", UnidadeMedida.Unidade, 62.00m, 129.90m, 45, 12),
            new("Cabo HDMI 2 metros", "ELE-007", "Versão 2.0, 4K@60Hz", "7891000100073", "Eletrônicos", UnidadeMedida.Unidade, 9.50m, 24.90m, 120, 30),
            new("Carregador Turbo 30W", "ELE-008", "USB-C Power Delivery", "7891000100080", "Eletrônicos", UnidadeMedida.Unidade, 32.00m, 69.90m, 70, 20),
            new("Fone Bluetooth TWS", "ELE-009", "Estojo com carga extra, IPX4", "7891000100097", "Eletrônicos", UnidadeMedida.Unidade, 55.00m, 119.90m, 55, 15),
            new("Mochila Executiva Notebook", "ACC-001", "Compartimento acolchoado até 15.6\"", null, "Acessórios", UnidadeMedida.Unidade, 89.00m, 179.90m, 35, 10),
            new("Suporte Notebook Alumínio", "ACC-002", "Altura regulável, dobrável", null, "Acessórios", UnidadeMedida.Unidade, 48.00m, 99.90m, 28, 8),
            new("Cadeira Ergonômica Office", "MOV-001", "Apoio lombar, braços 3D", null, "Móveis", UnidadeMedida.Unidade, 480.00m, 949.90m, 12, 4),
            new("Mesa Escritório 120cm", "MOV-002", "Tampo em MDF, estrutura em aço", null, "Móveis", UnidadeMedida.Unidade, 310.00m, 649.90m, 10, 4),
            // Abaixo do estoque mínimo — demonstram o badge "Baixo" e o alerta do dashboard.
            new("Luminária LED de Mesa", "ACC-003", "3 tons de luz, USB recarregável", null, "Acessórios", UnidadeMedida.Unidade, 35.00m, 79.90m, 3, 10),
            new("Organizador de Cabos", "ACC-004", "Kit com 20 clipes adesivos", null, "Acessórios", UnidadeMedida.Pacote, 6.00m, 15.90m, 4, 15),
            // Sem estoque — demonstram o badge "Sem estoque" e o alerta do dashboard.
            new("Mousepad Gamer XL", "ACC-005", "90x40cm, borda costurada", null, "Acessórios", UnidadeMedida.Unidade, 22.00m, 49.90m, 0, 10),
            new("Filtro de Linha 6 Tomadas", "ELE-010", "Proteção contra surtos, 1.5m", "7891000100103", "Eletrônicos", UnidadeMedida.Unidade, 27.00m, 59.90m, 0, 8),
        ];

        dbContext.Produtos.AddRange(produtos);
        return produtos;
    }

    private static async Task<List<Cliente>> SeedClientesAsync(BMPCommerceDbContext dbContext)
    {
        if (await dbContext.Clientes.AnyAsync())
        {
            return await dbContext.Clientes.ToListAsync();
        }

        List<Cliente> clientes =
        [
            new("Ana Souza", "39053344705", "(11) 98877-1234", "ana.souza@gmail.com", "São Paulo", "SP", null),
            new("Bruno Lima", "28963236885", "(21) 99655-4321", "bruno.lima@outlook.com", "Rio de Janeiro", "RJ", "Prefere contato por WhatsApp"),
            new("Carla Mendes", null, "(31) 98444-8765", "carla.mendes@gmail.com", "Belo Horizonte", "MG", null),
            new("Daniel Rocha", "84121994077", "(41) 99733-2211", null, "Curitiba", "PR", null),
            new("Eduarda Farias", null, "(51) 98122-9090", "eduarda.farias@yahoo.com", "Porto Alegre", "RS", null),
            new("Felipe Andrade", "51786881006", "(61) 99511-3344", "felipe.andrade@gmail.com", "Brasília", "DF", "Cliente corporativo"),
            new("Gabriela Nunes", null, "(71) 98833-6677", "gabi.nunes@gmail.com", "Salvador", "BA", null),
            new("Henrique Castro", "05137518000198", "(11) 3322-4455", "compras@castrotech.com.br", "São Paulo", "SP", "CNPJ — Castro Tech Ltda"),
            new("Isabela Martins", "16899535009", "(19) 99877-5544", "isa.martins@gmail.com", "Campinas", "SP", null),
            new("João Pedro Alves", null, "(27) 98456-7788", null, "Vitória", "ES", null),
            new("Larissa Costa", "72681465034", "(85) 99612-8899", "larissa.costa@gmail.com", "Fortaleza", "CE", null),
            new("Marcos Vinícius", null, "(62) 98177-2233", "marcos.vinicius@outlook.com", "Goiânia", "GO", null),
            new("Natália Pereira", "36130372027", "(48) 99933-4466", "natalia.pereira@gmail.com", "Florianópolis", "SC", null),
            new("Otávio Ramos", "45723174000110", "(11) 4002-8922", "financeiro@ramosdistribuidora.com.br", "Guarulhos", "SP", "CNPJ — Ramos Distribuidora"),
            new("Patrícia Gomes", null, "(81) 98722-1100", "patricia.gomes@gmail.com", "Recife", "PE", null),
        ];

        // Dois clientes inativos para os indicadores e o filtro de status terem dados.
        clientes[9].Atualizar(clientes[9].Nome, null, clientes[9].Telefone, clientes[9].Email, clientes[9].Cidade, clientes[9].Estado, clientes[9].Observacoes, ativo: false);
        clientes[11].Atualizar(clientes[11].Nome, null, clientes[11].Telefone, clientes[11].Email, clientes[11].Cidade, clientes[11].Estado, clientes[11].Observacoes, ativo: false);

        dbContext.Clientes.AddRange(clientes);
        return clientes;
    }

    private static async Task SeedVendasAsync(
        BMPCommerceDbContext dbContext,
        Usuario admin,
        List<Produto> produtos,
        List<Cliente> clientes)
    {
        if (await dbContext.Vendas.AnyAsync())
        {
            return;
        }

        // Random com semente fixa: o seed é determinístico entre ambientes.
        var random = new Random(42);

        // Só produtos com estoque folgado entram nas vendas de demonstração, para
        // preservar os cenários de "estoque baixo" e "sem estoque" dos badges.
        var produtosVendaveis = produtos.Where(p => p.Ativo && p.EstoqueAtual >= 20).ToList();
        var clientesAtivos = clientes.Where(c => c.Ativo).ToList();

        var agora = DateTime.UtcNow;
        var vendas = new List<Venda>();

        for (var i = 0; i < 20; i++)
        {
            // Espalha as vendas pelos últimos 14 dias (janela do gráfico do dashboard).
            var diasAtras = random.Next(0, 14);
            var dataHora = agora.Date.AddDays(-diasAtras).AddHours(random.Next(8, 19)).AddMinutes(random.Next(0, 60));

            // ~1/4 das vendas são de balcão (sem cliente).
            Cliente? cliente = random.Next(0, 4) == 0 ? null : clientesAtivos[random.Next(clientesAtivos.Count)];

            var quantidadeItens = random.Next(1, 5);
            var itens = new List<(Produto Produto, int Quantidade)>();
            var usados = new HashSet<Guid>();

            for (var j = 0; j < quantidadeItens; j++)
            {
                var produto = produtosVendaveis[random.Next(produtosVendaveis.Count)];

                if (!usados.Add(produto.Id))
                {
                    continue;
                }

                var quantidade = Math.Min(random.Next(1, 4), produto.EstoqueAtual);

                if (quantidade > 0)
                {
                    itens.Add((produto, quantidade));
                }
            }

            if (itens.Count == 0)
            {
                continue;
            }

            vendas.Add(Venda.Registrar(admin, cliente, itens, dataHora));
        }

        // Duas vendas canceladas (com estorno de estoque) para o filtro de status ter dados.
        foreach (var venda in vendas.Take(2))
        {
            venda.Cancelar();

            foreach (var item in venda.Itens)
            {
                var produto = produtos.Single(p => p.Id == item.ProdutoId);
                produto.ReporEstoque(item.Quantidade);
            }
        }

        dbContext.Vendas.AddRange(vendas);
    }
}
