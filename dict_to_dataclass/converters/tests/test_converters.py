from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from unittest import TestCase

from dict_to_dataclass import field_from_dict
from dict_to_dataclass.base_class import DataclassFromDict


class DateTimeConverterTestCase(TestCase):
    @dataclass
    class MyClass(DataclassFromDict):
        my_date: datetime = field_from_dict()

    @dataclass
    class WithOptional(DataclassFromDict):
        my_optional_date: Optional[datetime] = field_from_dict()

    def test_should_convert_iso_string(self):
        date_value = datetime.now()

        origin = {"my_date": date_value.isoformat()}

        expected = DateTimeConverterTestCase.MyClass(my_date=date_value)
        self.assertEqual(expected, DateTimeConverterTestCase.MyClass.from_dict(origin))

    def test_should_convert_utc_string(self):
        utc_string = "Sat, 10 Oct 2020 16:17:50 GMT"
        date_value = datetime(year=2020, month=10, day=10, hour=16, minute=17, second=50, tzinfo=timezone.utc)

        origin = {"my_date": utc_string}

        expected = DateTimeConverterTestCase.MyClass(my_date=date_value)
        self.assertEqual(expected, DateTimeConverterTestCase.MyClass.from_dict(origin))

    def test_should_convert_js_timestamp(self):
        # We lose some precision
        date_value = datetime.now().replace(microsecond=0)

        origin = {"my_date": int(date_value.timestamp() * 1000)}

        expected = DateTimeConverterTestCase.MyClass(my_date=date_value)
        self.assertEqual(expected, DateTimeConverterTestCase.MyClass.from_dict(origin))

    def test_should_convert_python_timestamp(self):
        # We lose some precision
        date_value = datetime.now()

        origin = {"my_date": date_value.timestamp()}

        expected = DateTimeConverterTestCase.MyClass(my_date=date_value)
        self.assertEqual(expected, DateTimeConverterTestCase.MyClass.from_dict(origin))

    def test_should_handle_optional_type(self):
        date_value = datetime.now()

        origin = {"my_optional_date": date_value.isoformat()}

        expected = DateTimeConverterTestCase.WithOptional(my_optional_date=date_value)
        self.assertEqual(expected, DateTimeConverterTestCase.WithOptional.from_dict(origin))
