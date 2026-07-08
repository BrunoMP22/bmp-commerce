using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Interfaces;
using BMPCommerce.Infrastructure.Persistence.DbContext;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.Repositories;

public class ProdutoRepository : IProdutoRepository
{
    private readonly BMPCommerceDbContext _dbContext;

    public ProdutoRepository(BMPCommerceDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<Produto?> GetByIdAsync(Guid id, CancellationToken cancellationToken)
        => await _dbContext.Produtos.SingleOrDefaultAsync(p => p.Id == id, cancellationToken);

    public async Task<IReadOnlyList<Produto>> GetAllAsync(string? search, CancellationToken cancellationToken)
    {
        var query = _dbContext.Produtos.AsQueryable();

        if (!string.IsNullOrWhiteSpace(search))
        {
            var termo = search.Trim();
            query = query.Where(p => p.Nome.Contains(termo) || p.Sku.Contains(termo));
        }

        return await query.OrderBy(p => p.Nome).ToListAsync(cancellationToken);
    }

    public async Task<bool> ExisteSkuAsync(string sku, Guid? ignorarId, CancellationToken cancellationToken)
    {
        var query = _dbContext.Produtos.Where(p => p.Sku == sku);

        if (ignorarId is not null)
        {
            query = query.Where(p => p.Id != ignorarId);
        }

        return await query.AnyAsync(cancellationToken);
    }

    public void Add(Produto produto) => _dbContext.Produtos.Add(produto);

    public void Remove(Produto produto) => _dbContext.Produtos.Remove(produto);
}
