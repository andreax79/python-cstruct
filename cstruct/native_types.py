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

import struct
from abc import ABCMeta
from typing import Any, Dict, Type, Tuple

__all__ = [
    "get_native_type",
    "AbstractNativeType",
    "Char",
    "SignedChar",
    "UnsignedChar",
    "Short",
    "UnsignedShort",
    "Int",
    "UnsignedInt",
    "Long",
    "UnsignedLong",
    "LongLong",
    "UnsignedLongLong",
    "Float",
    "Double",
    "Pointer",
    "Int8",
    "UnsignedInt8",
    "Int16",
    "UnsignedInt16",
    "Int32",
    "UnsignedInt32",
    "Int64",
    "UnsignedInt64",
]


NATIVE_TYPES: Dict[str, "AbstractNativeType"] = {}


def get_native_type(type_: str) -> "AbstractNativeType":
    """
    Get a base data type by name

    Args:
        type_: data type

    Returns:
        class: data type class

    Raises:
        KeyError: If type is not defined
    """
    try:
        return NATIVE_TYPES[type_]
    except KeyError:
        raise KeyError(f"Unknown type `{type_}`")


class NativeTypeMeta(ABCMeta):
    __size__: int = 0
    " Size in bytes "
    type_name: str = ""
    " Type name "
    native_format: str = ""
    " Type format "

    def __new__(metacls: Type[type], name: str, bases: Tuple[str], namespace: Dict[str, Any]) -> Type[Any]:
        if namespace.get("native_format"):
            native_format = namespace["native_format"]
            namespace["__size__"] = struct.calcsize(native_format)
        else:
            native_format = None
            namespace["native_format"] = None
            namespace["__size__"] = None
        new_class: Type[Any] = super().__new__(metacls, name, bases, namespace)
        if namespace.get("type_name"):
            NATIVE_TYPES[namespace["type_name"]] = new_class
        return new_class

    def __len__(cls) -> int:
        "Type size (in bytes)"
        return cls.__size__

    @property
    def size(cls) -> int:
        "Type size (in bytes)"
        return cls.__size__


class AbstractNativeType(metaclass=NativeTypeMeta):
    def __str__(self) -> str:
        return self.type_name

    @classmethod
    def sizeof(cls) -> int:
        "Type size (in bytes)"
        return cls.__size__


class Char(AbstractNativeType):
    type_name = "char"
    native_format = "s"


class SignedChar(AbstractNativeType):
    type_name = "signed char"
    native_format = "b"


class UnsignedChar(AbstractNativeType):
    type_name = "unsigned char"
    native_format = "B"


class Short(AbstractNativeType):
    type_name = "short"
    native_format = "h"


class UnsignedShort(AbstractNativeType):
    type_name = "unsigned short"
    native_format = "H"


class Int(AbstractNativeType):
    type_name = "int"
    native_format = "i"


class UnsignedInt(AbstractNativeType):
    type_name = "unsigned int"
    native_format = "I"


class Long(AbstractNativeType):
    type_name = "long"
    native_format = "l"


class UnsignedLong(AbstractNativeType):
    type_name = "unsigned long"
    native_format = "L"


class LongLong(AbstractNativeType):
    type_name = "long long"
    native_format = "q"


class UnsignedLongLong(AbstractNativeType):
    type_name = "unsigned long long"
    native_format = "Q"


class Float(AbstractNativeType):
    type_name = "float"
    native_format = "f"


class Double(AbstractNativeType):
    type_name = "double"
    native_format = "d"


class Pointer(AbstractNativeType):
    type_name = "void *"
    native_format = "P"


class Int8(AbstractNativeType):
    type_name = "int8"
    native_format = "b"


class UnsignedInt8(AbstractNativeType):
    type_name = "uint8"
    native_format = "B"


class Int16(AbstractNativeType):
    type_name = "int16"
    native_format = "h"


class UnsignedInt16(AbstractNativeType):
    type_name = "uint16"
    native_format = "H"


class Int32(AbstractNativeType):
    type_name = "int32"
    native_format = "i"


class UnsignedInt32(AbstractNativeType):
    type_name = "uint32"
    native_format = "I"


class Int64(AbstractNativeType):
    type_name = "int64"
    native_format = "q"


class UnsignedInt64(AbstractNativeType):
    type_name = "uint64"
    native_format = "Q"
