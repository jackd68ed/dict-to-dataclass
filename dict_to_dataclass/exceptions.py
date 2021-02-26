from dataclasses import Field
from typing import Optional


class DataclassFromDictError(Exception):
    """Raised when an error occurs during the conversion of a dict to a dataclass instance"""

    pass


class DictKeyNotFoundError(DataclassFromDictError):
    """Raised when a key cannot be found in a dictionary while converting it to a dataclass instance"""

    def __init__(self, dataclass_field: Field, origin_dict: dict):
        # If the field has a dict_key explicitly set, include it in the error message
        field_dict_key = dataclass_field.metadata.get("dict_key")
        field_dict_key_for_message = (
            f" (with '{field_dict_key}' specified as dict_key)" if field_dict_key is not None else ""
        )

        super().__init__(
            f"Could not find a dictionary key for the {dataclass_field.name} field{field_dict_key_for_message}."
        )

        self.dataclass_field = dataclass_field
        self.origin_dict = origin_dict


class DictValueNotFoundError(DataclassFromDictError):
    """Raised when a value is None in a dictionary and the field is not Optional in the dataclass"""

    def __init__(self, dataclass_field: Field, origin_dict: dict):
        super().__init__(
            f"A value of None was found for the field, {dataclass_field.name} but the field does not have an optional "
            f"type. If you expect the value of this field to potentially be None, you can make its type "
            f"Optional[{dataclass_field.type.__name__}].",
        )

        self.dataclass_field = dataclass_field
        self.origin_dict = origin_dict


class DictValueConversionError(DataclassFromDictError):
    """Raised when a value in a dictionary cannot be converted"""

    def __init__(self, dataclass_field: Optional[Field], value_from_dict):
        super().__init__(
            f"Could not convert dictionary value to type {dataclass_field.type.__name__} for field "
            f"{dataclass_field.name}. Found value '{value_from_dict}' of type {type(value_from_dict).__name__}."
        )

        self.dataclass_field = dataclass_field
        self.value_from_dict = value_from_dict


class EnumValueNotFoundError(DataclassFromDictError):
    """Raised when a dict value is not found in a dataclass field's `Enum` type"""

    def __init__(self, dataclass_field: Optional[Field], value_from_dict):
        super().__init__(f"The value '{value_from_dict}' was not found in the {dataclass_field.type.__name__} enum.")

        self.dataclass_field = dataclass_field
        self.value_from_dict = value_from_dict


class UnspecificListFieldError(DataclassFromDictError):
    """Raised when a list field in a dataclass does not specify the type of its items

    E.g.::

        list_of_strings: List = field_from_dict()

    Instead of::

        list_of_strings: List[str] = field_from_dict()
    """

    def __init__(self, dataclass_field: Optional[Field]):
        super().__init__(
            f"An item type was not specified for the list field, {dataclass_field.name}. Please give the field a type "
            "like 'List[<item type>]' to allow conversion from a dictionary."
        )

        self.dataclass_field = dataclass_field
