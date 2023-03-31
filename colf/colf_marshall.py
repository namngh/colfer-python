import datetime
from typing import List
import typing

from .colf_base import TypeCheckMixin, RawFloatConvertUtils, IntegerEncodeUtils, UTFUtils, ColferConstants
from .colf_type import Int32, UInt8, UInt16, UInt32, UInt64


class ColferMarshallerMixin(TypeCheckMixin, RawFloatConvertUtils, IntegerEncodeUtils, UTFUtils, ColferConstants):

    def marshallHeader(self, byteOutput, offset):
        byteOutput[offset] = 0x7f
        offset += 1
        return offset

    def marshallInt(self, value, byteOutput, offset, length):
        for index in range(1, length+1):
            byteOutput[offset+(length-index)] = value & 0xff
            value >>= 8
        return offset+length

    def marshallVarInt(self, value, byteOutput, offset, limit=-1):
        if limit > 0:
            while value > 0x7f and limit:
                byteOutput[offset] = (value & 0x7f) | 0x80
                offset += 1
                value >>= 7
                limit -= 1
        else:
            while value > 0x7f:
                byteOutput[offset] = (value & 0x7f) | 0x80
                offset += 1
                value >>= 7
        byteOutput[offset] = value & 0xff
        offset += 1
        return offset

    def marshallBool(self, value, index, byteOutput, offset):

        if value:
            byteOutput[offset] = index
            offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallUint8(self, value, index, byteOutput, offset):

        if value != 0:
            byteOutput[offset] = index
            offset += 1
            byteOutput[offset] = int.from_bytes(value, "little")
            offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallUint16(self, value, index, byteOutput, offset):
        if value != 0:

            if (value & self.getComplementaryMaskUnsigned(8, 16)) != 0:
                # Flat - do not use | 0x80. See https://github.com/pascaldekloe/colfer/issues/61
                byteOutput[offset] = index
                offset += 1
                offset = self.marshallInt(int.from_bytes(
                    value, "little"), byteOutput, offset, 2)
            else:
                # Compressed Path
                byteOutput[offset] = (index | 0x80)
                offset += 1
                byteOutput[offset] = int.from_bytes(value, "little")
                offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallInt32(self, value, index, byteOutput, offset):
        if value != 0:

            if value < 0:
                value = -value
                byteOutput[offset] = (index | 0x80)
                offset += 1
            else:
                byteOutput[offset] = index
                offset += 1

            # Compressed Path
            offset = self.marshallVarInt(int.from_bytes(
                value, "little"), byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallListInt32(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            for valueElement in value:
                # Move last bit to the end
                valueElementEncoded = self.encodeInt32(valueElement)
                # Compressed Path
                offset = self.marshallVarInt(
                    valueElementEncoded, byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallUint32(self, value, index, byteOutput, offset):

        if value != 0:
            if (value & self.getComplementaryMaskUnsigned(21, 32)) != 0:
                # Flat
                byteOutput[offset] = index | 0x80
                offset += 1
                offset = self.marshallInt(int.from_bytes(
                    value, "little"), byteOutput, offset, 4)
            else:
                # Compressed Path
                byteOutput[offset] = index
                offset += 1
                offset = self.marshallVarInt(int.from_bytes(
                    value, "little"), byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallInt64(self, value, index, byteOutput, offset):
        if value != 0:

            if value < 0:
                value = -value
                byteOutput[offset] = (index | 0x80)
                offset += 1
            else:
                byteOutput[offset] = index
                offset += 1

            # Compressed Path
            offset = self.marshallVarInt(value, byteOutput, offset, 8)

        return self.marshallHeader(byteOutput, offset)

    def marshallListInt64(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            for valueElement in value:
                # Move last bit to the end
                valueElementEncoded = self.encodeInt64(valueElement)
                # Compressed Path
                offset = self.marshallVarInt(
                    valueElementEncoded, byteOutput, offset, 8)

        return self.marshallHeader(byteOutput, offset)

    def marshallUint64(self, value, index, byteOutput, offset):
        if value != 0:
            if (value & self.getComplementaryMaskUnsigned(49)) != 0:
                # Flat
                byteOutput[offset] = index | 0x80
                offset += 1
                offset = self.marshallInt(int.from_bytes(
                    value, "little"), byteOutput, offset, 8)
            else:
                # Compressed Path
                byteOutput[offset] = index
                offset += 1
                offset = self.marshallVarInt(int.from_bytes(
                    value, "little"), byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallFloat32(self, value, index, byteOutput, offset):
        if value != 0:
            byteOutput[offset] = index
            offset += 1
            # Convert
            valueAsBytes = self.getFloatAsBytes(value)
            # Flat
            for valueAsByte in valueAsBytes:
                byteOutput[offset] = valueAsByte
                offset += 1
        return self.marshallHeader(byteOutput, offset)

    def marshallListFloat32(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            for valueElement in value:
                # Convert
                valueAsBytes = self.getFloatAsBytes(valueElement)
                # Flat
                for valueAsByte in valueAsBytes:
                    byteOutput[offset] = valueAsByte
                    offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallFloat64(self, value, index, byteOutput, offset):
        if value != 0:
            byteOutput[offset] = index
            offset += 1
            # Convert
            valueAsBytes = self.getDoubleAsBytes(value)
            # Flat
            for valueAsByte in valueAsBytes:
                byteOutput[offset] = valueAsByte
                offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallListFloat64(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            for valueElement in value:
                # Convert
                valueAsBytes = self.getDoubleAsBytes(valueElement)
                # Flat
                for valueAsByte in valueAsBytes:
                    byteOutput[offset] = valueAsByte
                    offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallTimestamp(self, value, index, byteOutput, offset):
        timeDelta = value - datetime.datetime.utcfromtimestamp(0)
        nanoSeconds = timeDelta.microseconds * (10**3)
        seconds = timeDelta.seconds + (timeDelta.days * 24 * 3600)
        if nanoSeconds != 0 or seconds != 0:
            if (seconds & self.getComplementaryMaskUnsigned(32)) != 0:
                # Flat
                byteOutput[offset] += index | 0x80
                offset += 1
                offset = self.marshallInt(seconds, byteOutput, offset, 8)
                offset = self.marshallInt(nanoSeconds, byteOutput, offset, 4)
            else:
                # Compressed Path
                byteOutput[offset] += index
                offset += 1
                offset = self.marshallInt(seconds, byteOutput, offset, 4)
                offset = self.marshallInt(nanoSeconds, byteOutput, offset, 4)

        return self.marshallHeader(byteOutput, offset)

    def marshallBinary(self, value, index, byteOutput, offset):
        valueLength = len(value)
        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

            # Compressed Path
            byteOutput[offset] = index
            offset += 1
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            # Flat
            for valueAsByte in value:
                byteOutput[offset] = valueAsByte
                offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallListBinary(self, value, index, byteOutput, offset):
        valueLength = len(value)
        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            # Compressed Path
            byteOutput[offset] = index
            offset += 1
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            # Flat
            for valueAsBytes in value:
                valueLength = len(valueAsBytes)
                assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

                # Compressed Path
                offset = self.marshallVarInt(valueLength, byteOutput, offset)

                # Flat
                for valueAsByte in valueAsBytes:
                    byteOutput[offset] = valueAsByte
                    offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallString(self, value, index, byteOutput, offset):
        valueLength = len(value)
        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

            # Compressed Path
            byteOutput[offset] = index
            offset += 1

            valueAsBytes, valueLength = self.encodeUTFBytes(value)
            assert (valueLength <= self.COLFER_MAX_SIZE)

            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            # Flat
            for valueAsByte in valueAsBytes:
                byteOutput[offset] = valueAsByte
                offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallListString(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            # Flat
            for valueAsString in value:
                valueLength = len(valueAsString)
                assert (valueLength <= ColferConstants.COLFER_MAX_SIZE)

                valueAsBytes, valueLength = self.encodeUTFBytes(valueAsString)
                assert (valueLength <= self.COLFER_MAX_SIZE)

                # Compressed Path
                offset = self.marshallVarInt(valueLength, byteOutput, offset)

                # Flat
                for valueAsByte in valueAsBytes:
                    byteOutput[offset] = valueAsByte
                    offset += 1

        return self.marshallHeader(byteOutput, offset)

    def marshallObject(self, value, index, byteOutput, offset):
        if value != None:
            byteOutput[offset] = index
            offset += 1

            # Flat
            offset = value.marshall(byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallListObject(self, value, index, byteOutput, offset):
        valueLength = len(value)

        if valueLength != 0:
            assert (valueLength <= ColferConstants.COLFER_LIST_MAX)

            byteOutput[offset] = index
            offset += 1

            # Compressed Path
            offset = self.marshallVarInt(valueLength, byteOutput, offset)

            # Flat
            for valueAsObject in value:
                # Flat
                offset = valueAsObject.marshall(byteOutput, offset)

        return self.marshallHeader(byteOutput, offset)

    def marshallList(self, value, index, byteOutput, offset, variableOuterType=None):
        STRING_TYPES_MAP = {
            List[int]: ColferMarshallerMixin.marshallListInt64,
            List[Int32]: ColferMarshallerMixin.marshallListInt32,
            List[float]: ColferMarshallerMixin.marshallListFloat64,
            List[bytes]: ColferMarshallerMixin.marshallListBinary,
            List[str]: ColferMarshallerMixin.marshallListString,
        }

        if variableOuterType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableOuterType]
            return functionToCall(self, value, index, byteOutput, offset)
        else:  # pragma: no cover
            return offset

    def marshallType(self, variableType, variableOuterType, value, index, byteOutput, offset):
        STRING_TYPES_MAP = {
            bool: ColferMarshallerMixin.marshallBool,
            int: ColferMarshallerMixin.marshallInt64,
            Int32: ColferMarshallerMixin.marshallInt32,
            UInt8: ColferMarshallerMixin.marshallUint8,
            UInt16: ColferMarshallerMixin.marshallUint16,
            UInt32: ColferMarshallerMixin.marshallUint32,
            UInt64: ColferMarshallerMixin.marshallUint64,
            float: ColferMarshallerMixin.marshallFloat64,
            bytes: ColferMarshallerMixin.marshallBinary,
            str: ColferMarshallerMixin.marshallString,
            dict: ColferMarshallerMixin.marshallObject,
        }

        if type(variableOuterType) == typing._GenericAlias:
            return self.marshallList(value, index, byteOutput,
                                     offset, variableOuterType)
        if variableType in STRING_TYPES_MAP:
            functionToCall = STRING_TYPES_MAP[variableType]
            return functionToCall(self, value, index, byteOutput, offset)
        else:  # pragma: no cover
            return offset

    def marshall(self, byteOutput, offset=0):
        assert (byteOutput != None)
        assert (self.isBinary(byteOutput, True))
        assert (offset >= 0)
        index = 0
        for name, modelField in self.__fields__.items():
            variableType = modelField.type_
            variableOuterType = modelField.outer_type_
            value = getattr(self, name)

            offset = self.marshallType(
                variableType, variableOuterType, value, index, byteOutput, offset)
            index += 1
        return offset
