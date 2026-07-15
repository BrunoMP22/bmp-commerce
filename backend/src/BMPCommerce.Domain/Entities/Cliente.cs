using System.Diagnostics.CodeAnalysis;
using System.Text.RegularExpressions;
using BMPCommerce.Domain.Common;

namespace BMPCommerce.Domain.Entities;

// Cliente é "CRUD honesto" (Doc 01 §6): sem value objects nem agregado —
// validações simples direto na entidade.
public class Cliente : BaseEntity
{
    private static readonly Regex EmailPattern = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    public string Nome { get; private set; }

    public string? CpfCnpj { get; private set; }

    public string? Telefone { get; private set; }

    public string? Email { get; private set; }

    public string? Cidade { get; private set; }

    public string? Estado { get; private set; }

    public string? Observacoes { get; private set; }

    public bool Ativo { get; private set; }

    // Exigido pelo EF Core para materializar a entidade via reflexão.
    private Cliente()
    {
        Nome = null!;
    }

    public Cliente(
        string nome,
        string? cpfCnpj,
        string? telefone,
        string? email,
        string? cidade,
        string? estado,
        string? observacoes)
    {
        Preencher(nome, cpfCnpj, telefone, email, cidade, estado, observacoes);
        Ativo = true;
    }

    public void Atualizar(
        string nome,
        string? cpfCnpj,
        string? telefone,
        string? email,
        string? cidade,
        string? estado,
        string? observacoes,
        bool ativo)
    {
        Preencher(nome, cpfCnpj, telefone, email, cidade, estado, observacoes);
        Ativo = ativo;
        MarkAsUpdated();
    }

    [MemberNotNull(nameof(Nome))]
    private void Preencher(
        string nome,
        string? cpfCnpj,
        string? telefone,
        string? email,
        string? cidade,
        string? estado,
        string? observacoes)
    {
        if (string.IsNullOrWhiteSpace(nome))
        {
            throw new DomainException("Nome do cliente é obrigatório.");
        }

        Nome = nome.Trim();
        CpfCnpj = NormalizarCpfCnpj(cpfCnpj);
        Telefone = string.IsNullOrWhiteSpace(telefone) ? null : telefone.Trim();
        Email = NormalizarEmail(email);
        Cidade = string.IsNullOrWhiteSpace(cidade) ? null : cidade.Trim();
        Estado = NormalizarEstado(estado);
        Observacoes = string.IsNullOrWhiteSpace(observacoes) ? null : observacoes.Trim();
    }

    private static string? NormalizarCpfCnpj(string? valor)
    {
        if (string.IsNullOrWhiteSpace(valor))
        {
            return null;
        }

        var digitos = new string(valor.Where(char.IsDigit).ToArray());

        if (digitos.Length is not (11 or 14))
        {
            throw new DomainException("CPF/CNPJ inválido: informe 11 dígitos (CPF) ou 14 dígitos (CNPJ).");
        }

        return digitos;
    }

    private static string? NormalizarEmail(string? email)
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            return null;
        }

        var normalizado = email.Trim().ToLowerInvariant();

        if (!EmailPattern.IsMatch(normalizado))
        {
            throw new DomainException($"Email '{email}' possui formato inválido.");
        }

        return normalizado;
    }

    private static string? NormalizarEstado(string? estado)
    {
        if (string.IsNullOrWhiteSpace(estado))
        {
            return null;
        }

        var normalizado = estado.Trim().ToUpperInvariant();

        if (normalizado.Length != 2)
        {
            throw new DomainException("Estado deve ser a sigla UF com 2 letras (ex: SP).");
        }

        return normalizado;
    }
}
