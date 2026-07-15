using BMPCommerce.Application.Insights.Dashboard;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BMPCommerce.API.Controllers;

[ApiController]
[Authorize]
[Route("api/dashboard")]
public class DashboardController : ControllerBase
{
    private readonly IDashboardService _dashboardService;

    public DashboardController(IDashboardService dashboardService)
    {
        _dashboardService = dashboardService;
    }

    [HttpGet]
    public async Task<IActionResult> Obter(CancellationToken cancellationToken)
    {
        var dashboard = await _dashboardService.ObterDashboardAsync(cancellationToken);
        return Ok(dashboard);
    }
}
