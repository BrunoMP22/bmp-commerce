using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Application.Common.Exceptions;
using BMPCommerce.Application.Common.Interfaces;
using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace BMPCommerce.Application.Operations.Vendas;

public class VendaService : IVendaService
{
    private readonly IVendaRepository _vendaRepository;
    private readonly IProdutoRepository _produtoRepository;
    private readonly IClienteRepository _clienteRepository;
    private readonly IApplicationDbContext _dbContext;
    private readonly ICurrentUserService _currentUserService;
    private readonly ILogger<VendaService> _logger;

    public VendaService(
        IVendaRepository vendaRepository,
        IProdutoRepository produtoRepository,
        IClienteRepository clienteRepository,
        IApplicationDbContext dbContext,
        ICurrentUserService currentUserService,
        ILogger<VendaService> logger)
    {
        _vendaRepository = vendaRepository;
        _produtoRepository = produtoRepository;
        _clienteRepository = clienteRepository;
        _dbContext = dbContext;
        _currentUserService = currentUserService;
        _logger = logger;
    }

    public async Task<IReadOnlyList<VendaDto>> ListarAsync(CancellationToken cancellationToken)
    {
        var vendas = await _vendaRepository.GetAllAsync(cancellationToken);
        return vendas.Select(MapToDto).ToList();
    }

    public async Task<VendaDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var venda = await _vendaRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Venda não encontrada.");

        return MapToDto(venda);
    }

    public async Task<VendaDto> RegistrarAsync(RegistrarVendaRequest request, CancellationToken cancellationToken)
    {
        if (request.Itens is null || request.Itens.Count == 0)
        {
            throw new DomainException("Venda deve ter ao menos um item.");
        }

        if (_currentUserService.UserId is not { } usuarioId)
        {
            throw new DomainException("Usuário responsável pela venda não identificado.");
        }

        var usuario = await _dbContext.GetUsuarioByIdAsync(usuarioId, cancellationToken)
            ?? throw new NotFoundException("Usuário não encontrado.");

        Cliente? cliente = null;

        if (request.ClienteId is not null)
        {
            cliente = await _clienteRepository.GetByIdAsync(request.ClienteId.Value, cancellationToken)
                ?? throw new NotFoundException("Cliente não encontrado.");
        }

        // O mesmo produto informado em mais de uma linha é consolidado somando as quantidades.
        var itensConsolidados = request.Itens
            .GroupBy(item => item.ProdutoId)
            .Select(grupo => (ProdutoId: grupo.Key, Quantidade: grupo.Sum(item => item.Quantidade)))
            .ToList();

        var itens = new List<(Produto Produto, int Quantidade)>();

        foreach (var (produtoId, quantidade) in itensConsolidados)
        {
            var produto = await _produtoRepository.GetByIdAsync(produtoId, cancellationToken)
                ?? throw new NotFoundException("Um dos produtos informados não foi encontrado.");

            itens.Add((produto, quantidade));
        }

        // O agregado valida todas as invariantes (estoque, produto ativo, quantidades)
        // e baixa o estoque; o SaveChanges único persiste venda + itens + baixa
        // atomicamente (uma transação), e o RowVersion dos produtos bloqueia
        // vendas simultâneas conflitantes (Doc 01 REGRA 1 e 2).
        var venda = Venda.Registrar(usuario, cliente, itens);

        _vendaRepository.Add(venda);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Venda {VendaId} registrada por {UsuarioId}: {QuantidadeItens} itens, total {Total}.",
            venda.Id,
            usuarioId,
            venda.Itens.Count,
            venda.Total);

        return MapToDto(venda);
    }

    public async Task<VendaDto> CancelarAsync(Guid id, CancellationToken cancellationToken)
    {
        var venda = await _vendaRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Venda não encontrada.");

        venda.Cancelar();

        // Estorno: devolve os itens ao estoque na mesma transação do cancelamento.
        foreach (var item in venda.Itens)
        {
            var produto = await _produtoRepository.GetByIdAsync(item.ProdutoId, cancellationToken);
            produto?.ReporEstoque(item.Quantidade);
        }

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Venda {VendaId} cancelada; estoque dos itens estornado.", venda.Id);

        return MapToDto(venda);
    }

    private static VendaDto MapToDto(Venda venda) => new(
        venda.Id,
        venda.ClienteId,
        venda.ClienteNome,
        venda.UsuarioNome,
        venda.DataHora,
        venda.Total,
        venda.Itens.Sum(item => item.Quantidade),
        venda.IsDeleted,
        venda.Itens
            .Select(item => new ItemVendaDto(
                item.ProdutoId,
                item.ProdutoNome,
                item.ProdutoSku,
                item.Quantidade,
                item.PrecoVendaMomento,
                item.Subtotal))
            .ToList());
}
