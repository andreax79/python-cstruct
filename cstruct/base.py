#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

from typing import Any, Dict, Type

__all__ = [
    'LITTLE_ENDIAN',
    'BIG_ENDIAN',
    'NATIVE_ORDER',
    'CHAR_ZERO',
    'STRUCTS',
    'DEFINES',
    'TYPEDEFS',
    'C_TYPE_TO_FORMAT',
    'EMPTY_BYTES_STRING',
    'CHAR_ZERO',
]

# little-endian, std. size & alignment
LITTLE_ENDIAN = '<'
# big-endian, std. size & alignment
BIG_ENDIAN = '>'
# native order, size & alignment
NATIVE_ORDER = '@'

STRUCTS: Dict[str, Type[Any]] = {}

DEFINES: Dict[str, Any] = {}

TYPEDEFS: Dict[str, str] = {
    'short int': 'short',
    'unsigned short int': 'unsigned short',
    'ushort': 'unsigned short',
    'long int': 'long',
    'unsigned long int': 'unsigned long',
    'int8_t': 'int8',
    'uint8_t': 'uint8',
    'int16_t': 'int16',
    'uint16_t': 'uint16',
    'int32_t': 'int32',
    'uint32_t': 'uint32',
    'int64_t': 'int64',
    'uint64_t': 'uint64',
}

C_TYPE_TO_FORMAT: Dict[str, str] = {
    'char': 's',
    'signed char': 'b',
    'unsigned char': 'B',
    'short': 'h',
    'unsigned short': 'H',
    'int': 'i',
    'unsigned int': 'I',
    'long': 'l',
    'unsigned long': 'L',
    'long long': 'q',
    'unsigned long long': 'Q',
    'float': 'f',
    'double': 'd',
    'void *': 'P',
    'int8': 'b',
    'uint8': 'B',
    'int16': 'h',
    'uint16': 'H',
    'int32': 'i',
    'uint32': 'I',
    'int64': 'q',
    'uint64': 'Q',
}

EMPTY_BYTES_STRING = bytes()
CHAR_ZERO = bytes('\0', 'ascii')
