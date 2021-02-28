from dataclasses import Field
from typing import Type, TypeVar, Union

from .exceptions import UnspecificListFieldError


def type_is_list_with_item_type(field_type: Type, dc_field: Field):
    """True if the given type is `typing.List` with an item type specified"""
    is_list = hasattr(field_type, "__origin__") and field_type.__origin__ is list

    if is_list and isinstance(field_type.__args__[0], TypeVar):
        raise UnspecificListFieldError(dataclass_field=dc_field)

    return is_list


def type_is_union(field_type: Type):
    try:
        return field_type.__origin__ == Union
    except AttributeError:
        return False


def type_is_optional(field_type: Type):
    # It seems that we can't use isinstance to check for NoneType
    return type_is_union(field_type) and any(arg is type(None) for arg in field_type.__args__)  # noqa: E721


def get_optional_type(field_type: Type) -> Type:
    """If the given type is optional, return the type that is not None. If not, the given field is returned.

    Example::

        _get_optional_type(Type[Optional[str]])  # str
        _get_optional_type(Type[str])  # str
    """
    if type_is_optional(field_type):
        # It seems that we can't use isinstance to check for NoneType
        return next(arg for arg in field_type.__args__ if arg is not type(None))  # noqa: E721
    else:
        return field_type
