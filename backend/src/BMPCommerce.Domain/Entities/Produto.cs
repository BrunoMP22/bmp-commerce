using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Enums;

namespace BMPCommerce.Domain.Entities;

public class Produto : BaseEntity
{
    public string Nome { get; private set; }

    public string? Descricao { get; private set; }

    public string Sku { get; private set; }

    public string? CodigoBarras { get; private set; }

    public string? Categoria { get; private set; }

    public UnidadeMedida UnidadeMedida { get; private set; }

    public decimal PrecoCusto { get; private set; }

    public decimal PrecoVenda { get; private set; }

    public int EstoqueAtual { get; private set; }

    public int EstoqueMinimo { get; private set; }

    public bool Ativo { get; private set; }

    // Concorrência otimista (Doc 01 REGRA 2 / Doc 02 PADRÃO 5): o SQL Server preenche
    // e atualiza esta coluna automaticamente; o EF a usa para detectar vendas simultâneas.
    public byte[] RowVersion { get; private set; } = [];

    // Exigido pelo EF Core para materializar a entidade via reflexão; o estado real é
    // preenchido logo em seguida a partir das colunas, nunca fica exposto sem passar por aqui.
    private Produto()
    {
        Nome = null!;
        Sku = null!;
    }

    public Produto(
        string nome,
        string sku,
        string? descricao,
        string? codigoBarras,
        string? categoria,
        UnidadeMedida unidadeMedida,
        decimal precoCusto,
        decimal precoVenda,
        int estoqueAtual,
        int estoqueMinimo)
    {
        Validar(nome, sku, precoCusto, precoVenda, estoqueAtual, estoqueMinimo);

        Nome = nome.Trim();
        Sku = sku.Trim();
        Descricao = descricao?.Trim();
        CodigoBarras = string.IsNullOrWhiteSpace(codigoBarras) ? null : codigoBarras.Trim();
        Categoria = string.IsNullOrWhiteSpace(categoria) ? null : categoria.Trim();
        UnidadeMedida = unidadeMedida;
        PrecoCusto = precoCusto;
        PrecoVenda = precoVenda;
        EstoqueAtual = estoqueAtual;
        EstoqueMinimo = estoqueMinimo;
        Ativo = true;
    }

    public void Atualizar(
        string nome,
        string sku,
        string? descricao,
        string? codigoBarras,
        string? categoria,
        UnidadeMedida unidadeMedida,
        decimal precoCusto,
        decimal precoVenda,
        int estoqueAtual,
        int estoqueMinimo,
        bool ativo)
    {
        Validar(nome, sku, precoCusto, precoVenda, estoqueAtual, estoqueMinimo);

        Nome = nome.Trim();
        Sku = sku.Trim();
        Descricao = descricao?.Trim();
        CodigoBarras = string.IsNullOrWhiteSpace(codigoBarras) ? null : codigoBarras.Trim();
        Categoria = string.IsNullOrWhiteSpace(categoria) ? null : categoria.Trim();
        UnidadeMedida = unidadeMedida;
        PrecoCusto = precoCusto;
        PrecoVenda = precoVenda;
        EstoqueAtual = estoqueAtual;
        EstoqueMinimo = estoqueMinimo;
        Ativo = ativo;
        MarkAsUpdated();
    }

    // Baixa de estoque da venda (Doc 01 REGRA 1): nunca deixa o estoque negativo —
    // estoque insuficiente bloqueia a venda inteira, nada é debitado.
    public void BaixarEstoque(int quantidade)
    {
        if (quantidade <= 0)
        {
            throw new DomainException("Quantidade deve ser maior que zero.");
        }

        if (EstoqueAtual < quantidade)
        {
            throw new DomainException(
                $"Estoque insuficiente para o produto '{Nome}'. Disponível: {EstoqueAtual}, solicitado: {quantidade}.");
        }

        EstoqueAtual -= quantidade;
        MarkAsUpdated();
    }

    // Estorno usado no cancelamento de venda: devolve os itens ao estoque.
    public void ReporEstoque(int quantidade)
    {
        if (quantidade <= 0)
        {
            throw new DomainException("Quantidade deve ser maior que zero.");
        }

        EstoqueAtual += quantidade;
        MarkAsUpdated();
    }

    private static void Validar(string nome, string sku, decimal precoCusto, decimal precoVenda, int estoqueAtual, int estoqueMinimo)
    {
        if (string.IsNullOrWhiteSpace(nome))
        {
            throw new DomainException("Nome do produto é obrigatório.");
        }

        if (string.IsNullOrWhiteSpace(sku))
        {
            throw new DomainException("SKU do produto é obrigatório.");
        }

        if (precoVenda <= 0)
        {
            throw new DomainException("Preço de venda deve ser maior que zero.");
        }

        if (precoCusto < 0)
        {
            throw new DomainException("Preço de custo não pode ser negativo.");
        }

        if (estoqueAtual < 0)
        {
            throw new DomainException("Estoque atual não pode ser negativo.");
        }

        if (estoqueMinimo < 0)
        {
            throw new DomainException("Estoque mínimo não pode ser negativo.");
        }
    }
}
