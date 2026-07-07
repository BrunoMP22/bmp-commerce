using BMPCommerce.Domain.Common;

namespace BMPCommerce.Application.Operations.Usuarios;

public interface IAuthService
{
    Task<Result<LoginResult>> LoginAsync(LoginRequest request, CancellationToken cancellationToken);

    Task<Result<AuthenticatedUserResult>> GetCurrentUserAsync(Guid userId, CancellationToken cancellationToken);
}
