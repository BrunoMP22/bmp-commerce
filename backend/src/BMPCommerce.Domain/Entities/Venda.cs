using BMPCommerce.Domain.Common;

namespace BMPCommerce.Domain.Entities;

// Raiz do agregado Venda (Doc 02 §3.6). Toda venda nasce completa pela factory
// Registrar(), que garante as invariantes:
//   INV 1: venda tem ao menos 1 item
//   INV 2: quantidade de cada item > 0
//   INV 3: preço/custo congelados no item no momento da venda
//   INV 4: Total = soma dos subtotais
//   INV 5: estoque insuficiente em qualquer item bloqueia a venda inteira
//   INV 6: venda nunca é deletada fisicamente (soft delete via Cancelar)
public class Venda : BaseEntity
{
    public Guid? ClienteId { get; private set; }

    // Nome congelado para exibição histórica — a venda de balcão não tem cliente.
    public string? ClienteNome { get; private set; }

    public Guid UsuarioId { get; private set; }

    public string UsuarioNome { get; private set; }

    public DateTime DataHora { get; private set; }

    public decimal Total { get; private set; }

    public bool IsDeleted { get; private set; }

    // Concorrência otimista (Doc 01 REGRA 2 / Doc 02 PADRÃO 5).
    public byte[] RowVersion { get; private set; } = [];

    private readonly List<ItemVenda> _itens = [];

    public IReadOnlyCollection<ItemVenda> Itens => _itens.AsReadOnly();

    // Exigido pelo EF Core para materializar a entidade via reflexão.
    private Venda()
    {
        UsuarioNome = null!;
    }

    private Venda(Usuario usuario, Cliente? cliente, DateTime dataHora)
    {
        UsuarioId = usuario.Id;
        UsuarioNome = usuario.Name;
        ClienteId = cliente?.Id;
        ClienteNome = cliente?.Nome;
        DataHora = dataHora;
    }

    // dataHora é opcional para permitir seed/importação de vendas históricas;
    // no fluxo normal a venda é registrada com o horário atual.
    public static Venda Registrar(
        Usuario usuario,
        Cliente? cliente,
        IReadOnlyList<(Produto Produto, int Quantidade)> itens,
        DateTime? dataHora = null)
    {
        if (usuario is null)
        {
            throw new DomainException("Usuário responsável pela venda é obrigatório.");
        }

        if (cliente is not null && !cliente.Ativo)
        {
            throw new DomainException($"Cliente '{cliente.Nome}' está inativo e não pode ser vinculado a uma venda.");
        }

        if (itens is null || itens.Count == 0)
        {
            throw new DomainException("Venda deve ter ao menos um item.");
        }

        var venda = new Venda(usuario, cliente, dataHora ?? DateTime.UtcNow);

        // Valida tudo ANTES de debitar qualquer estoque: estoque insuficiente em
        // qualquer item bloqueia a venda inteira, nada é baixado (INV 5).
        foreach (var (produto, quantidade) in itens)
        {
            if (quantidade <= 0)
            {
                throw new DomainException("Quantidade de cada item deve ser maior que zero.");
            }

            if (!produto.Ativo)
            {
                throw new DomainException($"Produto '{produto.Nome}' está inativo e não pode ser vendido.");
            }

            if (produto.EstoqueAtual < quantidade)
            {
                throw new DomainException(
                    $"Estoque insuficiente para o produto '{produto.Nome}'. Disponível: {produto.EstoqueAtual}, solicitado: {quantidade}.");
            }
        }

        foreach (var (produto, quantidade) in itens)
        {
            produto.BaixarEstoque(quantidade);
            var item = new ItemVenda(venda.Id, produto, quantidade);
            venda._itens.Add(item);
            venda.Total += item.Subtotal;
        }

        return venda;
    }

    // Soft delete (INV 6): a venda permanece no histórico como cancelada.
    // O estorno de estoque dos itens é orquestrado pelo caso de uso, na mesma transação.
    public void Cancelar()
    {
        if (IsDeleted)
        {
            throw new DomainException("Venda já está cancelada.");
        }

        IsDeleted = true;
        MarkAsUpdated();
    }
}
