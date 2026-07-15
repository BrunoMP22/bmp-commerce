using BMPCommerce.Domain.Interfaces;

namespace BMPCommerce.Application.Insights.Dashboard;

// Contexto Insights (ADR 0004): LÊ dos dados de Operations, nunca escreve.
// Nesta fase é uma agregação simples on-read; o Motor de Regras (insight cards
// com tipo/severidade/mensagem) pluga aqui na sprint de Insights sem quebrar
// este contrato.
public class DashboardService : IDashboardService
{
    private const int DiasDoGrafico = 14;

    private readonly IVendaRepository _vendaRepository;
    private readonly IProdutoRepository _produtoRepository;
    private readonly IClienteRepository _clienteRepository;

    public DashboardService(
        IVendaRepository vendaRepository,
        IProdutoRepository produtoRepository,
        IClienteRepository clienteRepository)
    {
        _vendaRepository = vendaRepository;
        _produtoRepository = produtoRepository;
        _clienteRepository = clienteRepository;
    }

    public async Task<DashboardDto> ObterDashboardAsync(CancellationToken cancellationToken)
    {
        // Cálculo on-read em memória: volume por tenant é baixo no MVP (ADR 0004);
        // a troca por queries agregadas/pré-cálculo acontece atrás deste mesmo contrato.
        var vendas = await _vendaRepository.GetAllAsync(cancellationToken);
        var produtos = await _produtoRepository.GetAllAsync(search: null, cancellationToken);
        var clientes = await _clienteRepository.GetAllAsync(cancellationToken);

        var vendasValidas = vendas.Where(venda => !venda.IsDeleted).ToList();

        var receitaTotal = vendasValidas.Sum(venda => venda.Total);
        var quantidadeVendas = vendasValidas.Count;
        var ticketMedio = quantidadeVendas > 0 ? Math.Round(receitaTotal / quantidadeVendas, 2) : 0m;
        var valorEstoque = produtos.Sum(produto => produto.PrecoCusto * produto.EstoqueAtual);

        var hoje = DateTime.UtcNow.Date;
        var inicioJanela = hoje.AddDays(-(DiasDoGrafico - 1));

        var vendasPorDia = Enumerable.Range(0, DiasDoGrafico)
            .Select(offset =>
            {
                var dia = inicioJanela.AddDays(offset);
                var vendasDoDia = vendasValidas.Where(venda => venda.DataHora.Date == dia).ToList();
                return new VendaPorDiaDto(dia, vendasDoDia.Sum(venda => venda.Total), vendasDoDia.Count);
            })
            .ToList();

        return new DashboardDto(
            receitaTotal,
            quantidadeVendas,
            clientes.Count,
            produtos.Count,
            produtos.Count(produto => produto.EstoqueAtual > 0 && produto.EstoqueAtual < produto.EstoqueMinimo),
            produtos.Count(produto => produto.EstoqueAtual == 0),
            ticketMedio,
            valorEstoque,
            vendasPorDia);
    }
}
