namespace BMPCommerce.Application.Operations.Produtos;

public record ProdutoDto(
    Guid Id,
    string Nome,
    string? Descricao,
    string Sku,
    string? CodigoBarras,
    string? Categoria,
    string UnidadeMedida,
    decimal PrecoCusto,
    decimal PrecoVenda,
    int EstoqueAtual,
    int EstoqueMinimo,
    bool Ativo,
    DateTime CreatedAt,
    DateTime? UpdatedAt);

public record CriarProdutoRequest(
    string Nome,
    string? Descricao,
    string Sku,
    string? CodigoBarras,
    string? Categoria,
    string UnidadeMedida,
    decimal PrecoCusto,
    decimal PrecoVenda,
    int EstoqueAtual,
    int EstoqueMinimo);

public record AtualizarProdutoRequest(
    string Nome,
    string? Descricao,
    string Sku,
    string? CodigoBarras,
    string? Categoria,
    string UnidadeMedida,
    decimal PrecoCusto,
    decimal PrecoVenda,
    int EstoqueAtual,
    int EstoqueMinimo,
    bool Ativo);
