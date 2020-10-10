class DataclassFromDict:
    """A base class for dataclasses that can be created using `dataclass_from_dict`"""

    # True if the origin dictionary's keys are in camelCase. Used when `field_from_dict`s are created
    # and `dict_key` is omitted.
    dict_has_camel_case_keys = False
