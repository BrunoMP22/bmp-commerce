namespace BMPCommerce.Application.Insights.Dashboard;

public interface IDashboardService
{
    Task<DashboardDto> ObterDashboardAsync(CancellationToken cancellationToken);
}
