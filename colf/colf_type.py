def validate_number(v, size, byte_order='little', signed=False):
    if not isinstance(v, int) and not isinstance(v, bytes):
        raise TypeError('must be int or bytes')

    if isinstance(v, bytes):
        if len(v) > size:
            raise ValueError('convert out-of-bound')

    if isinstance(v, int):
        if v.bit_length() / 8 > size:
            raise ValueError('convert out-of-bound')

        v = v.to_bytes(size, byteorder=byte_order, signed=signed)

    return v


class UInt64(bytes):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(validate_number(v, 8))

    def __repr__(self):
        return f'UInt64({super().__repr__()})'


class UInt32(bytes):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(validate_number(v, 4))

    def __repr__(self):
        return f'UInt32({super().__repr__()})'


class UInt16(bytes):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(validate_number(v, 2))

    def __repr__(self):
        return f'UInt16({super().__repr__()})'


class UInt8(bytes):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(validate_number(v, 1))

    def __repr__(self):
        return f'UInt8({super().__repr__()})'


class Int32(bytes):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(validate_number(v, 4, signed=True))

    def __repr__(self):
        return f'Int32({super().__repr__()})'
