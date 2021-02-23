from dataclasses import Field
from enum import Enum
from typing import Any, Optional, Type

from dict_to_dataclass.exceptions import DictValueConversionError


class EnumValueNotFoundError(DictValueConversionError):
    """Raised when a dict value is not found in a dataclass field's `Enum` type"""

    pass


def convert_enum(dc_field: Optional[Field], value: Any, enum: Type[Enum]):
    """Default converter for Enum dataclass fields."""
    try:
        return enum[value]
    except KeyError:
        raise EnumValueNotFoundError(dc_field, value)
