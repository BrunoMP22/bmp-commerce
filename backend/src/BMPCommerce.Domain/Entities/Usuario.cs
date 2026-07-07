using BMPCommerce.Domain.Common;
using BMPCommerce.Domain.Enums;
using BMPCommerce.Domain.ValueObjects;

namespace BMPCommerce.Domain.Entities;

public class Usuario : BaseEntity
{
    public string Name { get; private set; }

    public Email Email { get; private set; }

    public string PasswordHash { get; private set; }

    public UserRole Role { get; private set; }

    public bool IsActive { get; private set; }

    public Guid? TenantId { get; private set; }

    // Exigido pelo EF Core para materializar a entidade via reflexão; o estado real é
    // preenchido logo em seguida a partir das colunas, nunca fica exposto sem passar por aqui.
    private Usuario()
    {
        Name = null!;
        Email = null!;
        PasswordHash = null!;
    }

    public Usuario(string name, Email email, string passwordHash, UserRole role, Guid? tenantId)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new DomainException("Nome do usuário é obrigatório.");
        }

        if (email is null)
        {
            throw new DomainException("Email é obrigatório.");
        }

        if (string.IsNullOrWhiteSpace(passwordHash))
        {
            throw new DomainException("PasswordHash é obrigatório.");
        }

        if (role == UserRole.SuperAdmin && tenantId is not null)
        {
            throw new DomainException("Usuário SuperAdmin não pode estar vinculado a um tenant.");
        }

        if (role != UserRole.SuperAdmin && tenantId is null)
        {
            throw new DomainException("Usuário Admin/Employee precisa estar vinculado a um tenant.");
        }

        Name = name.Trim();
        Email = email;
        PasswordHash = passwordHash;
        Role = role;
        TenantId = tenantId;
        IsActive = true;
    }

    public void Activate()
    {
        IsActive = true;
        MarkAsUpdated();
    }

    public void Deactivate()
    {
        IsActive = false;
        MarkAsUpdated();
    }

    public void ChangePassword(string newPasswordHash)
    {
        if (string.IsNullOrWhiteSpace(newPasswordHash))
        {
            throw new DomainException("PasswordHash é obrigatório.");
        }

        PasswordHash = newPasswordHash;
        MarkAsUpdated();
    }
}
