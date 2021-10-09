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
from cstruct import (define, undef, sizeof, typedef)

class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


class TestCaseDefine(TestCase):

    def test_sizeof(self):
        self.assertEqual(sizeof('int'), 4)
        define('INIT_THREAD_SIZE', 2048 * sizeof('long'))
        self.assertEqual(cstruct.DEFINES['INIT_THREAD_SIZE'], 16384)
        self.assertEqual(sizeof('struct Position'), 3)
        self.assertEqual(sizeof('struct Position'), len(Position))
        self.assertEqual(sizeof(Position), 3)
        self.assertRaises(KeyError, lambda : sizeof('bla'))
        self.assertRaises(KeyError, lambda : sizeof('struct Bla'))

    def test_define(self):
        define('A', 10)
        self.assertEqual(cstruct.DEFINES['A'], 10)
        undef('A')
        self.assertRaises(KeyError, lambda : cstruct.DEFINES['A'])

    def test_typedef(self):
        typedef('int', 'integer')
        self.assertEqual(sizeof('integer'), 4)

if __name__ == '__main__':
    main()

