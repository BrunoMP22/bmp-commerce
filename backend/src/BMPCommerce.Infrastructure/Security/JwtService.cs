using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Infrastructure.Tenancy;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;

namespace BMPCommerce.Infrastructure.Security;

public class JwtService : IJwtService
{
    private readonly JwtSettings _settings;

    public JwtService(IOptions<JwtSettings> options)
    {
        _settings = options.Value;
    }

    public string GenerateToken(Usuario usuario)
    {
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, usuario.Id.ToString()),
            new(ClaimTypes.NameIdentifier, usuario.Id.ToString()),
            new(ClaimTypes.Name, usuario.Name),
            new(ClaimTypes.Email, usuario.Email.Value),
            new(ClaimTypes.Role, usuario.Role.ToString()),
        };

        if (usuario.TenantId is not null)
        {
            claims.Add(new Claim(TenancyClaimTypes.TenantId, usuario.TenantId.Value.ToString()));
        }

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_settings.Key));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _settings.Issuer,
            audience: _settings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_settings.ExpiryMinutes),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
