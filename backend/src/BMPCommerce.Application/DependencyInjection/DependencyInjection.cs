using BMPCommerce.Application.Insights.Dashboard;
using BMPCommerce.Application.Operations.Clientes;
using BMPCommerce.Application.Operations.Produtos;
using BMPCommerce.Application.Operations.Usuarios;
using BMPCommerce.Application.Operations.Vendas;
using Microsoft.Extensions.DependencyInjection;

namespace BMPCommerce.Application.DependencyInjection;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IAuthService, AuthService>();
        services.AddScoped<IProdutoService, ProdutoService>();
        services.AddScoped<IClienteService, ClienteService>();
        services.AddScoped<IVendaService, VendaService>();
        services.AddScoped<IDashboardService, DashboardService>();

        return services;
    }
}
