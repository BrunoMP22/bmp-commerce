using BMPCommerce.Domain.Common;

namespace BMPCommerce.Application.Operations.Produtos;

public interface IProdutoService
{
    Task<IReadOnlyList<ProdutoDto>> ListarAsync(string? search, CancellationToken cancellationToken);

    Task<ProdutoDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken);

    Task<Result<ProdutoDto>> CriarAsync(CriarProdutoRequest request, CancellationToken cancellationToken);

    Task<Result<ProdutoDto>> AtualizarAsync(Guid id, AtualizarProdutoRequest request, CancellationToken cancellationToken);

    Task ExcluirAsync(Guid id, CancellationToken cancellationToken);
}
