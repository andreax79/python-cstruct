#!/usr/bin/env python
#*****************************************************************************
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
#*****************************************************************************

from unittest import TestCase, main
import cstruct
import struct

class TestUnion(cstruct.CStruct):
    __is_union__ = True
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        uint8   a;
        uint8   a1;
        uint16  b;
        uint32  c;
        struct Partition d;
        struct Partition e[4];
    """

# class RCU_Special(cstruct.CStruct):
#     __union__ = """
#         struct {
#                 uint8                      blocked;
#                 uint8                      need_qs;
#                 uint8                      exp_hint; /* Hint for performance. */
#                 uint8                      deferred_qs;
#         } b; /* Bits. */
#         uint32 s; /* Set of bits. */
#     """

class TestCaseUnion(TestCase):

    def test_union_unpack(self):
        union = TestUnion()
        union.unpack(None)
        self.assertEqual(union.a, 0)
        self.assertEqual(union.a1, 0)
        self.assertEqual(union.b, 0)
        self.assertEqual(union.c, 0)
        union.unpack(struct.pack('b', 10) + cstruct.CHAR_ZERO * union.size)
        self.assertEqual(union.a, 10)
        self.assertEqual(union.a1, 10)
        self.assertEqual(union.b, 10)
        self.assertEqual(union.c, 10)
        union.unpack(struct.pack('h', 1979) + cstruct.CHAR_ZERO * union.size)
        self.assertEqual(union.a, 187)
        self.assertEqual(union.a1, 187)
        self.assertEqual(union.b, 1979)
        self.assertEqual(union.c, 1979)

if __name__ == '__main__':
    main()

