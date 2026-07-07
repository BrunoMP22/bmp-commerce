namespace BMPCommerce.Application.Common.Interfaces;

public interface ITenantProvider
{
    Guid? TenantId { get; }
}
