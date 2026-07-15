using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Domain.Interfaces;

public interface IClienteRepository
{
    Task<Cliente?> GetByIdAsync(Guid id, CancellationToken cancellationToken);

    Task<IReadOnlyList<Cliente>> GetAllAsync(CancellationToken cancellationToken);

    void Add(Cliente cliente);

    void Remove(Cliente cliente);
}
