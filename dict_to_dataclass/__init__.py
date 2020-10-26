from dataclasses import Field, field, fields, is_dataclass, MISSING
from dict_to_dataclass.exceptions import (
    DictKeyNotFoundError,
    DictValueConversionError,
    NonSpecificListFieldError,
    DictValueNotFoundError,
)
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from dict_to_dataclass.converters import default_value_converter_map


def field_from_dict(
    dict_key: str = None,
    converter: Callable = None,
    ignore_conversion_errors: bool = False,
    *args,
    **kwargs,
):
    """A dataclass field with required metadata for extracting it from a `dict`

    :param dict_key: The key in the dict that contains the value for this field. If omitted, the name of the field in
        the dataclass is used.
    :param converter: The function to convert the dict value to the type of the class field
    :param ignore_conversion_errors: True if `DictValueConversionError`s should be ignored. `None` will be returned on
        error if True.
    """
    dict_field_metadata = {
        "converter": converter,
        "dict_key": dict_key,
        "ignore_conversion_errors": ignore_conversion_errors,
        "should_get_from_dict": True,
    }
    metadata: Dict[str, Any] = {**kwargs.pop("metadata", {}), **dict_field_metadata}

    return field(metadata=metadata, *args, **kwargs)


def _no_conversion_required_for_json_value(value, field_type):
    """True if the given value from a dict can be set to a dataclass field without conversation"""
    return (field_type in [bool, float, int, str] and isinstance(value, field_type)) or value is None


def _type_is_list_with_item_type(field_type):
    """True if the given type is `typing.List` with an item type specified"""
    is_list = hasattr(field_type, "__origin__") and field_type.__origin__ is list

    if is_list and isinstance(field_type.__args__[0], TypeVar):
        raise NonSpecificListFieldError()

    return is_list


def _type_is_optional(field_type: Type):
    # TODO: There must be a better way
    return str(field_type).startswith("typing.Union")


def _get_optional_type(field_type: Type) -> Type:
    """If the given type is optional, return the type that is not none. If not, the given field is returned.

    Example::

        _get_optional_type(Type[Optional[str]])  # str
        _get_optional_type(Type[str])  # str
    """
    if _type_is_optional(field_type):
        return next(arg for arg in field_type.__args__ if arg is not None)
    else:
        return field_type


def _use_default_converter(dc_field: Optional[Field], field_type: Any, value_from_dict: Any):
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
    field_type = _get_optional_type(field_type)

    if field_type is None:
        raise Exception("Please provide either dc_field or list_item_type")

    field_converter = dc_field.metadata.get("converter") if dc_field else None

    if field_converter:
        return field_converter(value_from_dict)

    if (default_converter_value := _use_default_converter(dc_field, field_type, value_from_dict)) is not None:
        return default_converter_value

    if _type_is_list_with_item_type(field_type):
        return [_convert_value_for_dataclass(item, list_item_type=field_type.__args__[0]) for item in value_from_dict]
    elif field_type is list:
        raise NonSpecificListFieldError()

    if is_dataclass(field_type):
        return dataclass_from_dict(field_type, value_from_dict)

    if _no_conversion_required_for_json_value(value_from_dict, field_type):
        return value_from_dict

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


T = TypeVar("T")


def dataclass_from_dict(dataclass_type: Type[T], origin_dict: dict) -> T:
    """Create a dataclass instance from the given parsed dict

    :param dataclass_type: The type of the dataclass to be instantiated
    :param origin_dict: The dictionary to convert
    :raises DictKeyNotFoundError: Raised if an attribute defined in a dataclass field's metadata is not found
        in the json response
    :raises DictValueConversionError: Raised if the value in the json response can't be converted to the associated
        dataclass field's type
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"dataclass_type must be a dataclass. Received {dataclass_type}")

    init_args = {}

    for dc_field in fields(dataclass_type):
        # Ignore non-json response fields
        if not dc_field.metadata.get("should_get_from_dict"):
            continue

        try:
            value_from_dict = _get_value_from_dict(dc_field, origin_dict)
        except DictKeyNotFoundError:
            # If the field has a default value, we can just not include it when constructing the dataclass instance
            if dc_field.default != MISSING or dc_field.default_factory != MISSING:
                continue
            else:
                raise

        if not _type_is_optional(dc_field.type) and value_from_dict is None:
            raise DictValueNotFoundError(dc_field, origin_dict)
        elif value_from_dict is None:
            # Here, we've got a value of None for an optional field. Don't bother trying to convert it.
            init_args[dc_field.name] = value_from_dict
            continue

        try:
            converted_value = _convert_value_for_dataclass(value_from_dict, dc_field)
        except DictValueConversionError as e:
            if not dc_field.metadata.get("ignore_conversion_errors", False):
                raise e
            else:
                converted_value = None

        init_args[dc_field.name] = converted_value

    return dataclass_type(**init_args)
