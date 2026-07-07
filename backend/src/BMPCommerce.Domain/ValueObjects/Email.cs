using System.Text.RegularExpressions;
using BMPCommerce.Domain.Common;

namespace BMPCommerce.Domain.ValueObjects;

public sealed record Email
{
    private static readonly Regex Pattern = new(
        @"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        RegexOptions.Compiled);

    public string Value { get; }

    private Email(string value)
    {
        Value = value;
    }

    public static Email Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new DomainException("Email não pode ser vazio.");
        }

        var normalized = value.Trim().ToLowerInvariant();

        if (!Pattern.IsMatch(normalized))
        {
            throw new DomainException($"Email '{value}' possui formato inválido.");
        }

        return new Email(normalized);
    }

    public override string ToString() => Value;
}
