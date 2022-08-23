#!/usr/bin/env python
# *****************************************************************************
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
# *****************************************************************************

import cstruct
from cstruct import sizeof
import struct


class Position(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


class Partition(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char status;       /* 0x80 - active */
            struct Position start;
            unsigned char partition_type;
            struct Position end;
            unsigned int start_sect;    /* starting sector counting from 0 */
            unsigned int sectors;       // nr of sectors in partition
        }
    """


class UnionT1(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        union {
            uint8   a;
            uint8   a1;
            uint16  b;
            uint32  c;
            struct Partition d;
            struct Partition e[4];
        }
    """


def test_sizeof():
    assert sizeof('struct UnionT1') == 64
    s = UnionT1()
    assert len(s) == 64


def test_union_unpack():
    union = UnionT1()
    union.unpack(None)
    assert union.a == 0
    assert union.a1 == 0
    assert union.b == 0
    assert union.c == 0
    union.unpack(struct.pack('b', 10) + cstruct.CHAR_ZERO * union.size)
    assert union.a == 10
    assert union.a1 == 10
    assert union.b == 10
    assert union.c == 10
    union.unpack(struct.pack('h', 1979) + cstruct.CHAR_ZERO * union.size)
    assert union.a == 187
    assert union.a1 == 187
    assert union.b == 1979
    assert union.c == 1979
    print(union)
    union2 = UnionT1(union.pack())
    print(union2)
    assert len(union) == len(union2)
    assert union2.a == 187
    assert union2.a1 == 187
    assert union2.b == 1979
    assert union2.c == 1979
