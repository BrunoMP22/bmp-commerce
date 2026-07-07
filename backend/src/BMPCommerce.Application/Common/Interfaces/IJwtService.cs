using BMPCommerce.Domain.Entities;

namespace BMPCommerce.Application.Common.Interfaces;

public interface IJwtService
{
    string GenerateToken(Usuario usuario);
}
