from dataclasses import dataclass
from unittest import TestCase
from dict_to_dataclass.base_class import DataclassFromDict
from dict_to_dataclass import field_from_dict


class BaseClassTestCase(TestCase):
    def test_should_construct_instance_from_dict(self):
        @dataclass
        class MyDataclass(DataclassFromDict):
            my_field: str = field_from_dict()

        expected = MyDataclass(my_field="field value")

        self.assertEqual(expected, MyDataclass.from_dict({"my_field": "field value"}))

    def test_should_construct_instance_from_json(self):
        @dataclass
        class MyDataclass(DataclassFromDict):
            my_field: str = field_from_dict()

        expected = MyDataclass(my_field="field value")

        self.assertEqual(expected, MyDataclass.from_json('{"my_field": "field value"}'))
