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

import pytest

import cstruct
from cstruct import sizeof
from cstruct.exceptions import ParserError

INVALID_ANONYMOUS = """
    struct NestedStruct {
        struct {
          int a;
          int b;
        };
        int a;
        int b;
    };
"""


class NestedStruct(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct NestedStruct {
            struct {
              int a;
              int b;
            } s;
            int a;
            int b;
        };
    """


class NestedUnion(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        union NestedUnion {
            struct {
              int a;
              int b;
            } s;
            int a;
        };
    """


class NestedStructArr(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct NestedStructArr {
            struct b {
              int c;
            } bval[10];
        };
    """


class NestedAnonymousUnion(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        union NestedAnonymousUnion {
            struct {
              int a;
              int b;
            };
            int c;
        };
    """


class Packet(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        #define MaxPacket 20

        struct Packet {
            uint8_t packetLength;
            union {
                uint8_t bytes[MaxPacket];
                struct {
                    uint16_t field1;
                    uint16_t field2;
                    uint16_t field3;
                } format1;
                struct {
                    double value1;
                    double value2;
                } format2;
            };
        };
    """


def test_invalid_anonymous():
    with pytest.raises(ParserError):
        cstruct.parse(INVALID_ANONYMOUS)
    assert True


def test_sizeof_nested_struct():
    assert sizeof("struct NestedStruct") == 16
    o = NestedStruct()
    assert len(o) == 16


def test_pack_unpack_nested_struct():
    o = NestedStruct()
    o.s.a = 1
    o.s.b = 2
    o.a = 10
    o.b = 20
    b = o.pack()
    o1 = NestedStruct()

    o1.unpack(b)
    assert o1.s.a == 1
    assert o1.s.b == 2
    assert o1.a == 10
    assert o1.b == 20


def test_sizeof_nested_union():
    assert sizeof("struct NestedUnion") == 8
    o = NestedUnion()
    assert len(o) == 8


def test_pack_unpack_nested_union():
    o = NestedUnion()
    o.s.a = 1
    o.s.b = 2
    b = o.pack()

    o1 = NestedUnion()
    o1.unpack(b)
    assert o1.s.a == 1
    assert o1.s.b == 2

    o = NestedUnion()
    o.a = 1979
    b = o.pack()

    o1 = NestedUnion()
    o1.unpack(b)
    assert o1.a == 1979
    o1.s.b = 0
    assert o1.a == 1979
    o1.s.a = 0
    assert o1.a == 0


def test_sizeof_nested_anonymous_union():
    assert sizeof("struct NestedAnonymousUnion") == 8
    o = NestedAnonymousUnion()
    assert len(o) == 8


def test_pack_unpack_nested_anonymous_union():
    o = NestedAnonymousUnion()
    o.a = 1
    o.b = 2
    b = o.pack()

    o1 = NestedAnonymousUnion()
    o1.unpack(b)
    assert o1.a == 1
    assert o1.b == 2

    o = NestedAnonymousUnion()
    o.c = 1979
    b = o.pack()

    o1 = NestedAnonymousUnion()
    o1.unpack(b)
    assert o1.c == 1979
    o1.b = 0
    assert o1.c == 1979
    o1.a = 0
    assert o1.c == 0


def test_nested_anonymous_union_struct():
    o = Packet()
    assert sizeof("struct Packet") == len(o)

    o = Packet()
    o.packetLength = 10
    o.format1.field1 = 11
    o.format1.field2 = 12
    o.format1.field3 = 13
    b = o.pack()

    o1 = Packet()
    o1.unpack(b)
    assert o1.format1.field1 == 11
    assert o1.format1.field2 == 12
    assert o1.format1.field3 == 13


def test_nested_struct_offset():
    cstruct.parse(
        """
        struct op_a {
          int a;
        };

        struct op_b {
          char a;
          char b;
          char c;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )

    Op = cstruct.parse(
        """
        struct op {
          char preamble[10];
          uint64_t magic;
          union {
            struct op_a a_op;
            struct op_b b_op;
          } u1;
          struct op_a aaa;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )

    o = Op()
    o.preamble = b'ciao_ciao'
    o.magic = 3771778641802345472
    o.u1.a_op.a = 2022
    o.aaa.a = 0x33333333
    assert o.u1.b_op.a == b'\xe6'
    assert o.u1.b_op.b == b'\x07'
    assert o.u1.b_op.c == b'\x00'
    assert o.__base__ == 0
    assert o.u1.__base__ >= 10
    assert o.u1.__base__ == o.u1.a_op.__base__
    assert o.u1.__base__ == o.u1.b_op.__base__
    assert o.aaa.__base__ > o.u1.__base__
    assert o.pack() == b'ciao_ciao\x00\x00\xbc\x08\xe4\xb0\x0cX4\xe6\x07\x00\x003333'
    assert o.u1.pack() == b'\xe6\x07\x00\x00'
    assert o.aaa.pack() == b'3333'
    assert o.u1.a_op.inspect() == "00000000  e6 07 00 00                                       |....            |\n"
    assert o.u1.b_op.inspect() == "00000000  e6 07 00                                          |...             |\n"


def test_nested_anonymous_struct_offset():
    cstruct.parse(
        """
        struct op_a1 {
          int a;
        };

        struct op_b1 {
          char a;
          char b;
          char c;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )

    Opu = cstruct.parse(
        """
        struct opu {
          char preamble[10];
          uint64_t magic;
          union {
            struct op_a1 a_op;
            struct op_b1 b_op;
          };
          struct op_a aaa;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )

    o = Opu()
    o.preamble = b'ciao_ciao'
    o.magic = 3771778641802345472
    o.__anonymous0.a_op.a = 2022
    o.aaa.a = 0x33333333
    assert o.__anonymous0.b_op.a == b'\xe6'
    assert o.__anonymous0.b_op.b == b'\x07'
    assert o.__anonymous0.b_op.c == b'\x00'
    assert o.__base__ == 0
    assert o.__anonymous0.__base__ >= 10
    assert o.__anonymous0.__base__ == o.__anonymous0.a_op.__base__
    assert o.__anonymous0.__base__ == o.__anonymous0.b_op.__base__
    assert o.aaa.__base__ > o.__anonymous0.__base__
    assert o.pack() == b'ciao_ciao\x00\x00\xbc\x08\xe4\xb0\x0cX4\xe6\x07\x00\x003333'
    assert o.__anonymous0.pack() == b'\xe6\x07\x00\x00'
    assert o.aaa.pack() == b'3333'
    assert o.__anonymous0.inspect() == "00000000  e6 07 00 00                                       |....            |\n"
    assert o.__anonymous0.a_op.inspect() == "00000000  e6 07 00 00                                       |....            |\n"
    assert o.__anonymous0.b_op.inspect() == "00000000  e6 07 00                                          |...             |\n"

    o = Opu()
    o.preamble = b'ciao_ciao'
    o.magic = 3771778641802345472
    o.a_op.a = 2022
    o.aaa.a = 0x33333333
    assert o.b_op.a == b'\xe6'
    assert o.b_op.b == b'\x07'
    assert o.b_op.c == b'\x00'
    assert o.__base__ == 0
    assert o.__anonymous0.__base__ >= 10
    assert o.__anonymous0.__base__ == o.a_op.__base__
    assert o.__anonymous0.__base__ == o.b_op.__base__
    assert o.aaa.__base__ > o.__base__
    assert o.pack() == b'ciao_ciao\x00\x00\xbc\x08\xe4\xb0\x0cX4\xe6\x07\x00\x003333'
    assert o.a_op.pack() == b'\xe6\x07\x00\x00'
    assert o.aaa.pack() == b'3333'
    assert o.a_op.inspect() == "00000000  e6 07 00 00                                       |....            |\n"
    assert o.b_op.inspect() == "00000000  e6 07 00                                          |...             |\n"


def test_nested_struct_array():
    Nested = cstruct.parse(
        """
        struct Nested {
          struct b {
           int c;
          } bval;
          int a;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )
    assert len(Nested) == 8
    t = Nested()
    assert "a" in t.__fields_types__
    assert "bval" in t.__fields_types__

    NestedArray = cstruct.parse(
        """
        struct NestedArray {
          struct b {
           int c;
          } bval[2];
          int a;
        };
    """,
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )
    t = NestedArray()
    assert "a" in t.__fields_types__
    assert "bval" in t.__fields_types__
    assert len(NestedArray) > len(Nested)
    t.bval[0].c = 10
    t.bval[1].c = 11
    assert t.bval[0].c == 10
    assert t.bval[1].c == 11
    assert len(t.bval) == 2

    assert len(NestedStructArr) == 40
    t = NestedStructArr()
    assert "bval" in t.__fields_types__
    t.bval[0].c = 10
    t.bval[1].c = 11
    assert t.bval[0].c == 10
    assert t.bval[1].c == 11
    assert len(t.bval) == 10
