from dataclasses import dataclass
from enum import Enum
from typing import Optional
from unittest import TestCase

from dict_to_dataclass import field_from_dict
from dict_to_dataclass.base_class import DataclassFromDict
from exceptions import EnumValueNotFoundError


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
        with self.assertRaises(EnumValueNotFoundError):
            MyDataclass.from_dict({"enumField": "DOESNT_EXIST"})

        with self.assertRaises(EnumValueNotFoundError):
            MyDataclass.from_dict({"enumField": 1})

        with self.assertRaises(EnumValueNotFoundError):
            MyDataclass.from_dict({"enumField": True})

    def test_should_handle_optional_type(self):
        origin_dict = {"enumField": "SECOND"}

        dataclass_instance = MyDataclassWithOptional.from_dict(origin_dict)
        self.assertEqual(dataclass_instance.enum_field, MyEnum.SECOND)
