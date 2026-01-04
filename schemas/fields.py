from marshmallow import ValidationError, fields


class EnumField(fields.Field):
    """
    Simple enum field that serializes to the enum name and accepts either the
    name (case-insensitive) or value when deserializing.
    """

    def __init__(self, enum_cls, by_value=False, **kwargs):
        self.enum_cls = enum_cls
        self.by_value = by_value
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value if self.by_value else value.name

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None

        try:
            if self.by_value:
                return self.enum_cls(value)

            return self.enum_cls[value]  # type: ignore[index]
        except KeyError:
            if isinstance(value, str):
                try:
                    return self.enum_cls[value.upper()]  # type: ignore[index]
                except KeyError:
                    pass
        except ValueError:
            pass

        raise ValidationError(f"Invalid value '{value}' for enum {self.enum_cls.__name__}")
