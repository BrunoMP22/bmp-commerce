using BMPCommerce.Domain.Enums;

namespace BMPCommerce.Application.Common.Interfaces;

public interface ICurrentUserService
{
    Guid? UserId { get; }

    UserRole? Role { get; }
}
