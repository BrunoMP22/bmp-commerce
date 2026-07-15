using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Interfaces;
using BMPCommerce.Infrastructure.Persistence.DbContext;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.Repositories;

public class VendaRepository : IVendaRepository
{
    private readonly BMPCommerceDbContext _dbContext;

    public VendaRepository(BMPCommerceDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<Venda?> GetByIdAsync(Guid id, CancellationToken cancellationToken)
        => await _dbContext.Vendas
            .Include(v => v.Itens)
            .SingleOrDefaultAsync(v => v.Id == id, cancellationToken);

    public async Task<IReadOnlyList<Venda>> GetAllAsync(CancellationToken cancellationToken)
        => await _dbContext.Vendas
            .Include(v => v.Itens)
            .OrderByDescending(v => v.DataHora)
            .ToListAsync(cancellationToken);

    public async Task<bool> ExisteVendaComProdutoAsync(Guid produtoId, CancellationToken cancellationToken)
        => await _dbContext.Set<ItemVenda>().AnyAsync(i => i.ProdutoId == produtoId, cancellationToken);

    public async Task<bool> ExisteVendaComClienteAsync(Guid clienteId, CancellationToken cancellationToken)
        => await _dbContext.Vendas.AnyAsync(v => v.ClienteId == clienteId, cancellationToken);

    public void Add(Venda venda) => _dbContext.Vendas.Add(venda);
}
