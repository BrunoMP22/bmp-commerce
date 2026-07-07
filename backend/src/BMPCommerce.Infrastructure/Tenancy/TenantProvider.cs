using BMPCommerce.Application.Common.Interfaces;
using Microsoft.AspNetCore.Http;

namespace BMPCommerce.Infrastructure.Tenancy;

public class TenantProvider : ITenantProvider
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public TenantProvider(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public Guid? TenantId
    {
        get
        {
            var value = _httpContextAccessor.HttpContext?.User.FindFirst(TenancyClaimTypes.TenantId)?.Value;
            return Guid.TryParse(value, out var tenantId) ? tenantId : null;
        }
    }
}
