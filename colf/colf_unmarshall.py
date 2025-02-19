import datetime
from typing import List
import typing

from .colf_base import TypeCheckMixin, RawFloatConvertUtils, IntegerEncodeUtils, UTFUtils, ColferConstants
from .colf_type import Int32, UInt8, UInt16, UInt32, UInt64


class ColferUnmarshallerMixin(TypeCheckMixin, RawFloatConvertUtils, IntegerEncodeUtils, UTFUtils, ColferConstants):

    def unmarshallHeader(self, value, byteInput, offset):
        assert (byteInput[offset] == 0x7f)
        offset += 1
        return value, offset

    def unmarshallInt(self, byteInput, offset, length):
        value = 0
        for index in range(length):
            value = (value << 8) | byteInput[offset]
            offset += 1
        return value, offset

    def unmarshallVarInt(self, byteInput, offset, limit=-1):
        value = 0
        bitShift = 0

        valueAsByte = byteInput[offset]
        offset += 1
        if limit > 0:
            while valueAsByte > 0x7f and limit:
                value |= (valueAsByte & 0x7f) << bitShift
                valueAsByte = byteInput[offset]
                offset += 1
                bitShift += 7
                limit -= 1
        else:
            while valueAsByte > 0x7f:
                value |= (valueAsByte & 0x7f) << bitShift
                valueAsByte = byteInput[offset]
                offset += 1
                bitShift += 7

        value |= (valueAsByte & 0xff) << bitShift

        return value, offset

    def unmarshallBool(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1
        value = True

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallUint8(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1
        value = byteInput[offset]
        offset += 1

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallUint16(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsCompressed = True if byteInput[offset] & 0x80 else False

        offset += 1

        if not indexIsCompressed:
            # Flat - do not use | 0x80. See https://github.com/pascaldekloe/colfer/issues/61
            value, offset = self.unmarshallInt(byteInput, offset, 2)
        else:
            # Compressed Path
            value = byteInput[offset]
            offset += 1

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallInt32(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsSigned = True if byteInput[offset] & 0x80 else False

        offset += 1

        # Compressed Path
        value, offset = self.unmarshallVarInt(byteInput, offset)
        value = -value if indexIsSigned else value

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListInt32(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

        value = []

        for _ in range(valueLength):
            # Compressed Path
            valueElementEncoded, offset = self.unmarshallVarInt(
                byteInput, offset)
            # Move last bit to front
            valueElement = self.decodeInt32(valueElementEncoded)
            # Append to Array
            value.append(valueElement)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallUint32(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsFlat = True if byteInput[offset] & 0x80 else False

        offset += 1

        if indexIsFlat:
            # Flat
            value, offset = self.unmarshallInt(byteInput, offset, 4)
        else:
            # Compressed
            value, offset = self.unmarshallVarInt(byteInput, offset)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallInt64(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsSigned = True if byteInput[offset] & 0x80 else False

        offset += 1

        # Compressed Path
        value, offset = self.unmarshallVarInt(byteInput, offset, 8)
        value = -value if indexIsSigned else value

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListInt64(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)
        value = []

        for _ in range(valueLength):
            # Compressed Path
            valueElementEncoded, offset = self.unmarshallVarInt(
                byteInput, offset, 8)
            # Move last bit to front
            valueElement = self.decodeInt64(valueElementEncoded)
            # Append to Array
            value.append(valueElement)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallUint64(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsFlat = True if byteInput[offset] & 0x80 else False

        offset += 1

        if indexIsFlat:
            # Flat
            value, offset = self.unmarshallInt(byteInput, offset, 8)
        else:
            # Compressed
            value, offset = self.unmarshallVarInt(byteInput, offset)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallFloat32(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Flat
        valueAsBytes = byteInput[offset:offset+4]
        offset += 4
        # Convert
        value = self.getBytesAsFloat(valueAsBytes)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListFloat32(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

        value = []

        for _ in range(valueLength):
            # Flat
            valueAsBytes = byteInput[offset:offset+4]
            offset += 4
            # Convert
            valueElement = self.getBytesAsFloat(valueAsBytes)
            # Append to Array
            value.append(valueElement)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallFloat64(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Flat
        valueAsBytes = byteInput[offset:offset+8]
        offset += 8
        # Convert
        value = self.getBytesAsDouble(valueAsBytes)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListFloat64(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)
        value = []

        for _ in range(valueLength):
            # Flat
            valueAsBytes = byteInput[offset:offset+8]
            offset += 8
            # Convert
            valueElement = self.getBytesAsDouble(valueAsBytes)
            # Append to Array
            value.append(valueElement)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallTimestamp(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        indexIsFlat = True if byteInput[offset] & 0x80 else False

        offset += 1

        if indexIsFlat:
            seconds, offset = self.unmarshallInt(byteInput, offset, 8)
            nanoSeconds, offset = self.unmarshallInt(byteInput, offset, 4)
        else:
            seconds, offset = self.unmarshallInt(byteInput, offset, 4)
            nanoSeconds, offset = self.unmarshallInt(byteInput, offset, 4)

        timeDelta = datetime.timedelta(
            seconds=seconds, microseconds=nanoSeconds//1000)

        value = datetime.datetime.utcfromtimestamp(0) + timeDelta

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallBinary(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

        # Flat
        value = byteInput[offset:offset+valueLength]
        offset += valueLength

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListBinary(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

        value = []
        # Flat
        for _ in range(valueLength):
            # Compressed Path
            valueLength, offset = self.unmarshallVarInt(byteInput, offset)
            assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)
            # Flat
            valueAsBytes = byteInput[offset:offset + valueLength]
            offset += valueLength
            value.append(valueAsBytes)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallString(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

        # Flat
        valueAsBytes = byteInput[offset:offset+valueLength]
        offset += valueLength
        value = self.decodeUTFBytes(valueAsBytes)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListString(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

        value = []
        # Flat
        for _ in range(valueLength):
            # Compressed Path
            valueLength, offset = self.unmarshallVarInt(byteInput, offset)
            assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)
            # Flat
            valueAsBytes = byteInput[offset:offset + valueLength]
            offset += valueLength
            value.append(self.decodeUTFBytes(valueAsBytes))

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallObject(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Flat
        value, offset = type(self)().unmarshall(byteInput, offset)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallListObject(self, index, byteInput, offset):
        if (byteInput[offset] & 0x7f) != index:
            return None, offset

        offset += 1

        # Compressed Path
        valueLength, offset = self.unmarshallVarInt(byteInput, offset)
        assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

        value = []
        # Flat
        for _ in range(valueLength):
            # Flat
            valueAsObject, offset = type(self)().unmarshall(byteInput, offset)
            value.append(valueAsObject)

        return self.unmarshallHeader(value, byteInput, offset)

    def unmarshallList(self, index, byteInput, offset, variableOuterType=None):
        STRING_TYPES_MAP = {
            List[int]: ColferUnmarshallerMixin.unmarshallListInt64,
            List[Int32]: ColferUnmarshallerMixin.unmarshallListInt32,
            List[float]: ColferUnmarshallerMixin.unmarshallListFloat64,
            List[bytes]: ColferUnmarshallerMixin.unmarshallListBinary,
            List[str]: ColferUnmarshallerMixin.unmarshallListString,
        }

        if variableOuterType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableOuterType]
            return functionToCall(self, index, byteInput, offset)
        else:  # pragma: no cover
            return None, offset

    def unmarshallType(self, variableType, variableOuterType, index, byteInput, offset):
        STRING_TYPES_MAP = {
            bool: ColferUnmarshallerMixin.unmarshallBool,
            int: ColferUnmarshallerMixin.unmarshallInt64,
            Int32: ColferUnmarshallerMixin.unmarshallInt32,
            UInt8: ColferUnmarshallerMixin.unmarshallUint8,
            UInt16: ColferUnmarshallerMixin.unmarshallUint16,
            UInt32: ColferUnmarshallerMixin.unmarshallUint32,
            UInt64: ColferUnmarshallerMixin.unmarshallUint64,
            float: ColferUnmarshallerMixin.unmarshallFloat64,
            bytes: ColferUnmarshallerMixin.unmarshallBinary,
            str: ColferUnmarshallerMixin.unmarshallString,
            dict: ColferUnmarshallerMixin.unmarshallObject,
        }
        if type(variableOuterType) == typing._GenericAlias:
            return self.unmarshallList(index, byteInput, offset, variableOuterType)
        if variableType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableType]
            return functionToCall(self, index, byteInput, offset)
        else:  # pragma: no cover
            return None, offset

    def unmarshall(self, byteInput, offset=0):
        assert (byteInput is not None)
        assert (self.isBinary(byteInput))
        assert (offset >= 0)
        index = 0
        for name, modelField in self.__fields__.items():
            variableType = modelField.type_
            variableOuterType = modelField.outer_type_

            newValue, offset = self.unmarshallType(
                variableType, variableOuterType, index, byteInput, offset)
            self.setKnownAttribute(
                name, variableType, newValue, variableOuterType)
            index += 1
        return self, offset

    def getAttributeWithType(self, name):  # pragma: no cover
        value = self.__getattr__(name)
        return None, value, None

    def setKnownAttribute(self, name, variableType, value, variableSubType=None):  # pragma: no cover
        self.__setattr__(name, value)
