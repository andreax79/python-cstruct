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

from typing import Any, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .abstract import AbstractCStruct, AbstractCEnum

__all__ = [
    "LITTLE_ENDIAN",
    "BIG_ENDIAN",
    "NATIVE_ORDER",
    "CHAR_ZERO",
    "STRUCTS",
    "DEFINES",
    "TYPEDEFS",
    "CHAR_ZERO",
    "DEFAULT_ENUM_SIZE",
]

LITTLE_ENDIAN = "<"
"Little-endian, std. size & alignment"
BIG_ENDIAN = ">"
"Big-endian, std. size & alignment"
NATIVE_ORDER = "@"
"Native order, size & alignment"

STRUCTS: Dict[str, Type["AbstractCStruct"]] = {}

ENUMS: Dict[str, Type["AbstractCEnum"]] = {}

DEFINES: Dict[str, Any] = {}

TYPEDEFS: Dict[str, str] = {
    "short int": "short",
    "unsigned short int": "unsigned short",
    "ushort": "unsigned short",
    "long int": "long",
    "unsigned long int": "unsigned long",
    "int8_t": "int8",
    "uint8_t": "uint8",
    "int16_t": "int16",
    "uint16_t": "uint16",
    "int32_t": "int32",
    "uint32_t": "uint32",
    "int64_t": "int64",
    "uint64_t": "uint64",
}

ENUM_SIZE_TO_C_TYPE: Dict[int, str] = {1: "int8", 2: "int16", 4: "int32", 8: "int64"}

CHAR_ZERO = bytes("\0", "ascii")

DEFAULT_ENUM_SIZE = 4
