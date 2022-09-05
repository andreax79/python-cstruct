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

from cstruct import parse, getdef, define
from cstruct.c_expr import c_eval


def test_c_expr_def():
    parse(
        """
        #define A1  10 /* test */
        #define A2  10 + A1  /* comment */
        #define A3  30
    """
    )
    assert getdef("A1") == 10
    assert getdef('A2') == 20  # TODO
    assert c_eval("A1 / 10") == 1


def test_c_expr_binary():
    assert c_eval("6*2/( 2+1 * 2/3 +6) +8 * (8/4)") == 17
    assert c_eval("6*2/(2+2/3 + 6) + 8 * (8/4)") == 17
    assert c_eval("6*2/(2+0+6) + 8 * (8/4)") == 17
    assert c_eval("((1 + 2) + (3 - 4)) * 10 / 5") == 4
    assert c_eval("12 % 2") == 0
    assert c_eval("64 >> 2") == 16
    assert c_eval("3 & 2") == 2
    assert c_eval("3 | 2") == 3


def test_c_expr_bool():
    assert c_eval("3 && 2") == 1
    assert c_eval("3 && 2 && 1") == 1
    assert c_eval("3 || 2") == 1


def test_c_expr_unary():
    assert c_eval("16 << 2") == 64
    assert c_eval("+123") == 123
    assert c_eval("-123") == -123
    assert c_eval("!100") == -0
    assert c_eval("!0") == 1
    assert c_eval("~0") == -1
    assert c_eval("~1") == -2


def test_c_expr_compare():
    assert c_eval("1 == 2") == 0
    assert c_eval("5 == 5") == 1
    assert c_eval("1 < 2 <= 3") == 1
    assert c_eval("3 > 2 > 1") == 1
    assert c_eval("3 >= 30") == 0
    assert c_eval("3 <= 30") == 1
    define('A10', 10)
    assert c_eval("((A10 < 6) || (A10>10))") == 0
