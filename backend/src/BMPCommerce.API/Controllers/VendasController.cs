using BMPCommerce.Application.Operations.Vendas;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BMPCommerce.API.Controllers;

[ApiController]
[Authorize]
[Route("api/vendas")]
public class VendasController : ControllerBase
{
    private readonly IVendaService _vendaService;

    public VendasController(IVendaService vendaService)
    {
        _vendaService = vendaService;
    }

    [HttpGet]
    public async Task<IActionResult> Listar(CancellationToken cancellationToken)
    {
        var vendas = await _vendaService.ListarAsync(cancellationToken);
        return Ok(vendas);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> ObterPorId(Guid id, CancellationToken cancellationToken)
    {
        var venda = await _vendaService.ObterPorIdAsync(id, cancellationToken);
        return Ok(venda);
    }

    [HttpPost]
    public async Task<IActionResult> Registrar([FromBody] RegistrarVendaRequest request, CancellationToken cancellationToken)
    {
        var venda = await _vendaService.RegistrarAsync(request, cancellationToken);
        return CreatedAtAction(nameof(ObterPorId), new { id = venda.Id }, venda);
    }

    // Cancelamento é soft delete (Doc 01 REGRA 4) com estorno de estoque —
    // a venda permanece no histórico como cancelada.
    [HttpPost("{id:guid}/cancelar")]
    public async Task<IActionResult> Cancelar(Guid id, CancellationToken cancellationToken)
    {
        var venda = await _vendaService.CancelarAsync(id, cancellationToken);
        return Ok(venda);
    }
}
