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


class Pkg(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t cmd;
            uint16_t length;
            uint8_t data[];
        }
    """


class MemPkg(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t cmd;
            uint16_t length;
            uint8_t data[];
        }
    """


def test_len():
    pkg = Pkg()
    assert len(pkg) == sizeof('uint16_t') * 2
    assert len(pkg.pack())
    assert len(pkg) == sizeof('uint16_t') * 2
    assert pkg.sizeof() == sizeof('uint16_t') * 2
    assert pkg.__size__ == sizeof('uint16_t') * 2

    pkg.length = 10
    pkg.data = list(range(pkg.length))
    assert len(pkg.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert len(pkg) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert pkg.sizeof() == sizeof('uint16_t') * 2
    assert pkg.__size__ == sizeof('uint16_t') * 2

    pkg2 = Pkg()
    pkg2.length = 20
    pkg2.data = list(range(pkg2.length))
    assert len(pkg2.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg2.length)
    assert len(pkg2) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg2.length)
    assert pkg2.sizeof() == sizeof('uint16_t') * 2
    assert pkg2.__size__ == sizeof('uint16_t') * 2
    assert len(pkg) != len(pkg2)


def test_pack_unpack():
    pkg = Pkg()
    pkg.cmd = 5
    pkg.length = 10
    assert pkg.__fields_types__['data'].vlen == 0
    assert pkg.__fields_types__['data'].vsize == 0
    assert len(pkg) == sizeof('uint16_t') * 2
    pkg.data = list(range(pkg.length))
    assert len(pkg.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert pkg.__fields_types__['data'].vlen == pkg.length
    assert pkg.__fields_types__['data'].vsize == (sizeof('uint8_t') * pkg.length)
    assert len(pkg.data) == pkg.length
    data = pkg.pack()

    pkg2 = Pkg()
    assert pkg2.__fields_types__['data'].vlen == 0
    pkg2.unpack(data, flexible_array_length=pkg.length)
    assert pkg2.__fields_types__['data'].vlen == pkg2.length
    assert pkg2.cmd == pkg.cmd
    assert pkg2.length == pkg.length
    assert pkg2.data == pkg.data
    assert len(pkg2.data) == len(pkg.data)

    pkg3 = Pkg(data, flexible_array_length=pkg.length)
    assert pkg3.cmd == pkg.cmd
    assert pkg3.length == pkg.length
    assert len(pkg3.data) == len(pkg.data)
    assert pkg3.data == pkg.data


def test_mem_len():
    pkg = MemPkg()
    assert len(pkg) == sizeof('uint16_t') * 2
    assert len(pkg.pack())
    assert len(pkg) == sizeof('uint16_t') * 2
    assert pkg.sizeof() == sizeof('uint16_t') * 2
    assert pkg.__size__ == sizeof('uint16_t') * 2

    pkg.length = 10
    pkg.data = list(range(pkg.length))
    assert len(pkg.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert len(pkg) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert pkg.sizeof() == sizeof('uint16_t') * 2
    assert pkg.__size__ == sizeof('uint16_t') * 2

    pkg.length = 5
    pkg.data = list(range(pkg.length))
    assert len(pkg.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert len(pkg) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert pkg.sizeof() == sizeof('uint16_t') * 2
    assert pkg.__size__ == sizeof('uint16_t') * 2

    pkg2 = MemPkg()
    pkg2.length = 20
    pkg2.data = list(range(pkg2.length))
    assert len(pkg2.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg2.length)
    assert len(pkg2) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg2.length)
    assert pkg2.sizeof() == sizeof('uint16_t') * 2
    assert pkg2.__size__ == sizeof('uint16_t') * 2
    assert len(pkg) != len(pkg2)


def test_mem_pack_unpack():
    pkg = MemPkg()
    pkg.cmd = 5
    pkg.length = 10
    assert pkg.__fields_types__['data'].vlen == 0
    assert pkg.__fields_types__['data'].vsize == 0
    assert len(pkg) == sizeof('uint16_t') * 2
    pkg.data = list(range(pkg.length))
    assert len(pkg.pack()) == (sizeof('uint16_t') * 2) + (sizeof('uint8_t') * pkg.length)
    assert pkg.__fields_types__['data'].vlen == pkg.length
    assert pkg.__fields_types__['data'].vsize == (sizeof('uint8_t') * pkg.length)
    assert len(pkg.data) == pkg.length
    data = pkg.pack()

    pkg2 = MemPkg()
    assert pkg2.__fields_types__['data'].vlen == 0
    pkg2.unpack(data, flexible_array_length=pkg.length)
    assert pkg2.__fields_types__['data'].vlen == pkg2.length
    assert pkg2.cmd == pkg.cmd
    assert pkg2.length == pkg.length
    assert pkg2.data == pkg.data
    assert len(pkg2.data) == len(pkg.data)

    pkg3 = MemPkg(data, flexible_array_length=pkg.length)
    assert pkg3.cmd == pkg.cmd
    assert pkg3.length == pkg.length
    assert len(pkg3.data) == len(pkg.data)
    assert pkg3.data == pkg.data
