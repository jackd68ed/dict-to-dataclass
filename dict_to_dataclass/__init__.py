from dataclasses import MISSING, Field, field, fields, is_dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar

import dict_to_dataclass._base_class
from ._type_utils import type_is_list_with_item_type, type_is_optional, get_optional_type
from ._converters import default_value_converter_map
from ._converters.enum_converter import convert_enum
from .exceptions import (
    DictKeyNotFoundError,
    DictValueConversionError,
    DictValueNotFoundError,
    UnspecificListFieldError,
)

__version__ = "0.0.8"
__all__ = ["DataclassFromDict", "field_from_dict", "dataclass_from_dict"]

# Allow export from top-level package
DataclassFromDict = dict_to_dataclass._base_class.DataclassFromDict


def field_from_dict(
    dict_key: str = None,
    converter: Callable = None,
    *args,
    **kwargs,
):
    """A dataclass field with required metadata for extracting it from a `dict`

    :param dict_key: The key in the dict that contains the value for this field. If omitted, the name of the field in
        the dataclass is used.
    :param converter: The function to convert the dict value to the type of the class field
    """
    dict_field_metadata = {
        "converter": converter,
        "dict_key": dict_key,
        "should_get_from_dict": True,
    }
    metadata: Dict[str, Any] = {**kwargs.pop("metadata", {}), **dict_field_metadata}

    return field(metadata=metadata, *args, **kwargs)


def _use_default_converter(dc_field: Optional[Field], field_type: Any, value_from_dict: Any):
    try:
        if issubclass(field_type, Enum):
            return convert_enum(dc_field, value_from_dict, enum=field_type)
    except TypeError:
        # The first arg to `issubclass` must be a class
        pass

    try:
        if (convert := default_value_converter_map.get(field_type.__name__)) is not None:
            return convert(dc_field, value_from_dict)
    except AttributeError:
        # Sometimes field_type doesn't have a __name__ attribute. Not sure why yet.
        pass

    return None


def _convert_value_for_dataclass(value_from_dict, dc_field: Field = None, list_item_type=None):
    """Convert a value from a dict for a dataclass field

    :param value_from_dict: The value from the dict
    :param dc_field: The target dataclass field
    :param list_item_type: The type of the items in the list if the target field type is a `typing.List[type]`
    """
    field_type = dc_field.type if dc_field else list_item_type

    # Handle optional types
    field_type = get_optional_type(field_type)

    if field_type is None:
        raise Exception("Please provide either dc_field or list_item_type")

    field_converter = dc_field.metadata.get("converter") if dc_field else None

    if field_converter:
        return field_converter(value_from_dict)

    if type_is_list_with_item_type(field_type, dc_field):
        return [_convert_value_for_dataclass(item, list_item_type=field_type.__args__[0]) for item in value_from_dict]
    elif field_type is list:
        raise UnspecificListFieldError(dataclass_field=dc_field)

    if isinstance(value_from_dict, field_type):
        return value_from_dict

    if (default_converter_value := _use_default_converter(dc_field, field_type, value_from_dict)) is not None:
        return default_converter_value

    if is_dataclass(field_type):
        return dataclass_from_dict(field_type, value_from_dict)

    raise DictValueConversionError(dc_field, value_from_dict)


def _to_camel_case(snake_str: str):
    """Converts the given snake_case string to camelCase"""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _get_value_from_dict(dc_field: Field, origin_dict: dict):
    # Use the dict_key in the field metadata if one was provided
    if (dict_key := dc_field.metadata.get("dict_key")) is not None:
        try:
            return origin_dict[dict_key]
        except KeyError:
            raise DictKeyNotFoundError(dc_field, origin_dict)

    # TODO: Test that we don't error if the snake_case field name is in the dict but has a `None` value
    # If not, first, try the field's name
    try:
        return origin_dict[dc_field.name]
    except KeyError:
        pass

    # If that's not found, try it in camelCase
    try:
        return origin_dict[_to_camel_case(dc_field.name)]
    except KeyError:
        raise DictKeyNotFoundError(dc_field, origin_dict)


_T = TypeVar("_T")


def dataclass_from_dict(dataclass_type: Type[_T], origin_dict: dict) -> _T:
    """Create a dataclass instance from the given parsed dict

    :param dataclass_type: The type of the dataclass to be instantiated
    :param origin_dict: The dictionary to convert
    :raises DictKeyNotFoundError: Raised if an attribute defined in a dataclass field's metadata is not found
        in the origin dict
    :raises DictValueNotFoundError: Raised when a value is None in a dictionary and the field is not Optional in the
        dataclass
    :raises DictValueConversionError: Raised if the value in the origin dict can't be converted to the associated
        dataclass field's type
    :raises UnspecificListFieldError: Raised when a list field in a dataclass does not specify the type of its items
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"dataclass_type must be a dataclass. Received {dataclass_type}")

    # Ignore ordinary dataclass fields
    fields_from_dict = (
        dc_field for dc_field in fields(dataclass_type) if dc_field.metadata.get("should_get_from_dict")
    )
    dc_init_args = {}

    for dc_field in fields_from_dict:
        try:
            value_from_dict = _get_value_from_dict(dc_field, origin_dict)
        except DictKeyNotFoundError:
            # If the field has a default value, we can just not include it when constructing the dataclass instance
            if dc_field.default != MISSING or dc_field.default_factory != MISSING:
                continue
            else:
                raise

        if not type_is_optional(dc_field.type) and value_from_dict is None:
            raise DictValueNotFoundError(dc_field, origin_dict)
        elif value_from_dict is None:
            # Here, we've got a value of None for an optional field. Don't bother trying to convert it.
            dc_init_args[dc_field.name] = value_from_dict
            continue

        dc_init_args[dc_field.name] = _convert_value_for_dataclass(value_from_dict, dc_field)

    return dataclass_type(**dc_init_args)
