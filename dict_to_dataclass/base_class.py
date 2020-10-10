from dict_to_dataclass import dataclass_from_dict


class DataclassFromDict:
    """A base class for dataclasses that can be created using `dataclass_from_dict`"""

    @classmethod
    def from_dict(cls, origin_dict: dict):
        return dataclass_from_dict(cls, origin_dict)
