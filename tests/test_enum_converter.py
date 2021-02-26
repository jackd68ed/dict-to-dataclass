from dataclasses import dataclass
from enum import Enum
from typing import Optional
from unittest import TestCase

from dict_to_dataclass import DataclassFromDict, field_from_dict
from dict_to_dataclass.exceptions import EnumValueNotFoundError


class MyEnum(Enum):
    FIRST = 1
    SECOND = 2


@dataclass
class MyDataclass(DataclassFromDict):
    enum_field: MyEnum = field_from_dict()


@dataclass
class MyDataclassWithOptional(DataclassFromDict):
    enum_field: Optional[MyEnum] = field_from_dict()


class EnumConverterTestCase(TestCase):
    def test_should_convert_string_to_enum_value(self):
        origin_dict = {"enumField": "SECOND"}

        dataclass_instance = MyDataclass.from_dict(origin_dict)
        self.assertEqual(dataclass_instance.enum_field, MyEnum.SECOND)

    def test_should_raise_conversion_error_if_enum_value_doesnt_exist(self):
        with self.assertRaises(EnumValueNotFoundError) as context:
            MyDataclass.from_dict({"enumField": "DOESNT_EXIST"})

        expected_message = "The value 'DOESNT_EXIST' was not found in the MyEnum enum."
        self.assertEqual(expected_message, str(context.exception))

        with self.assertRaises(EnumValueNotFoundError) as context:
            MyDataclass.from_dict({"enumField": 1})

        expected_message = "The value '1' was not found in the MyEnum enum."
        self.assertEqual(expected_message, str(context.exception))

        with self.assertRaises(EnumValueNotFoundError) as context:
            MyDataclass.from_dict({"enumField": True})

        expected_message = "The value 'True' was not found in the MyEnum enum."
        self.assertEqual(expected_message, str(context.exception))

    def test_should_handle_optional_type(self):
        origin_dict = {"enumField": "SECOND"}

        dataclass_instance = MyDataclassWithOptional.from_dict(origin_dict)
        self.assertEqual(dataclass_instance.enum_field, MyEnum.SECOND)
