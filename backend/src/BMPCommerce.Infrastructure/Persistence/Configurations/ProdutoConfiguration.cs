using BMPCommerce.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BMPCommerce.Infrastructure.Persistence.Configurations;

public class ProdutoConfiguration : IEntityTypeConfiguration<Produto>
{
    public void Configure(EntityTypeBuilder<Produto> builder)
    {
        builder.ToTable("Produtos");

        builder.HasKey(p => p.Id);

        builder.Property(p => p.Nome)
            .IsRequired()
            .HasMaxLength(200);

        builder.Property(p => p.Descricao)
            .HasMaxLength(1000);

        builder.Property(p => p.Sku)
            .IsRequired()
            .HasMaxLength(50);

        builder.HasIndex(p => p.Sku)
            .IsUnique();

        builder.Property(p => p.CodigoBarras)
            .HasMaxLength(50);

        builder.Property(p => p.Categoria)
            .HasMaxLength(100);

        builder.Property(p => p.UnidadeMedida)
            .IsRequired()
            .HasConversion<string>()
            .HasMaxLength(20);

        builder.Property(p => p.PrecoCusto)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        builder.Property(p => p.PrecoVenda)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        builder.Property(p => p.EstoqueAtual)
            .IsRequired();

        builder.Property(p => p.EstoqueMinimo)
            .IsRequired();

        builder.Property(p => p.Ativo)
            .IsRequired();

        builder.Property(p => p.CreatedAt)
            .IsRequired();
    }
}
