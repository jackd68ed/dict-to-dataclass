from dataclasses import Field
from typing import Optional


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
