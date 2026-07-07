using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Application.Common.Abstractions;

public interface IApplicationDbContext
{
    Task<Usuario?> GetUsuarioByEmailAsync(string email, CancellationToken cancellationToken);

    Task<Usuario?> GetUsuarioByIdAsync(Guid id, CancellationToken cancellationToken);

    Task<Tenant?> GetTenantByIdAsync(Guid id, CancellationToken cancellationToken);

    Task<int> SaveChangesAsync(CancellationToken cancellationToken);
}
