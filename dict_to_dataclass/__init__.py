from dataclasses import Field, field, fields, is_dataclass
from typing import Any, Callable, Dict, Optional, Type, TypeVar


class DataclassFromDictError(Exception):
    """Raised when an error occurs during the conversion of a dict to a dataclass instance"""

    pass


class DictKeyNotFoundError(DataclassFromDictError):
    """Raised when a key cannot be found in a dictionary while converting it to a dataclass instance"""

    def __init__(self, dataclass_field: Field, response):
        self.field = dataclass_field
        self.response = response


class DictValueConversionError(DataclassFromDictError):
    """Raised when a value in a dictionary cannot be converted"""

    def __init__(self, dataclass_field: Optional[Field], value_from_json):
        self.field = dataclass_field
        self.value_from_json = value_from_json


class NonSpecificListFieldError(DataclassFromDictError):
    """Raised when a list field in a dataclass does not specify the type of its items

    E.g.::

        list_of_strings: List = field_from_dict()

    Instead of::

        list_of_strings: List[str] = field_from_dict()
    """

    pass


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


def _convert_value_for_dataclass(value_from_dict, dc_field: Field = None, list_item_type=None):
    """Convert a value from a dict for a dataclass field

    :param value_from_dict: The value from the dict
    :param dc_field: The target dataclass field
    :param list_item_type: The type of the items in the list if the target field type is a `typing.List[type]`
    """
    field_type = dc_field.type if dc_field else list_item_type
    if field_type is None:
        raise Exception("Please provide either dc_field or list_item_type")

    field_converter = dc_field.metadata.get("converter") if dc_field else None

    if field_converter:
        return field_converter(value_from_dict)

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
    # Use the dict_key provided or the field's name if omitted
    if (dict_key := dc_field.metadata.get("dict_key")) is not None:
        try:
            return origin_dict[dict_key]
        except KeyError:
            raise DictKeyNotFoundError(dc_field, origin_dict)
    else:
        try:
            # First, try the field's name. If that's not found, try it in camelCase.
            return origin_dict.get(dc_field.name) or origin_dict[_to_camel_case(dc_field.name)]
        except KeyError:
            raise DictKeyNotFoundError(dc_field, origin_dict)


T = TypeVar("T")


def dataclass_from_dict(dataclass_type: Type[T], origin_dict: dict) -> T:
    """Create a dataclass instance from the given parsed dict

    :param dataclass_type: The type of the dataclass to be instantiated
    :param origin_dict: The parsed json response
    :raises JSONAttributeNotFoundError: Raised if an attribute defined in a dataclass field's metadata is not found
        in the json response
    :raises JSONAttributeConversionError: Raised if the value in the json response can't be converted to the associated
        dataclass field's type
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"dataclass_type must be a dataclass. Received {dataclass_type}")

    init_args = {}

    for dc_field in fields(dataclass_type):
        # Ignore non-json response fields
        if not dc_field.metadata.get("should_get_from_dict"):
            continue

        value_from_dict = _get_value_from_dict(dc_field, origin_dict)

        try:
            converted_value = _convert_value_for_dataclass(value_from_dict, dc_field)
        except DictValueConversionError as e:
            if not dc_field.metadata.get("ignore_conversion_errors", False):
                raise e
            else:
                converted_value = None

        init_args[dc_field.name] = converted_value

    return dataclass_type(**init_args)
