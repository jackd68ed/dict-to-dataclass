from dataclasses import dataclass
from typing import List
from unittest import TestCase

from dict_to_dataclass import (
    DataclassFromDict,
    dataclass_from_dict,
    field_from_dict,
)


class DictToDataclassTestCase(TestCase):
    def test_should_return_dataclass_instance(self):
        @dataclass
        class TestClass:
            my_field: str = "default"

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
            my_field: str = field_from_dict()

        origin_dict = {"myField": "valueDoesntMatter"}

        expected = TestClass(my_field="valueDoesntMatter")
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_use_field_converter_if_present(self):
        @dataclass
        class TestClass:
            my_field: str = field_from_dict("testField", converter=lambda x: "converter_result")

        origin_dict = {"testField": "valueDoesntMatter"}

        expected = TestClass(my_field="converter_result")
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_dataclass_type(self):
        @dataclass
        class TestChildClass:
            my_field: str = field_from_dict()

        @dataclass
        class TestClass:
            child_field: TestChildClass = field_from_dict()

        origin_dict = {"childField": {"myField": "testChildFieldValue"}}

        expected = TestClass(child_field=TestChildClass(my_field="testChildFieldValue"))
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_list_type(self):
        @dataclass
        class TestClass:
            my_field: List[str] = field_from_dict("testList")

        origin_dict = {"testList": ["value1", "value2"]}

        expected = TestClass(my_field=["value1", "value2"])
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_get_field_of_list_of_dataclasses(self):
        @dataclass
        class TestChildClass:
            my_field: str = field_from_dict("testChildStrField")
            field_with_converter: str = field_from_dict("testChildConvertedField", lambda x: "convertedValue")

        @dataclass
        class TestClass:
            children: List[TestChildClass] = field_from_dict()

        origin_dict = {
            "children": [
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
            children=[
                TestChildClass(my_field="testStrValue", field_with_converter="convertedValue"),
                TestChildClass(my_field="testStrValue", field_with_converter="convertedValue"),
            ]
        )
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))

    def test_should_use_converter_for_list_field(self):
        @dataclass
        class TestClass:
            my_field: List[str] = field_from_dict(converter=lambda x: ["convertedValue"])

        origin_dict = {"myField": []}

        expected = TestClass(my_field=["convertedValue"])
        self.assertEqual(expected, dataclass_from_dict(TestClass, origin_dict))
