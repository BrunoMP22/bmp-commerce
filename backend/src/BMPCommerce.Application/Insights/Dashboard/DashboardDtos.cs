namespace BMPCommerce.Application.Insights.Dashboard;

public record VendaPorDiaDto(DateTime Data, decimal Total, int Quantidade);

public record DashboardDto(
    decimal ReceitaTotal,
    int QuantidadeVendas,
    int ClientesCadastrados,
    int ProdutosCadastrados,
    int ProdutosAbaixoMinimo,
    int ProdutosSemEstoque,
    decimal TicketMedio,
    decimal ValorEstoque,
    IReadOnlyList<VendaPorDiaDto> VendasPorDia);
