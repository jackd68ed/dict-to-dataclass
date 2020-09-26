from dataclasses import field, fields, Field, is_dataclass
from typing import Callable, TypeVar, Type


class DataclassFromDictError(Exception):
    pass


class DictKeyNotFoundError(DataclassFromDictError):
    def __init__(self, dataclass_field: Field, response):
        self.field = dataclass_field
        self.response = response


class DictValueConversionError(DataclassFromDictError):
    def __init__(self, dataclass_field: Field, value_from_json):
        self.field = dataclass_field
        self.value_from_json = value_from_json


class NonSpecificListFieldError(DataclassFromDictError):
    pass


def field_from_dict(
    dict_key: str,
    converter: Callable = None,
    ignore_conversion_errors: bool = False,
    *args,
    **kwargs,
):
    """Creates a dataclass field with required metadata for extracting it from a `dict`

    :param dict_key: The key in the dict that contains the value for this field
    :param converter: The function to convert the dict value to the type of the class field
    :param ignore_conversion_errors: True if `DictValueConversionError`s should be ignored. `None` will be returned on
        error if True.
    """
    dict_field_metadata = {
        "dict_key": dict_key,
        "converter": converter,
        "ignore_conversion_errors": ignore_conversion_errors,
    }
    metadata = {**kwargs.pop("metadata", {}), **dict_field_metadata}
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
    elif _type_is_list_with_item_type(field_type):
        return [_convert_value_for_dataclass(item, list_item_type=field_type.__args__[0]) for item in value_from_dict]
    elif field_type is list:
        raise NonSpecificListFieldError()
    elif is_dataclass(field_type):
        return dataclass_from_dict(field_type, value_from_dict)
    elif _no_conversion_required_for_json_value(value_from_dict, field_type):
        return value_from_dict
    else:
        raise DictValueConversionError(dc_field, value_from_dict)


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
        dict_key = dc_field.metadata.get("dict_key")

        # Ignore non-json response fields
        if dict_key is None:
            continue

        if dict_key not in origin_dict:
            raise DictKeyNotFoundError(dc_field, origin_dict)

        value_from_dict = origin_dict[dict_key]
        ignore_conversion_errors = dc_field.metadata.get("ignore_conversion_errors")

        try:
            converted_value = _convert_value_for_dataclass(value_from_dict, dc_field)
        except DictValueConversionError as e:
            if not ignore_conversion_errors:
                raise e
            else:
                converted_value = None

        init_args[dc_field.name] = converted_value

    return dataclass_type(**init_args)
