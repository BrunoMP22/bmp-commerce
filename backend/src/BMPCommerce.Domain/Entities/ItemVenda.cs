using BMPCommerce.Domain.Common;

namespace BMPCommerce.Domain.Entities;

// Parte do agregado Venda — só é criado por dentro dele (construtor internal).
// Preço, custo, nome e SKU são CONGELADOS no momento da venda (Doc 01 REGRA 3):
// se o produto mudar depois, o histórico e a margem desta venda não mudam.
public class ItemVenda : BaseEntity
{
    public Guid VendaId { get; private set; }

    public Guid ProdutoId { get; private set; }

    public string ProdutoNome { get; private set; }

    public string ProdutoSku { get; private set; }

    public int Quantidade { get; private set; }

    public decimal PrecoVendaMomento { get; private set; }

    public decimal PrecoCustoMomento { get; private set; }

    public decimal Subtotal { get; private set; }

    // Exigido pelo EF Core para materializar a entidade via reflexão.
    private ItemVenda()
    {
        ProdutoNome = null!;
        ProdutoSku = null!;
    }

    internal ItemVenda(Guid vendaId, Produto produto, int quantidade)
    {
        if (quantidade <= 0)
        {
            throw new DomainException("Quantidade de cada item deve ser maior que zero.");
        }

        VendaId = vendaId;
        ProdutoId = produto.Id;
        ProdutoNome = produto.Nome;
        ProdutoSku = produto.Sku;
        Quantidade = quantidade;
        PrecoVendaMomento = produto.PrecoVenda;
        PrecoCustoMomento = produto.PrecoCusto;
        Subtotal = quantidade * produto.PrecoVenda;
    }
}
