from dataclasses import Field
from enum import Enum
from typing import Any, Optional, Type

from ..exceptions import EnumValueNotFoundError


def convert_enum(dc_field: Optional[Field], value: Any, enum: Type[Enum]):
    """Default converter for Enum dataclass fields."""
    try:
        return enum[value]
    except KeyError:
        raise EnumValueNotFoundError(dataclass_field=dc_field, value_from_dict=value)
