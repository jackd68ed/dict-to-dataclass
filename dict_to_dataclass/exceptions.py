from dataclasses import Field
from typing import Optional


class DataclassFromDictError(Exception):
    """Raised when an error occurs during the conversion of a dict to a dataclass instance"""

    pass


class DictKeyNotFoundError(DataclassFromDictError):
    """Raised when a key cannot be found in a dictionary while converting it to a dataclass instance"""

    def __init__(self, dataclass_field: Field, origin_dict: dict):
        self.field = dataclass_field
        self.origin_dict = origin_dict


class DictValueNotFoundError(DataclassFromDictError):
    """Raised when a value is None in a dictionary and the field is not Optional in the dataclass"""

    def __init__(self, dataclass_field: Field, origin_dict: dict):
        super().__init__(
            f"A value of None was found for the field, {dataclass_field.name} but the field does not have an optional "
            f"type. If you expect the value of this field to potentially be None, you can make its type "
            f"Optional[{dataclass_field.type.__name__}]."
        )

        self.field = dataclass_field
        self.origin_dict = origin_dict


class DictValueConversionError(DataclassFromDictError):
    """Raised when a value in a dictionary cannot be converted"""

    def __init__(self, dataclass_field: Optional[Field], value_from_dict):
        self.field = dataclass_field
        self.value_from_json = value_from_dict


class NonSpecificListFieldError(DataclassFromDictError):
    """Raised when a list field in a dataclass does not specify the type of its items

    E.g.::

        list_of_strings: List = field_from_dict()

    Instead of::

        list_of_strings: List[str] = field_from_dict()
    """

    pass
