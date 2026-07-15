namespace BMPCommerce.Application.Operations.Clientes;

public record ClienteDto(
    Guid Id,
    string Nome,
    string? CpfCnpj,
    string? Telefone,
    string? Email,
    string? Cidade,
    string? Estado,
    string? Observacoes,
    bool Ativo,
    DateTime CreatedAt,
    DateTime? UpdatedAt);

public record CriarClienteRequest(
    string Nome,
    string? CpfCnpj,
    string? Telefone,
    string? Email,
    string? Cidade,
    string? Estado,
    string? Observacoes);

public record AtualizarClienteRequest(
    string Nome,
    string? CpfCnpj,
    string? Telefone,
    string? Email,
    string? Cidade,
    string? Estado,
    string? Observacoes,
    bool Ativo);
