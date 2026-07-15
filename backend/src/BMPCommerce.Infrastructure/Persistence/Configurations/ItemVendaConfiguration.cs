using BMPCommerce.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BMPCommerce.Infrastructure.Persistence.Configurations;

public class ItemVendaConfiguration : IEntityTypeConfiguration<ItemVenda>
{
    public void Configure(EntityTypeBuilder<ItemVenda> builder)
    {
        builder.ToTable("ItensVenda");

        builder.HasKey(i => i.Id);

        builder.Property(i => i.ProdutoNome)
            .IsRequired()
            .HasMaxLength(200);

        builder.Property(i => i.ProdutoSku)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(i => i.Quantidade)
            .IsRequired();

        builder.Property(i => i.PrecoVendaMomento)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        builder.Property(i => i.PrecoCustoMomento)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        builder.Property(i => i.Subtotal)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        // Referência histórica (Doc 02 §4): o produto não pode ser apagado se tem vendas —
        // guard no ProdutoService; Restrict é a defesa em profundidade no banco.
        builder.HasOne<Produto>()
            .WithMany()
            .HasForeignKey(i => i.ProdutoId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
