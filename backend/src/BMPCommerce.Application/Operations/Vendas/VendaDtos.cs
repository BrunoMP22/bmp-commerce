namespace BMPCommerce.Application.Operations.Vendas;

public record ItemVendaRequest(Guid ProdutoId, int Quantidade);

public record RegistrarVendaRequest(Guid? ClienteId, List<ItemVendaRequest> Itens);

public record ItemVendaDto(
    Guid ProdutoId,
    string ProdutoNome,
    string ProdutoSku,
    int Quantidade,
    decimal PrecoVendaMomento,
    decimal Subtotal);

public record VendaDto(
    Guid Id,
    Guid? ClienteId,
    string? ClienteNome,
    string UsuarioNome,
    DateTime DataHora,
    decimal Total,
    int QuantidadeItens,
    bool Cancelada,
    IReadOnlyList<ItemVendaDto> Itens);
