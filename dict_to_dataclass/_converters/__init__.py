from dict_to_dataclass._converters.datetime_converter import convert_datetime

# Value converter functions mapped by their output type
default_value_converter_map = {
    "datetime": convert_datetime,
}
