using BMPCommerce.Domain.Common;

namespace BMPCommerce.Domain.Entities;

public class Tenant : BaseEntity
{
    public string Name { get; private set; }

    public string Plan { get; private set; }

    public bool IsActive { get; private set; }

    // Exigido pelo EF Core para materializar a entidade via reflexão; o estado real é
    // preenchido logo em seguida a partir das colunas, nunca fica exposto sem passar por aqui.
    private Tenant()
    {
        Name = null!;
        Plan = null!;
    }

    public Tenant(string name, string plan)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new DomainException("Nome do tenant é obrigatório.");
        }

        if (string.IsNullOrWhiteSpace(plan))
        {
            throw new DomainException("Plan do tenant é obrigatório.");
        }

        Name = name.Trim();
        Plan = plan.Trim();
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
}
