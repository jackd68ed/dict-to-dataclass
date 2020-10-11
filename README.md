# Dict to dataclass

Utils for mapping dataclass fields to dictionary keys, making it possible to create an instance of a dataclass from a dictionary.

```python
# Declare dataclass fields with `field_from_dict`
@dataclass
class MyDataclass(DataclassFromDict):
    my_string: str = field_from_dict()
    my_int: int = field_from_dict()
    my_date: datetime = field_from_dict()


# Create a dataclass instance using the `from_dict` constructor
origin_dict = {
  "my_string": "Hello",
  "my_int": 123,
  "my_date": "2020-10-11T13:21:23.396748",
}

dataclass_instance = MyDataclass.from_dict(origin_dict)

# Now, our dataclass instance has the values from the dictionary
>>> dataclass_instance.my_string
"Hello"

>>> dataclass_instance.my_int
123

>>> dataclass_instance.my_date
datetime.datetime(2020, 10, 11, 13, 21, 23, 396748)
```
