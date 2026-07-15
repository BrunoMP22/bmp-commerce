using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Interfaces;
using BMPCommerce.Infrastructure.Persistence.DbContext;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.Repositories;

public class ClienteRepository : IClienteRepository
{
    private readonly BMPCommerceDbContext _dbContext;

    public ClienteRepository(BMPCommerceDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<Cliente?> GetByIdAsync(Guid id, CancellationToken cancellationToken)
        => await _dbContext.Clientes.SingleOrDefaultAsync(c => c.Id == id, cancellationToken);

    public async Task<IReadOnlyList<Cliente>> GetAllAsync(CancellationToken cancellationToken)
        => await _dbContext.Clientes.OrderBy(c => c.Nome).ToListAsync(cancellationToken);

    public void Add(Cliente cliente) => _dbContext.Clientes.Add(cliente);

    public void Remove(Cliente cliente) => _dbContext.Clientes.Remove(cliente);
}
