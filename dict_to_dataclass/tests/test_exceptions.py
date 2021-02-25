from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List
from unittest.case import TestCase

from dict_to_dataclass import (
    DataclassFromDict,
    field_from_dict,
    dataclass_from_dict,
)
from dict_to_dataclass.exceptions import (
    DictValueNotFoundError,
    DictKeyNotFoundError,
    DictValueConversionError,
    UnspecificListFieldError,
)


class ExceptionsTestCase(TestCase):
    def test_should_not_error_if_optional_field_name_exists_in_dict_but_has_none_value(self):
        # Inspired by this happening in another project

        @dataclass
        class TestClass(DataclassFromDict):
            my_field: Optional[str] = field_from_dict()

        origin_dict = {"my_field": None}

        expected = TestClass(my_field=None)
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_error_if_non_optional_field_name_exists_in_dict_but_has_none_value(self):
        @dataclass
        class TestClass(DataclassFromDict):
            my_field: str = field_from_dict()

        origin_dict = {"my_field": None}

        with self.assertRaises(DictValueNotFoundError) as context:
            dataclass_from_dict(TestClass, origin_dict)

        expected_message = (
            "A value of None was found for the field, my_field but the field does not have an optional type. If you "
            "expect the value of this field to potentially be None, you can make its type Optional[str]."
        )
        self.assertEqual(str(context.exception), expected_message)

    def test_should_raise_error_if_key_not_found(self):
        @dataclass
        class TestClass:
            my_field: str = field_from_dict()

        @dataclass
        class TestClassWithDictKeySpecified:
            my_field: str = field_from_dict("myFieldInDict")

        # Check the message with no dict_key specified
        with self.assertRaises(DictKeyNotFoundError) as context:
            dataclass_from_dict(TestClass, {"unexpectedField": "value"})

        expected_message = "Could not find a dictionary key for the my_field field."
        self.assertEqual(expected_message, str(context.exception))

        # Check the message with dict_key specified
        with self.assertRaises(DictKeyNotFoundError) as with_dict_key_context:
            dataclass_from_dict(TestClassWithDictKeySpecified, {"unexpectedField": "value"})

        with_dict_key_expected_message = (
            "Could not find a dictionary key for the my_field field (with 'myFieldInDict' specified as dict_key)."
        )
        self.assertEqual(with_dict_key_expected_message, str(with_dict_key_context.exception))

    def test_not_should_raise_error_if_key_not_found_for_field_with_default_value(self):
        @dataclass
        class TestClass:
            param: str = field_from_dict("notFoundField", default="default value")

        origin_dict = {"unexpectedField": "value"}

        expected = TestClass(param="default value")
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_raise_error_if_attribute_cannot_be_converted(self):
        @dataclass
        class TestClass:
            my_field: Decimal = field_from_dict()

        origin_dict = {"myField": "cannot_convert"}

        with self.assertRaises(DictValueConversionError) as context:
            dataclass_from_dict(TestClass, origin_dict)

        expected_message = (
            "Could not convert dictionary value to type Decimal for field my_field. Found value 'cannot_convert' of "
            "type str."
        )
        self.assertEqual(expected_message, str(context.exception))

    def test_should_raise_error_if_list_field_doesnt_specify_item_type(self):
        @dataclass
        class TestClass1:
            list_field: List = field_from_dict()

        @dataclass
        class TestClass2:
            list_field: list = field_from_dict()

        origin_dict = {"listField": []}

        with self.assertRaises(UnspecificListFieldError):
            dataclass_from_dict(TestClass1, origin_dict)

        with self.assertRaises(UnspecificListFieldError) as context:
            dataclass_from_dict(TestClass2, origin_dict)

        expected_message = (
            "An item type was not specified for the list field, list_field. Please give the field a type like "
            "'List[<item type>]' to allow conversion from a dictionary."
        )
        self.assertEqual(expected_message, str(context.exception))
