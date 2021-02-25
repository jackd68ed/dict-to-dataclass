from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from unittest import TestCase

from dict_to_dataclass import (
    DataclassFromDict,
    dataclass_from_dict,
    field_from_dict,
)
from dict_to_dataclass.exceptions import (
    DictValueConversionError,
    DictKeyNotFoundError,
    DictValueNotFoundError,
    UnspecificListFieldError,
)


class DictToDataclassTestCase(TestCase):
    def test_should_return_dataclass_instance(self):
        @dataclass
        class TestClass:
            param: str = "default"

        self.assertEqual(TestClass(), dataclass_from_dict(TestClass, {}))

    def test_should_get_basic_field_values_from_dict(self):
        @dataclass
        class TestClass:
            test_bool_field: bool = field_from_dict("testBoolField")
            test_float_field: float = field_from_dict("testFloatField")
            test_int_field: int = field_from_dict("testIntField")
            test_str_field: str = field_from_dict("testStrField")

        origin_dict = {
            "testBoolField": True,
            "testFloatField": 12.34,
            "testIntField": 123,
            "testStrField": "string_value",
        }

        expected = TestClass(
            test_bool_field=True,
            test_float_field=12.34,
            test_int_field=123,
            test_str_field="string_value",
        )

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_use_field_name_if_dict_key_is_missing(self):
        @dataclass
        class TestClass:
            my_field: str = field_from_dict()

        origin_dict = {"my_field": "valueDoesntMatter"}

        expected = TestClass(my_field="valueDoesntMatter")

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_use_camel_cased_field_name_if_dict_key_is_missing_and_dict_has_camel_case_keys(self):
        @dataclass
        class TestClass(DataclassFromDict):
            dict_has_camel_case_keys = True

            my_field: str = field_from_dict()

        origin_dict = {"myField": "valueDoesntMatter"}

        expected = TestClass(my_field="valueDoesntMatter")

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

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

    def test_should_use_field_converter_if_present(self):
        @dataclass
        class TestClass:
            param: str = field_from_dict("testField", converter=lambda x: "converter_result")

        origin_dict = {"testField": "valueDoesntMatter"}

        expected = TestClass(param="converter_result")

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_dataclass_type(self):
        @dataclass
        class TestChildClass:
            param: str = field_from_dict("testChildField")

        @dataclass
        class TestClass:
            dc_param: TestChildClass = field_from_dict("testChild")

        origin_dict = {"testChild": {"testChildField": "testChildFieldValue"}}

        expected = TestClass(dc_param=TestChildClass(param="testChildFieldValue"))

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_list_type(self):
        @dataclass
        class TestClass:
            dc_param: List[str] = field_from_dict("testList")

        origin_dict = {"testList": ["value1", "value2"]}

        expected = TestClass(dc_param=["value1", "value2"])

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_list_of_dataclasses(self):
        @dataclass
        class TestChildClass:
            param: str = field_from_dict("testChildStrField")
            converter_param: str = field_from_dict("testChildConvertedField", lambda x: "convertedValue")

        @dataclass
        class TestClass:
            dc_param: List[TestChildClass] = field_from_dict("testList")

        origin_dict = {
            "testList": [
                {
                    "testChildStrField": "testStrValue",
                    "testChildConvertedField": "testRawValue",
                },
                {
                    "testChildStrField": "testStrValue",
                    "testChildConvertedField": "testRawValue",
                },
            ]
        }

        expected = TestClass(
            dc_param=[
                TestChildClass(param="testStrValue", converter_param="convertedValue"),
                TestChildClass(param="testStrValue", converter_param="convertedValue"),
            ]
        )

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_use_converter_for_list_field(self):
        @dataclass
        class TestClass:
            dc_param: List[str] = field_from_dict("testList", lambda x: ["convertedValue"])

        origin_dict = {"testList": []}

        expected = TestClass(dc_param=["convertedValue"])

        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

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
