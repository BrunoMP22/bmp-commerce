"""Equivalente a Domain/Enums/UserRole.cs e Domain/Enums/UnidadeMedida.cs.

StrEnum com os mesmos valores literais (PascalCase) que o C# produzia via `.ToString()`,
para que o JSON da API continue idêntico ao que o frontend já espera
(ex: role "SuperAdmin", unidadeMedida "Unidade").
"""

from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "SuperAdmin"
    ADMIN = "Admin"
    EMPLOYEE = "Employee"


class UnidadeMedida(StrEnum):
    UNIDADE = "Unidade"
    CAIXA = "Caixa"
    PACOTE = "Pacote"
    KG = "Kg"
    LITRO = "Litro"
    METRO = "Metro"
