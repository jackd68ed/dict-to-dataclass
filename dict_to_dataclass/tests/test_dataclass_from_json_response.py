from dataclasses import dataclass
from decimal import Decimal
from typing import List
from unittest import TestCase

from dict_to_dataclass import (
    dataclass_from_dict,
    field_from_dict,
    DictKeyNotFoundError,
    DictValueConversionError,
    NonSpecificListFieldError,
)


class DataclassFromJSONResponseTestCase(TestCase):
    def test_should_return_dataclass_instance(self):
        @dataclass
        class TestClass:
            param: str = "default"

        self.assertEqual(TestClass(), dataclass_from_dict(TestClass, {}))

    def test_should_get_basic_field_values_from_json_response(self):
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

    def test_should_get_field_of_list__of_dataclasses(self):
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

    def test_should_raise_error_if_attribute_not_found(self):
        @dataclass
        class TestClass:
            param: str = field_from_dict("notFoundField")

        origin_dict = {"unexpectedField": "value"}

        with self.assertRaises(DictKeyNotFoundError):
            dataclass_from_dict(TestClass, origin_dict)

    def test_should_raise_error_if_attribute_cannot_be_converted(self):
        @dataclass
        class TestClass:
            param: Decimal = field_from_dict("testField")

        origin_dict = {"testField": "cannot_convert"}

        with self.assertRaises(DictValueConversionError):
            dataclass_from_dict(TestClass, origin_dict)

    def test_should_set_field_to_none_if_attribute_cannot_be_converted_and_should_ignore_errors(
        self,
    ):
        @dataclass
        class TestClass:
            param: Decimal = field_from_dict("testField", ignore_conversion_errors=True)

        origin_dict = {"testField": "cannot_convert"}

        dc = dataclass_from_dict(TestClass, origin_dict)
        self.assertIsNone(dc.param)

    def test_should_raise_error_if_list_field_doesnt_specify_item_type(self):
        @dataclass
        class TestClass1:
            list_param: List = field_from_dict("testList")

        @dataclass
        class TestClass2:
            list_param: list = field_from_dict("testList")

        origin_dict = {"testList": []}

        with self.assertRaises(NonSpecificListFieldError):
            dataclass_from_dict(TestClass1, origin_dict)

        with self.assertRaises(NonSpecificListFieldError):
            dataclass_from_dict(TestClass2, origin_dict)
