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


def test_get_type():
    S2 = cstruct.parse(
        """
        #define ACTIVE_FLAG         0x80

        struct S1 {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        };
        typedef struct S1 S1;

        union U1 {
            unsigned int a;
            float b;
        };
        typedef union U1 U1type;

        #define NONE         0

        enum htmlfont {
            HTMLFONT_NONE = NONE,
            HTMLFONT_BOLD,
            HTMLFONT_ITALIC,
        };

        struct S2 {
            unsigned char status;       /* 0x80 - active */
            struct S1 start;
            unsigned char partition_type;
            S1 end;
        };

        typedef struct S2 S2type;
    """
    )
    assert S2
    assert cstruct.get_type("struct S1")
    assert cstruct.get_type("S1")
    assert cstruct.get_type("union U1")
    assert cstruct.get_type("U1type")
    assert cstruct.get_type("enum htmlfont")
    assert cstruct.get_type("struct S2")
    assert cstruct.get_type("int")
    assert cstruct.get_type("unsigned int")
    assert cstruct.get_type("long long")
    with pytest.raises(KeyError):
        cstruct.get_type("struct X")
    with pytest.raises(KeyError):
        cstruct.get_type("U1")
    assert cstruct.sizeof("union U1") == max(cstruct.sizeof("unsigned int"), cstruct.sizeof("float"))
