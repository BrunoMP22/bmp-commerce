using BMPCommerce.Application.Common.Abstractions;
using BMPCommerce.Application.Common.Exceptions;
using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Entities;
using BMPCommerce.Domain.Interfaces;

namespace BMPCommerce.Application.Operations.Clientes;

public class ClienteService : IClienteService
{
    private readonly IClienteRepository _clienteRepository;
    private readonly IVendaRepository _vendaRepository;
    private readonly IApplicationDbContext _dbContext;

    public ClienteService(
        IClienteRepository clienteRepository,
        IVendaRepository vendaRepository,
        IApplicationDbContext dbContext)
    {
        _clienteRepository = clienteRepository;
        _vendaRepository = vendaRepository;
        _dbContext = dbContext;
    }

    public async Task<IReadOnlyList<ClienteDto>> ListarAsync(CancellationToken cancellationToken)
    {
        var clientes = await _clienteRepository.GetAllAsync(cancellationToken);
        return clientes.Select(MapToDto).ToList();
    }

    public async Task<ClienteDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var cliente = await _clienteRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Cliente não encontrado.");

        return MapToDto(cliente);
    }

    public async Task<ClienteDto> CriarAsync(CriarClienteRequest request, CancellationToken cancellationToken)
    {
        var cliente = new Cliente(
            request.Nome,
            request.CpfCnpj,
            request.Telefone,
            request.Email,
            request.Cidade,
            request.Estado,
            request.Observacoes);

        _clienteRepository.Add(cliente);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(cliente);
    }

    public async Task<ClienteDto> AtualizarAsync(Guid id, AtualizarClienteRequest request, CancellationToken cancellationToken)
    {
        var cliente = await _clienteRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Cliente não encontrado.");

        cliente.Atualizar(
            request.Nome,
            request.CpfCnpj,
            request.Telefone,
            request.Email,
            request.Cidade,
            request.Estado,
            request.Observacoes,
            request.Ativo);

        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(cliente);
    }

    public async Task<Result> ExcluirAsync(Guid id, CancellationToken cancellationToken)
    {
        var cliente = await _clienteRepository.GetByIdAsync(id, cancellationToken)
            ?? throw new NotFoundException("Cliente não encontrado.");

        if (await _vendaRepository.ExisteVendaComClienteAsync(id, cancellationToken))
        {
            return Result.Failure("Cliente possui vendas registradas e não pode ser excluído. Inative-o em vez de excluir.");
        }

        _clienteRepository.Remove(cliente);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }

    private static ClienteDto MapToDto(Cliente cliente) => new(
        cliente.Id,
        cliente.Nome,
        cliente.CpfCnpj,
        cliente.Telefone,
        cliente.Email,
        cliente.Cidade,
        cliente.Estado,
        cliente.Observacoes,
        cliente.Ativo,
        cliente.CreatedAt,
        cliente.UpdatedAt);
}
