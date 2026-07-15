using BMPCommerce.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BMPCommerce.Infrastructure.Persistence.Configurations;

public class ClienteConfiguration : IEntityTypeConfiguration<Cliente>
{
    public void Configure(EntityTypeBuilder<Cliente> builder)
    {
        builder.ToTable("Clientes");

        builder.HasKey(c => c.Id);

        builder.Property(c => c.Nome)
            .IsRequired()
            .HasMaxLength(200);

        builder.Property(c => c.CpfCnpj)
            .HasMaxLength(14);

        builder.Property(c => c.Telefone)
            .HasMaxLength(30);

        builder.Property(c => c.Email)
            .HasMaxLength(256);

        builder.Property(c => c.Cidade)
            .HasMaxLength(100);

        builder.Property(c => c.Estado)
            .HasMaxLength(2);

        builder.Property(c => c.Observacoes)
            .HasMaxLength(1000);

        builder.Property(c => c.Ativo)
            .IsRequired();

        builder.Property(c => c.CreatedAt)
            .IsRequired();
    }
}
