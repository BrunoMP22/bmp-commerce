using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Domain.Interfaces;

public interface IProdutoRepository
{
    Task<Produto?> GetByIdAsync(Guid id, CancellationToken cancellationToken);

    Task<IReadOnlyList<Produto>> GetAllAsync(string? search, CancellationToken cancellationToken);

    Task<bool> ExisteSkuAsync(string sku, Guid? ignorarId, CancellationToken cancellationToken);

    void Add(Produto produto);

    void Remove(Produto produto);
}
