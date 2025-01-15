#!/usr/bin/env python
# *****************************************************************************
#
# Copyright (c) 2013-2025 Andrea Bonomi <andrea.bonomi@gmail.com>
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
from cstruct.c_expr import c_eval


class Struct0(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t a;
            uint16_t b;
            char c[6];
        }
    """


class Struct1(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        #define X1 6
        struct {
            uint16_t a;
            uint16_t b;
            char c[X1];
        }
    """


class Struct2(cstruct.CStruct):
    c_len: int = 6

    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t a;
            uint16_t b;
            char c[self.c_len];
        }
    """


class Struct3(cstruct.MemCStruct):
    c_len: int = 0

    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t a;
            uint16_t b;
            uint16_t c[self.c_len];
        }
    """


def test_v():
    assert c_eval('10') == 10

    s0 = Struct0()
    assert len(s0) == 10
    s1 = Struct1()
    assert len(s1) == 10

    assert sizeof(Struct2) == 4

    s2 = Struct2()
    assert len(s2) == 10
    s2.c_len = 10
    assert len(s2) == 14

    for i in range(10):
        s2.c_len = i
        assert len(s2) == 4 + i

    assert sizeof(Struct3) == 4
    s3 = Struct3()
    assert len(s3) == 4

    for i in range(10):
        s3.c_len = i
        assert len(s3) == 4 + i * 2
