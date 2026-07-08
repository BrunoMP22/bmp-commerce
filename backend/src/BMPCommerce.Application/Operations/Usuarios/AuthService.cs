using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Application.Common.Exceptions;
using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Entities;
using Microsoft.Extensions.Logging;

namespace BMPCommerce.Application.Operations.Usuarios;

public class AuthService : IAuthService
{
    private readonly IApplicationDbContext _dbContext;
    private readonly IPasswordHasher _passwordHasher;
    private readonly IJwtService _jwtService;
    private readonly ILogger<AuthService> _logger;

    public AuthService(
        IApplicationDbContext dbContext,
        IPasswordHasher passwordHasher,
        IJwtService jwtService,
        ILogger<AuthService> logger)
    {
        _dbContext = dbContext;
        _passwordHasher = passwordHasher;
        _jwtService = jwtService;
        _logger = logger;
    }

    public async Task<Result<LoginResult>> LoginAsync(LoginRequest request, CancellationToken cancellationToken)
    {
        var usuario = await _dbContext.GetUsuarioByEmailAsync(request.Email, cancellationToken);

        if (usuario is null || !usuario.IsActive || !_passwordHasher.Verify(request.Password, usuario.PasswordHash))
        {
            _logger.LogWarning("Tentativa de login falhou para o email {Email}.", request.Email);
            return Result<LoginResult>.Failure("Email ou senha inválidos.");
        }

        Tenant? tenant = null;

        if (usuario.TenantId is not null)
        {
            tenant = await _dbContext.GetTenantByIdAsync(usuario.TenantId.Value, cancellationToken);

            if (tenant is null || !tenant.IsActive)
            {
                _logger.LogWarning(
                    "Login bloqueado para o usuário {UserId}: tenant {TenantId} inativo ou não encontrado.",
                    usuario.Id,
                    usuario.TenantId);
                return Result<LoginResult>.Failure("Empresa inativa ou não encontrada.");
            }
        }

        var token = _jwtService.GenerateToken(usuario);
        var user = MapToResult(usuario, tenant);

        _logger.LogInformation("Login bem-sucedido para o usuário {UserId}.", usuario.Id);

        return Result<LoginResult>.Success(new LoginResult(token, user));
    }

    public async Task<AuthenticatedUserResult> ObterUsuarioAtualAsync(Guid userId, CancellationToken cancellationToken)
    {
        var usuario = await _dbContext.GetUsuarioByIdAsync(userId, cancellationToken)
            ?? throw new NotFoundException("Usuário não encontrado.");

        var tenant = usuario.TenantId is not null
            ? await _dbContext.GetTenantByIdAsync(usuario.TenantId.Value, cancellationToken)
            : null;

        return MapToResult(usuario, tenant);
    }

    private static AuthenticatedUserResult MapToResult(Usuario usuario, Tenant? tenant) => new(
        usuario.Id,
        usuario.Name,
        usuario.Email.Value,
        usuario.Role.ToString(),
        usuario.TenantId,
        tenant?.Name);
}
