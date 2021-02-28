# Table of contents

- [Dict to dataclass](#dict-to-dataclass)
  - [Why?](#why)
  - [Finding dictionary values](#finding-dictionary-values)
  - [Nested data classes](#nested-data-classes)
  - [Lists](#lists)
  - [Value conversion](#value-conversion)
    - [Datetime](#datetime)
    - [Enum](#enum)
    - [Custom converters](#custom-converters)
  - [Optional types](#optional-types)
  - [Missing values](#missing-values)
  - [Data validation](#data-validation)

# Dict to dataclass

Dict to dataclass makes it easy to convert dictionaries to instances of dataclasses.

```python
from dataclasses import dataclass
from datetime import datetime
from dict_to_dataclass import DataclassFromDict, field_from_dict


# Declare dataclass fields with field_from_dict
@dataclass
class MyDataclass(DataclassFromDict):
    my_string: str = field_from_dict()
    my_int: int = field_from_dict()
    my_date: datetime = field_from_dict()


# Create a dataclass instance using the from_dict constructor
origin_dict = {
  "my_string": "Hello",
  "my_int": 123,
  "my_date": "2020-10-11T13:21:23.396748",
}

dataclass_instance = MyDataclass.from_dict(origin_dict)

# Now our dataclass instance has the values from the dictionary
>>> dataclass_instance.my_string
"Hello"

>>> dataclass_instance.my_int
123

>>> dataclass_instance.my_date
datetime.datetime(2020, 10, 11, 13, 21, 23, 396748)
```

## Why?

You can create a dataclass instance from a dictionary already by unpacking the dictionary values and passing them to the dataclass constructor like this:

```python
origin_dict = {
  "my_string": "Hello",
  "my_int": 123,
  "my_date": "2020-10-11T13:21:23.396748",
}

dataclass_instance = MyDataclass(**origin_dict)
```

However, that method doesn't work when we need to consider

- Type validation
- Type conversion, e.g. an ISO string to a `datetime` instance
- Differences between dictionary keys and dataclass field names
- Complex structures with nested dictionaries and lists

## Finding dictionary values

You may have noticed that we don't need to specify where to look in the dictionary for field values. That's because by default, the name given to the field in the dataclass is used. It even works if the key in the dictionary is in camelCase:

```python
@dataclass
class MyDataclass(DataclassFromDict):
    my_field: str = field_from_dict()


origin_dict = {
    "myField": "field value"
}

dataclass_instance = MyDataclass.from_dict(origin_dict)

>>> dataclass_instance.my_field
"field value"
```

It's probably quite common that your dataclass fields have the same names as the dictionary keys they map to but in case they don't, you can pass the dictionary key as the first argument (or the `dict_key` keyword argument) to `field_from_dict`:

```python
@dataclass
class MyDataclass(DataclassFromDict):
    name_in_dataclass: str = field_from_dict("nameInDictionary")

origin_dict = {
    "nameInDictionary": "field value"
}

dataclass_instance = MyDataclass.from_dict(origin_dict)

>>> dataclass_instance.name_in_dataclass
"field value"
```

## Nested data classes

Nested dictionaries can be represented by nested dataclasses.

```python
@dataclass
class Child(DataclassFromDict):
    my_field: str = field_from_dict()


@dataclass
class Parent(DataclassFromDict):
    child_field: Child = field_from_dict()


origin_dict = {
  "child_field": {
      "my_field": "Hello"
  }
}

dataclass_instance = Parent.from_dict(origin_dict)

>>> dataclass_instance.child_field.my_field
"Hello"
```

## Lists

List types are handled but the type of the list's items must be specified in the dataclass field type so that we know how to convert them.

```python
@dataclass
class MyDataclass(DataclassFromDict):
    my_list_field: List[str] = field_from_dict()

origin_dict = {
    "my_list_field": ["First", "Second", "Third"]
}

dataclass_instance = MyDataclass.from_dict(origin_dict)

>>> dataclass_instance.my_list_field
["First", "Second", "Third"]
```

If we were to use the more generic `typing.List` or `list` as the field type, an error would be raised when converting the dictionary (there's more info on errors later).

```python
@dataclass
class MyDataclass(DataclassFromDict):
    name_in_dataclass: List = field_from_dict("nameInDictionary")

origin_dict = {
    "my_list_field": ["First", "Second", "Third"]
}

# Here, an UnspecificListFieldError is raised
dataclass_instance = MyDataclass.from_dict(origin_dict)
```

Lists of other dataclasses are also supported.

```python
@dataclass
class Child(DataclassFromDict):
    name: str = field_from_dict()


@dataclass
class Parent(DataclassFromDict):
    children: List[Child] = field_from_dict()


origin_dict = {
  "children": [
      { "name": "Jane" },
      { "name": "Joe" },
  ]
}

dataclass_instance = Parent.from_dict(origin_dict)

>>> dataclass_instance.children
[Child(name='Jane'), Child(name='Joe')]
```

## Value conversion

If the value found in the dictionary doesn't match the dataclass field type, the dictionary value can be converted.

### Datetime

Dataclass fields of type `datetime` are handled and can be converted from

- Strings (handled by [dateutil](https://dateutil.readthedocs.io/en/stable/))
- Python-style timestamps of type `float`, e.g. `1602436272.681808`
- Javascript-style timestamps of type `int`, e.g. `1602436323268`

### Enum

Dataclass fields with an `Enum` type can also be converted by default:

```python
class Number(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


@dataclass
class MyDataclass(DataclassFromDict):
    number: Number = field_from_dict()


dataclass_instance = MyDataclass.from_dict({"number": "TWO"})

>>> dataclass_instance.number
<Number.TWO: 2>
```

The value in the dictionary should be the name of the Enum value as a string. If the value is not found, an `EnumValueNotFoundError` is raised.

### Custom converters

If you need to convert a dictionary value that isn't covered by the defaults, you can pass in a converter function using `field_from_dict`'s `converter` parameter:

```python
def yes_no_to_bool(yes_no: str) -> bool:
    return yes_no == "yes"


@dataclass
class MyDataclass(DataclassFromDict):
    is_yes: bool = field_from_dict(converter=yes_no_to_bool)

dataclass_instance = MyDataclass.from_dict({"is_yes": "yes"})

>>> dataclass_instance.is_yes
True
```

A `DictValueConversionError` is raised if the dictionary value cannot be converted.

## Optional types

If you expect that the dictionary value for a field might be `None`, the dataclass field should be given an `Optional` type.

```python
@dataclass
class MyDataclass(DataclassFromDict):
    my_field: Optional[str] = field_from_dict()

dataclass_instance = MyDataclass.from_dict({"myField": None})

>>> dataclass_instance.my_field
None
```

If `my_field` above had the type `str` instead, a `DictValueNotFoundError` would be raised.

## Missing values

If you expect that the field might be missing from the dictionary, you should provide a value to either the `default` or `default_factory` parameters of `field_from_dict`. These are passed through to the underlying `dataclasses.field` call, which you can read about [here](https://docs.python.org/3/library/dataclasses.html#dataclasses.field).

If no default value is provided and the key is not found in the dictionary, a `DictKeyNotFoundError` is raised.

```python
@dataclass
class MyDataclass(DataclassFromDict):
    my_field: str = field_from_dict(default="default value")
    my_list_field: str = field_from_dict(default_factory=list)

dataclass_instance = MyDataclass.from_dict({})

>>> dataclass_instance.my_field
"default value"

>>> dataclass_instance.my_list_field
[]
```

Note that if the field exists in the dictionary and has a value of `None`, `default` and `default_factory` are _not_ used. You would still need to give the field an `Optional` type.

```python
@dataclass
class MyDataclass(DataclassFromDict):
    my_field: str = field_from_dict(default="default value")

# Here, a DictValueNotFoundError is raised
dataclass_instance = MyDataclass.from_dict({"myField": None})
```

## Data validation

A side effect of converting a dictionary to a dataclass instance is that the data in the dictionary is validated, which can be useful on its own. For example, imagine we're writing a handler for a POST method in a REST API. If we use a `DataclassFromDict` to describe the request body, we can validate the user's input by attempting to convert it to a dataclass instance.

```python
@dataclass
class CreateResourceBody(DataclassFromDict):
    ...fields


@app.route("/resource", methods=["POST"])
def create_resource():
    body_dict = request.get_json()

    try:
        body_dataclass_instance = CreateResourceBody.from_dict(body_dict)
    except DataclassFromDictError:
        return "Bad request", 400

    # Create the resource with with body_dataclass_instance
```
