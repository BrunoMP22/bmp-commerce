using BMPCommerce.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BMPCommerce.Infrastructure.Persistence.Configurations;

public class VendaConfiguration : IEntityTypeConfiguration<Venda>
{
    public void Configure(EntityTypeBuilder<Venda> builder)
    {
        builder.ToTable("Vendas");

        builder.HasKey(v => v.Id);

        builder.Property(v => v.ClienteNome)
            .HasMaxLength(200);

        builder.Property(v => v.UsuarioNome)
            .IsRequired()
            .HasMaxLength(200);

        builder.Property(v => v.DataHora)
            .IsRequired();

        builder.HasIndex(v => v.DataHora);

        builder.Property(v => v.Total)
            .IsRequired()
            .HasColumnType("decimal(18,2)");

        builder.Property(v => v.IsDeleted)
            .IsRequired();

        builder.Property(v => v.RowVersion)
            .IsRowVersion();

        builder.Property(v => v.CreatedAt)
            .IsRequired();

        // Cliente é opcional (venda de balcão) e não pode ser excluído com vendas —
        // o guard fica no ClienteService; o Restrict é a defesa em profundidade no banco.
        builder.HasOne<Cliente>()
            .WithMany()
            .HasForeignKey(v => v.ClienteId)
            .OnDelete(DeleteBehavior.Restrict)
            .IsRequired(false);

        builder.HasOne<Usuario>()
            .WithMany()
            .HasForeignKey(v => v.UsuarioId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(v => v.Itens)
            .WithOne()
            .HasForeignKey(i => i.VendaId)
            .OnDelete(DeleteBehavior.Cascade);

        // Itens só entram/saem pelo agregado — EF materializa direto no campo _itens.
        builder.Navigation(v => v.Itens)
            .UsePropertyAccessMode(PropertyAccessMode.Field);
    }
}
