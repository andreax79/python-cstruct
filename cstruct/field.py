#!/usr/bin/env python
# Copyright (c) 2013-2019 Andrea Bonomi <andrea.bonomi@gmail.com>
#
# Published under the terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import copy
import struct
from enum import Enum
from typing import Optional, Any, List, Type, TYPE_CHECKING
from .base import NATIVE_ORDER
from .native_types import get_native_type
from .exceptions import ParserError

if TYPE_CHECKING:
    from .abstract import AbstractCStruct

__all__ = ["align", "calculate_padding", "Kind", "FieldType"]


def align(byte_order: Optional[str]) -> bool:
    return byte_order is None or byte_order == NATIVE_ORDER


def calculate_padding(byte_order: Optional[str], alignment: int, pos: int) -> int:
    if align(byte_order):  # calculate the padding
        modulo = pos % alignment
        if modulo:  # not aligned
            return alignment - modulo
    return 0


class Kind(Enum):
    """
    Field type
    """

    NATIVE = 0
    "Native type (e.g. int, char)"
    STRUCT = 1
    "Struct type"
    UNION = 2
    "Union type"
    ENUM = 3
    "Enum type"


class FieldType(object):
    """
    Struct/Union field

    Attributes:
        kind (Kind): struct/union/native
        c_type (str): field type
        ref (AbstractCStruct): struct/union class ref
        vlen (int): number of elements
        flexible_array (bool): True for flexible arrays
        offset (int): relative memory position of the field (relative to the struct)
        padding (int): padding
    """

    def __init__(
        self,
        kind: Kind,
        c_type: str,
        ref: Optional[Type["AbstractCStruct"]],
        vlen: int,
        flexible_array: bool,
        byte_order: Optional[str],
        offset: int,
    ) -> None:
        """
        Initialize a Struct/Union field

        Args:
            kind: struct/union/native
            c_type: field type
            ref: struct/union class ref
            vlen: number of elements
            flexible_array: True for flexible arrays
            offset: relative memory position of the field (relative to the struct)
        """
        self.kind = kind
        self.c_type = c_type
        self.ref = ref
        self.vlen = vlen
        self.flexible_array = flexible_array
        self.byte_order = byte_order
        self.offset = self.base_offset = offset
        self.padding = 0

    def unpack_from(self, buffer: bytes, offset: int = 0) -> Any:
        """
        Unpack bytes containing packed C structure data

        Args:
            buffer: bytes to be unpacked
            offset: optional buffer offset

        Returns:
            data: The unpacked data
        """
        if self.is_native or self.is_enum:
            result = struct.unpack_from(self.fmt, buffer, self.offset + offset)

            if self.is_enum:
                result = tuple(map(self.ref, result))

            if self.is_array:
                return list(result)
            else:
                return result[0]
        else:  # struct/union
            if self.vlen == 1:  # single struct/union
                instance: AbstractCStruct = self.ref()  # type: ignore
                instance.unpack_from(buffer, self.offset + offset)
                return instance
            else:  # multiple struct/union
                instances: List[AbstractCStruct] = []
                for j in range(0, self.vlen):
                    instance: AbstractCStruct = self.ref()  # type: ignore
                    instance.unpack_from(buffer, self.offset + offset + j * instance.size)
                    instances.append(instance)
                return instances

    def pack(self, data: Any) -> bytes:
        """
        Pack the field into bytes

        Args:
            data: data to be packed

        Returns:
            bytes: The packed structure
        """
        if self.flexible_array:
            self.vlen = len(data)  # set flexible array size
            return struct.pack(self.fmt, *data)
        elif self.is_array:
            return struct.pack(self.fmt, *data)
        else:
            return struct.pack(self.fmt, data)

    @property
    def is_array(self) -> bool:
        "True if field is an array/flexible array"
        return self.flexible_array or (not (self.vlen == 1 or self.c_type == "char"))

    @property
    def is_native(self) -> bool:
        "True if the field is a native type (e.g. int, char)"
        return self.kind == Kind.NATIVE

    @property
    def is_enum(self) -> bool:
        "True if the field is an enum"
        return self.kind == Kind.ENUM

    @property
    def is_struct(self) -> bool:
        "True if the field is a struct"
        return self.kind == Kind.STRUCT

    @property
    def is_union(self) -> bool:
        "True if the field is an union"
        return self.kind == Kind.UNION

    @property
    def native_format(self) -> str:
        "Field format (struct library format)"
        if self.is_native:
            try:
                return get_native_type(self.c_type).native_format
            except KeyError:
                raise ParserError(f"Unknow type `{self.c_type}`")
        elif self.is_enum:
            return self.ref.__native_format__
        else:
            return "c"

    @property
    def fmt(self) -> str:
        "Field format prefixed by byte order (struct library format)"
        if self.is_native or self.is_enum:
            fmt = (str(self.vlen) if self.vlen > 1 or self.flexible_array else "") + self.native_format
        else:  # Struct/Union
            fmt = str(self.vlen * self.ref.sizeof()) + self.native_format
        if self.byte_order:
            return self.byte_order + fmt
        else:
            return fmt

    @property
    def vsize(self) -> int:
        "Field size in bytes"
        return struct.calcsize(self.fmt)

    @property
    def alignment(self) -> int:
        "Alignment"
        if self.is_native or self.is_enum:
            if self.byte_order is not None:
                return struct.calcsize(self.byte_order + self.native_format)
            else:
                return struct.calcsize(self.native_format)
        else:  # struct/union
            return self.ref.__alignment__

    def align_filed_offset(self) -> None:
        "If the byte order is native, align the field"
        if align(self.byte_order) and self.c_type != "char":
            self.padding = calculate_padding(self.byte_order, self.alignment, self.base_offset)
            self.offset = self.base_offset + self.padding

    def copy(self) -> "FieldType":
        "Return a shallow copy of this FieldType"
        return copy.copy(self)

    def __repr__(self) -> str:  # pragma: no cover
        return repr(self.__dict__)
