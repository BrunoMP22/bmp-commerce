using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Domain.Interfaces;

public interface IVendaRepository
{
    Task<Venda?> GetByIdAsync(Guid id, CancellationToken cancellationToken);

    Task<IReadOnlyList<Venda>> GetAllAsync(CancellationToken cancellationToken);

    Task<bool> ExisteVendaComProdutoAsync(Guid produtoId, CancellationToken cancellationToken);

    Task<bool> ExisteVendaComClienteAsync(Guid clienteId, CancellationToken cancellationToken);

    void Add(Venda venda);
}
