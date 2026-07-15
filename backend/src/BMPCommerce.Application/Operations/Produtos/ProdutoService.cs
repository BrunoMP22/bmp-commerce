using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Application.Common.Exceptions;
using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Enums;
using BMPCommerce.Domain.Interfaces;

namespace BMPCommerce.Application.Operations.Produtos;

public class ProdutoService : IProdutoService
{
    private readonly IProdutoRepository _produtoRepository;
    private readonly IVendaRepository _vendaRepository;
    private readonly IApplicationDbContext _dbContext;

    public ProdutoService(
        IProdutoRepository produtoRepository,
        IVendaRepository vendaRepository,
        IApplicationDbContext dbContext)
    {
        _produtoRepository = produtoRepository;
        _vendaRepository = vendaRepository;
        _dbContext = dbContext;
    }

    public async Task<IReadOnlyList<ProdutoDto>> ListarAsync(string? search, CancellationToken cancellationToken)
    {
        var produtos = await _produtoRepository.GetAllAsync(search, cancellationToken);
        return produtos.Select(MapToDto).ToList();
    }

    public async Task<ProdutoDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var produto = await _produtoRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Produto não encontrado.");

        return MapToDto(produto);
    }

    public async Task<Result<ProdutoDto>> CriarAsync(CriarProdutoRequest request, CancellationToken cancellationToken)
    {
        if (await _produtoRepository.ExisteSkuAsync(request.Sku, ignorarId: null, cancellationToken))
        {
            return Result<ProdutoDto>.Failure("Já existe um produto com esse SKU.");
        }

        if (!Enum.TryParse<UnidadeMedida>(request.UnidadeMedida, out var unidadeMedida))
        {
            return Result<ProdutoDto>.Failure("Unidade de medida inválida.");
        }

        var produto = new Produto(
            request.Nome,
            request.Sku,
            request.Descricao,
            request.CodigoBarras,
            request.Categoria,
            unidadeMedida,
            request.PrecoCusto,
            request.PrecoVenda,
            request.EstoqueAtual,
            request.EstoqueMinimo);

        _produtoRepository.Add(produto);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result<ProdutoDto>.Success(MapToDto(produto));
    }

    public async Task<Result<ProdutoDto>> AtualizarAsync(Guid id, AtualizarProdutoRequest request, CancellationToken cancellationToken)
    {
        var produto = await _produtoRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Produto não encontrado.");

        if (await _produtoRepository.ExisteSkuAsync(request.Sku, id, cancellationToken))
        {
            return Result<ProdutoDto>.Failure("Já existe um produto com esse SKU.");
        }

        if (!Enum.TryParse<UnidadeMedida>(request.UnidadeMedida, out var unidadeMedida))
        {
            return Result<ProdutoDto>.Failure("Unidade de medida inválida.");
        }

        produto.Atualizar(
            request.Nome,
            request.Sku,
            request.Descricao,
            request.CodigoBarras,
            request.Categoria,
            unidadeMedida,
            request.PrecoCusto,
            request.PrecoVenda,
            request.EstoqueAtual,
            request.EstoqueMinimo,
            request.Ativo);

        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result<ProdutoDto>.Success(MapToDto(produto));
    }

    public async Task<Result> ExcluirAsync(Guid id, CancellationToken cancellationToken)
    {
        var produto = await _produtoRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Produto não encontrado.");

        // Preserva o histórico de vendas (Doc 01 REGRA 4): produto vendido não sai do banco.
        if (await _vendaRepository.ExisteVendaComProdutoAsync(id, cancellationToken))
        {
            return Result.Failure("Produto possui vendas registradas e não pode ser excluído. Inative-o em vez de excluir.");
        }

        _produtoRepository.Remove(produto);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }

    private static ProdutoDto MapToDto(Produto produto) => new(
        produto.Id,
        produto.Nome,
        produto.Descricao,
        produto.Sku,
        produto.CodigoBarras,
        produto.Categoria,
        produto.UnidadeMedida.ToString(),
        produto.PrecoCusto,
        produto.PrecoVenda,
        produto.EstoqueAtual,
        produto.EstoqueMinimo,
        produto.Ativo,
        produto.CreatedAt,
        produto.UpdatedAt);
}
