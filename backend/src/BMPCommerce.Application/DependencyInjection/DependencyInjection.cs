using BMPCommerce.Application.Operations.Produtos;
using BMPCommerce.Application.Operations.Usuarios;
using Microsoft.Extensions.DependencyInjection;

namespace BMPCommerce.Application.DependencyInjection;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IAuthService, AuthService>();
        services.AddScoped<IProdutoService, ProdutoService>();

        return services;
    }
}
