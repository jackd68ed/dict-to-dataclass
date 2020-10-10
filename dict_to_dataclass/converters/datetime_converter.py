from dataclasses import Field
from dict_to_dataclass.exceptions import DictValueConversionError
from dateutil.parser import parse
from datetime import datetime
from typing import Any, Optional


def convert_datetime(dc_field: Optional[Field], value: Any):
    """Default converter for datetime dataclass fields.

    Supports converting the following dict value types to a datetime instance
    - Strings of any format that `dateutil.parser` can handle
    - JS-style timestamps as `int`s
    - Python-style timestamps as `float`s
    """
    try:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            return parse(value)

        if isinstance(value, int):
            return datetime.fromtimestamp(value / 1000)

        if isinstance(value, float):
            return datetime.fromtimestamp(value)
    except Exception:
        pass

    raise DictValueConversionError(dc_field, value)
