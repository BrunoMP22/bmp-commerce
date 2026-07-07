using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Application.Operations.Usuarios;

public class AuthService : IAuthService
{
    private readonly IApplicationDbContext _dbContext;
    private readonly IPasswordHasher _passwordHasher;
    private readonly IJwtService _jwtService;

    public AuthService(IApplicationDbContext dbContext, IPasswordHasher passwordHasher, IJwtService jwtService)
    {
        _dbContext = dbContext;
        _passwordHasher = passwordHasher;
        _jwtService = jwtService;
    }

    public async Task<Result<LoginResult>> LoginAsync(LoginRequest request, CancellationToken cancellationToken)
    {
        var usuario = await _dbContext.GetUsuarioByEmailAsync(request.Email, cancellationToken);

        if (usuario is null || !usuario.IsActive || !_passwordHasher.Verify(request.Password, usuario.PasswordHash))
        {
            return Result<LoginResult>.Failure("Email ou senha inválidos.");
        }

        Tenant? tenant = null;

        if (usuario.TenantId is not null)
        {
            tenant = await _dbContext.GetTenantByIdAsync(usuario.TenantId.Value, cancellationToken);

            if (tenant is null || !tenant.IsActive)
            {
                return Result<LoginResult>.Failure("Empresa inativa ou não encontrada.");
            }
        }

        var token = _jwtService.GenerateToken(usuario);
        var user = MapToResult(usuario, tenant);

        return Result<LoginResult>.Success(new LoginResult(token, user));
    }

    public async Task<Result<AuthenticatedUserResult>> GetCurrentUserAsync(Guid userId, CancellationToken cancellationToken)
    {
        var usuario = await _dbContext.GetUsuarioByIdAsync(userId, cancellationToken);

        if (usuario is null)
        {
            return Result<AuthenticatedUserResult>.Failure("Usuário não encontrado.");
        }

        var tenant = usuario.TenantId is not null
            ? await _dbContext.GetTenantByIdAsync(usuario.TenantId.Value, cancellationToken)
            : null;

        return Result<AuthenticatedUserResult>.Success(MapToResult(usuario, tenant));
    }

    private static AuthenticatedUserResult MapToResult(Usuario usuario, Tenant? tenant) => new(
        usuario.Id,
        usuario.Name,
        usuario.Email.Value,
        usuario.Role.ToString(),
        usuario.TenantId,
        tenant?.Name);
}
