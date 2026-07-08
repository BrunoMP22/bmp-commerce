namespace BMPCommerce.Application.Operations.Usuarios;

public record LoginRequest(string Email, string Password);

public record AuthenticatedUserResult(
    Guid UserId,
    string Name,
    string Email,
    string Role,
    Guid? TenantId,
    string? TenantName);

public record LoginResult(string Token, AuthenticatedUserResult User);
