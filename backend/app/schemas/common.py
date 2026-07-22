"""Base para todos os schemas Pydantic da API.

O frontend React foi escrito contra o JSON que o System.Text.Json do ASP.NET Core
produzia (camelCase por padrão). `alias_generator=to_camel` replica isso: os campos em
Python continuam snake_case (idiomático), mas o corpo HTTP de entrada/saída usa
camelCase — o contrato com o frontend não muda uma vírgula.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
