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

import sys

__all__ = [
    'STRUCTS',
    'DEFINES',
    'TYPEDEFS',
    'C_TYPE_TO_FORMAT',
    'EMPTY_BYTES_STRING',
    'CHAR_ZERO'
]

STRUCTS = {
}

DEFINES = {
}

TYPEDEFS = {
}

C_TYPE_TO_FORMAT = {
    'char':                 's',
    'signed char':          'b',
    'unsigned char':        'B',
    'short':                'h',
    'short int':            'h',
    'ushort':               'H',
    'unsigned short':       'H',
    'unsigned short int':   'H',
    'int':                  'i',
    'unsigned int':         'I',
    'long':                 'l',
    'long int':             'l',
    'unsigned long':        'L',
    'unsigned long int':    'L',
    'long long':            'q',
    'unsigned long long':   'Q',
    'float':                'f',
    'double':               'd',
    'void *':               'P',
    'int8':                 'b',
    'int8_t':               'b',
    'uint8':                'B',
    'uint8_t':              'B',
    'int16':                'h',
    'int16_t':              'h',
    'uint16':               'H',
    'uint16_t':             'H',
    'int32':                'i',
    'int32_t':              'i',
    'uint32':               'I',
    'uint32_t':             'I',
    'int64':                'q',
    'int64_t':              'q',
    'uint64':               'Q',
    'uint64_t':             'Q',
}

EMPTY_BYTES_STRING = bytes()
CHAR_ZERO = bytes('\0', 'ascii') if sys.version_info >= (3, 0) else bytes('\0')

