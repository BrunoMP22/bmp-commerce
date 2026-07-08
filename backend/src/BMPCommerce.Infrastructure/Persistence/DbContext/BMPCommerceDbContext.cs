using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.ValueObjects;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.DbContext;

public class BMPCommerceDbContext : Microsoft.EntityFrameworkCore.DbContext, IApplicationDbContext
{
    public BMPCommerceDbContext(DbContextOptions<BMPCommerceDbContext> options)
        : base(options)
    {
    }

    public DbSet<Tenant> Tenants => Set<Tenant>();

    public DbSet<Usuario> Usuarios => Set<Usuario>();

    public DbSet<Produto> Produtos => Set<Produto>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(BMPCommerceDbContext).Assembly);
    }

    public async Task<Usuario?> GetUsuarioByEmailAsync(string email, CancellationToken cancellationToken)
    {
        Email parsedEmail;

        try
        {
            parsedEmail = Email.Create(email);
        }
        catch (Domain.Common.DomainException)
        {
            return null;
        }

        return await Usuarios.SingleOrDefaultAsync(u => u.Email == parsedEmail, cancellationToken);
    }

    public async Task<Usuario?> GetUsuarioByIdAsync(Guid id, CancellationToken cancellationToken)
        => await Usuarios.SingleOrDefaultAsync(u => u.Id == id, cancellationToken);

    public async Task<Tenant?> GetTenantByIdAsync(Guid id, CancellationToken cancellationToken)
        => await Tenants.SingleOrDefaultAsync(t => t.Id == id, cancellationToken);
}
