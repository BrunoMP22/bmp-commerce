"""Exceções centrais — equivalentes a Domain/Common/DomainException.cs e
Application/Common/Exceptions/NotFoundException.cs do backend original.

Convenção preservada (ver backend/README.md do projeto):
- DomainException  -> violação de regra de negócio  -> HTTP 400
- NotFoundException -> recurso inexistente            -> HTTP 404
"""


class DomainException(Exception):
    """Violação de uma invariante de domínio (ex: preço negativo, estoque insuficiente)."""


class NotFoundException(Exception):
    """Recurso solicitado não existe."""
