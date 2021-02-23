from dataclasses import Field
from enum import Enum
from typing import Any, Optional, Type

from dict_to_dataclass.exceptions import DictValueConversionError


def convert_enum(dc_field: Optional[Field], value: Any, enum: Type[Enum]):
    """Default converter for Enum dataclass fields."""
    try:
        return enum[value]
    except KeyError:
        raise DictValueConversionError(dc_field, value)
