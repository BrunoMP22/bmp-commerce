using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Enums;
using BMPCommerce.Domain.ValueObjects;
using BMPCommerce.Infrastructure.Persistence.DbContext;
using Microsoft.EntityFrameworkCore;

namespace BMPCommerce.Infrastructure.Persistence.Seed;

public static class DbSeeder
{
    private const string AdminEmail = "admin@bmpcommerce.com";
    private const string AdminPassword = "Admin@123";

    public static async Task SeedAsync(BMPCommerceDbContext dbContext, IPasswordHasher passwordHasher)
    {
        if (!await dbContext.Tenants.AnyAsync(t => t.Name == "BMP Demo"))
        {
            dbContext.Tenants.Add(new Tenant("BMP Demo", "Standard"));
        }

        var adminEmail = Email.Create(AdminEmail);

        if (!await dbContext.Usuarios.AnyAsync(u => u.Email == adminEmail))
        {
            var passwordHash = passwordHasher.Hash(AdminPassword);
            var admin = new Usuario("Administrador", adminEmail, passwordHash, UserRole.SuperAdmin, tenantId: null);
            dbContext.Usuarios.Add(admin);
        }

        await dbContext.SaveChangesAsync(CancellationToken.None);
    }
}
