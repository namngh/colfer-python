import ctypes
import datetime
import json
import sys
from collections import OrderedDict

import six

if sys.version_info[0:2] >= (3, 7):
    long = int

class TypeCheckMixin(object):
    def __isType(self, variable, typesToCheck):
        for typeToCheck in typesToCheck:
            if type(variable) is typeToCheck or isinstance(variable, typeToCheck):
                return True
        return False

    def __checkRange(self, variable, minInclusive, maxInclusive):
        return variable >= minInclusive and variable <= maxInclusive

    def __isInt(self, variable):
        # In Python 2.7, -2^31 is treated as long, not int.
        return self.__isType(variable, [int, long])

    def __isShort(self, variable):
        return self.isInt16(variable)

    def __isLong(self, variable):
        return self.__isType(variable, [long])

    def __isFloat(self, variable):
        # TODO: Figure out Float128, Big Number Types in Python
        return self.__isType(variable, [float])

    def isBool(self, variable):
        return self.__isType(variable, [bool])

    def isInt8(self, variable):
        return self.__isInt(variable) and self.__checkRange(variable, -128, 127)

    def isUint8(self, variable):
        return self.__isInt(variable) and self.__checkRange(variable, 0, 255)

    def isInt16(self, variable):
        # Two's complement allows -32768
        return self.__isInt(variable) and self.__checkRange(variable, -32768, 32767)

    def isUint16(self, variable):
        return self.__isInt(variable) and self.__checkRange(variable, 0, 65535)

    def isInt32(self, variable):
        return self.__isInt(variable) and self.__checkRange(variable, -2147483648, 2147483647)

    def isUint32(self, variable):
        return self.__isInt(variable) and self.__checkRange(variable, 0, 4294967295)

    def isInt64(self, variable):
        return (self.__isLong(variable) or self.__isInt(variable)) \
               and self.__checkRange(variable, -9223372036854775808, 9223372036854775807)

    def isUint64(self, variable):
        return (self.__isLong(variable) or self.__isInt(variable)) \
               and self.__checkRange(variable, 0, 18446744073709551615)

    def isFloat32(self, variable):
        return self.__isFloat(variable) \
               and self.__checkRange(variable, -3.402823e+38, 3.402823e+38)

    def isFloat64(self, variable):
        return self.__isFloat(variable) \
               and self.__checkRange(variable, -1.7976931348623158e+308, 1.7976931348623158e+308)

    def isTimestamp(self, variable):
        return self.__isType(variable, [datetime.datetime])

    def isBinary(self, variable, outputCapable=False):
        if outputCapable:
            return self.__isType(variable, [bytearray])
        return self.__isType(variable, [bytes, bytearray])

    def isString(self, variable):
        return self.__isType(variable, [six.string_types])

    def isList(self, variable):
        return self.__isType(variable, [list, tuple])

    def isDict(self, variable):
        return self.__isType(variable, [dict])

    def isType(self, variable, variableType):
        STRING_TYPES_MAP = {
            'bool': TypeCheckMixin.isBool,
            'int8': TypeCheckMixin.isInt8,
            'uint8': TypeCheckMixin.isUint8,
            'int16': TypeCheckMixin.isInt16,
            'uint16': TypeCheckMixin.isUint16,
            'int32': TypeCheckMixin.isInt32,
            'uint32': TypeCheckMixin.isUint32,
            'int64': TypeCheckMixin.isInt64,
            'uint64': TypeCheckMixin.isUint64,
            'float32': TypeCheckMixin.isFloat32,
            'float64': TypeCheckMixin.isFloat64,
            'timestamp': TypeCheckMixin.isTimestamp,
            'datetime': TypeCheckMixin.isTimestamp,
            'str': TypeCheckMixin.isString,
            'text': TypeCheckMixin.isString,
            'unicode': TypeCheckMixin.isString,
            'bytes': TypeCheckMixin.isBinary,
            'bytearray': TypeCheckMixin.isBinary,
            'list': TypeCheckMixin.isList,
            'tuple': TypeCheckMixin.isList,
            'dict': TypeCheckMixin.isDict,
        }
        if variableType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableType]
            return functionToCall(self, variable)
        return False


class TypeDeriveValueMixin(object):

    def getBool(self):
        return False

    def getInt8(self):
        return 0

    def getUint8(self):
        return 0

    def getInt16(self):
        return 0

    def getUint16(self):
        return 0

    def getInt32(self):
        return 0

    def getUint32(self):
        return 0

    def getInt64(self):
        return 0

    def getUint64(self):
        return 0

    def getFloat32(self):
        return 0.0

    def getFloat64(self):
        return 0.0

    def getTimestamp(self):
        return datetime.datetime.utcfromtimestamp(0)

    def getBinary(self):
        return b''

    def getString(self):
        return ''

    def getList(self):
        return []

    def getDict(self):
        return {}

    def getValue(self, variableType):
        STRING_TYPES_MAP = {
            'bool': TypeDeriveValueMixin.getBool,
            'int8': TypeDeriveValueMixin.getInt8,
            'uint8': TypeDeriveValueMixin.getUint8,
            'int16': TypeDeriveValueMixin.getInt16,
            'uint16': TypeDeriveValueMixin.getUint16,
            'int32': TypeDeriveValueMixin.getInt32,
            'uint32': TypeDeriveValueMixin.getUint32,
            'int64': TypeDeriveValueMixin.getInt64,
            'uint64': TypeDeriveValueMixin.getUint64,
            'float32': TypeDeriveValueMixin.getFloat32,
            'float64': TypeDeriveValueMixin.getFloat64,
            'timestamp': TypeDeriveValueMixin.getTimestamp,
            'datetime': TypeDeriveValueMixin.getTimestamp,
            'str': TypeDeriveValueMixin.getString,
            'unicode': TypeDeriveValueMixin.getString,
            'bytes': TypeDeriveValueMixin.getBinary,
            'bytearray': TypeDeriveValueMixin.getBinary,
            'list': TypeDeriveValueMixin.getList,
            'tuple': TypeDeriveValueMixin.getList,
            'dict': TypeDeriveValueMixin.getDict,
        }
        if variableType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableType]
            return functionToCall(self)
        return False


class EntropyUtils(object):

    def getSign(self, value):
        if value >= 0:
            return 0
        return 1

    def getPowerOfTwo(self, power=1):
        if power == long(power) and power >= 0:
            return (long) (1 << power)
        raise ArithmeticError("Only support +ve Integral Powers of Two.")

    def getMaximumUnsigned(self, power=1):
        return self.getPowerOfTwo(power) - 1

    def getComplementaryMaskUnsigned(self, power=1, powerBits = 64):
        assert(powerBits >= power)
        return self.getMaximumUnsigned(powerBits) - self.getMaximumUnsigned(power)


class RawFloatConvertUtils(object):

    def getFloatAsBytes(self, value):
        cFloatValue = ctypes.c_float(value)
        cMemValue = (ctypes.c_byte * 4)()
        ctypes.memmove(cMemValue, ctypes.byref(cFloatValue), 4)
        if sys.byteorder == "little":
            return bytearray(cMemValue)[::-1]
        return bytearray(cMemValue)

    def getBytesAsFloat(self, value):
        if sys.byteorder == "little":
            flippedValue = value[::-1]
        else:
            flippedValue = value
        cMemValue = (ctypes.c_byte * 4)()
        cMemValue[0] = flippedValue[0]
        cMemValue[1] = flippedValue[1]
        cMemValue[2] = flippedValue[2]
        cMemValue[3] = flippedValue[3]
        cFloatValue = ctypes.c_float(0)
        ctypes.memmove(ctypes.byref(cFloatValue), cMemValue, 4)
        return cFloatValue.value

    def getDoubleAsBytes(self, value):
        cDoubleValue = ctypes.c_double(value)
        cMemValue = (ctypes.c_byte * 8)()

        ctypes.memmove(cMemValue, ctypes.byref(cDoubleValue), 8)
        if sys.byteorder == "little":
            return bytearray(cMemValue)[::-1]
        return bytearray(cMemValue)

    def getBytesAsDouble(self, value):
        if sys.byteorder == "little":
            flippedValue = value[::-1]
        else:
            flippedValue = value
        cMemValue = (ctypes.c_byte * 8)()
        cMemValue[0] = flippedValue[0]
        cMemValue[1] = flippedValue[1]
        cMemValue[2] = flippedValue[2]
        cMemValue[3] = flippedValue[3]
        cMemValue[4] = flippedValue[4]
        cMemValue[5] = flippedValue[5]
        cMemValue[6] = flippedValue[6]
        cMemValue[7] = flippedValue[7]
        cDoubleValue = ctypes.c_double(0)
        ctypes.memmove(ctypes.byref(cDoubleValue), cMemValue, 8)
        return cDoubleValue.value


class UTFUtils(EntropyUtils):

    def encodeUTFBytes(self, stringValue):
        stringAsBytes = stringValue.encode('utf-8')
        return stringAsBytes, len(stringAsBytes)


class JsonMixin(TypeCheckMixin):

    def toJson(self):
        return json.dumps(self, default=str)

    def fromJson(self, jsonStr):
        loadedValue = json.loads(jsonStr)
        if self.isDict(loadedValue):
            for key, value in loadedValue.items():
                self.__setattr__(key, value)


class DictMixIn(dict, JsonMixin):

    def __init__(self, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs)
        self.__dict__['__variables'] = OrderedDict()

    def __dir__(self):
        return self.__dict__['__variables'].keys()

    def __str__(self):
        return dict(self.items()).__str__()

    def keys(self):
        return iter(name for name in self.__dict__['__variables'].keys())

    def values(self):
        return iter(value[1] for value in self.__dict__['__variables'].values())

    def items(self):
        return iter((name, value[1]) for name, value in self.__dict__['__variables'].items())

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        return self.__setattr__(name, value)

    def __delitem__(self, name):
        del self.__dict__['__variables'][name]

    def __getattr__(self, name):
        if not name in self.__dict__['__variables']:
            raise AttributeError('Attribute {} does not exist.'.format(name))
        return self.__dict__['__variables'][name][1]

    def getAttribute(self, name):
        return self.__getattr__(name)

    def getAttributeWithType(self, name):
        return self.__dict__['__variables'][name]

    def validateKnownAttribute(self, name, variableType, value, variableSubType = None):
        return value

    def setKnownAttribute(self, name, variableType, value, variableSubType = None):
        value = self.validateKnownAttribute(name, variableType, value, variableSubType)
        self.__dict__['__variables'][name] = [variableType, value, variableSubType]

    def __setattr__(self, name, value):
        if not name in self.__dict__['__variables']:
            variableType = str(type(value).__name__)
            if self.isList(value) and value:
                variableSubType = str(type(value[0]).__name__)
            else:
                variableSubType = None
        else:
            variableType = self.__dict__['__variables'][name][0]
            variableSubType = self.__dict__['__variables'][name][2]
        value = self.validateKnownAttribute(name, variableType, value, variableSubType)
        self.__dict__['__variables'][name] = [variableType, value, variableSubType]

    def setAttribute(self, name, value):
        return self.__setattr__(name, value)

    def toJson(self):
        return json.dumps(dict(self.items()), default=str)


class ColferConstants(object):
    COLFER_MAX_INDEX = 127
    COLFER_MAX_SIZE = 16 * 1024 * 1024
    COLFER_LIST_MAX = 64 * 1024