namespace BMPCommerce.Application.Operations.Vendas;

public interface IVendaService
{
    Task<IReadOnlyList<VendaDto>> ListarAsync(CancellationToken cancellationToken);

    Task<VendaDto> ObterPorIdAsync(Guid id, CancellationToken cancellationToken);

    Task<VendaDto> RegistrarAsync(RegistrarVendaRequest request, CancellationToken cancellationToken);

    Task<VendaDto> CancelarAsync(Guid id, CancellationToken cancellationToken);
}
