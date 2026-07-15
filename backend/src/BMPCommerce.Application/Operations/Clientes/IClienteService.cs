using BMPCommerce.Domain.Common;

namespace BMPCommerce.Application.Operations.Clientes;

public interface IClienteService
{
    Task<IReadOnlyList<ClienteDto>> ListarAsync(CancellationToken cancellationToken);

    Task<ClienteDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken);

    Task<ClienteDto> CriarAsync(CriarClienteRequest request, CancellationToken cancellationToken);

    Task<ClienteDto> AtualizarAsync(Guid id, AtualizarClienteRequest request, CancellationToken cancellationToken);

    Task<Result> ExcluirAsync(Guid id, CancellationToken cancellationToken);
}
