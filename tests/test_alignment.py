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

from cstruct import sizeof, typedef, define, CStruct, NATIVE_ORDER

define("UT_NAMESIZE", 32)
define("UT_LINESIZE", 32)
define("UT_HOSTSIZE", 256)

typedef("int", "pid_t")
typedef("long", "time_t")


class ExitStatus(CStruct):
    __def__ = """
        struct {
            short   e_termination;      /* Process termination status.  */
            short   e_exit;             /* Process exit status.  */
        }
    """


class Timeval(CStruct):
    __def__ = """
        struct {
            int32_t tv_sec;             /* Seconds.  */
            int32_t tv_usec;            /* Microseconds.  */
        }
    """


class Utmp(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            short   ut_type;              /* Type of record */
            pid_t   ut_pid;               /* PID of login process */
            char    ut_line[UT_LINESIZE]; /* Device name of tty - "/dev/" */
            char    ut_id[4];             /* Terminal name suffix, or inittab(5) ID */
            char    ut_user[UT_NAMESIZE]; /* Username */
            char    ut_host[UT_HOSTSIZE]; /* Hostname for remote login, or kernel version for run-level messages */
            struct  ExitStatus ut_exit;   /* Exit status of a process marked as DEAD_PROCESS; not used by Linux init (1 */
            int32_t ut_session;           /* Session ID (getsid(2)), used for windowing */
            struct {
               int32_t tv_sec;            /* Seconds */
               int32_t tv_usec;           /* Microseconds */
            } ut_tv;                      /* Time entry was made */
            int32_t ut_addr_v6[4];        /* Internet address of remote host; IPv4 address uses just ut_addr_v6[0] */
            char __unused[20];            /* Reserved for future use */
        }
    """


class AllTypes(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            char                x00;
            signed char         x01;
            unsigned char       x02;
            short               x03;
            short int           x04;
            ushort              x05;
            unsigned short      x06;
            unsigned short int  x07;
            int                 x08;
            unsigned int        x09;
            long                x10;
            long int            x11;
            unsigned long       x12;
            unsigned long int   x13;
            long long           x14;
            unsigned long long  x15;
            float               x16;
            double              x17;
            void               *x18;
            int8                x19;
            int8_t              x20;
            uint8               x21;
            uint8_t             x22;
            int16               x23;
            int16_t             x24;
            uint16              x25;
            uint16_t            x26;
            int32               x27;
            int32_t             x28;
            uint32              x29;
            uint32_t            x30;
            int64               x31;
            int64_t             x32;
            uint64              x33;
            uint64_t            x34;
        }
    """


class Foo1(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            long p;
            char c;
            long x;
        }
    """


class Foo2(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            char c;
            char pad[7];
            long p;
            long x;
        }
    """


class Foo3(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            long p;
            char c;
        }
    """


class Foo4(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            short s;
            char c;
        }
    """


class Foo5(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            char c;
            struct foo5_inner {
                long p;
                short x;
            } inner;
        }
    """


class Foo10(CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        struct {
            char c;
            long p;
            short s;
        }
    """


def test_utmp_sizeof():
    assert sizeof("struct Utmp") == 384


# http://www.catb.org/esr/structure-packing/


def test_foo1_sizeof():
    assert sizeof("struct Foo1") == 24


def test_foo2_sizeof():
    assert sizeof("struct Foo2") == 24


def test_foo3_sizeof():
    assert sizeof("struct Foo3") == 16


def test_foo4_sizeof():
    assert sizeof("struct Foo4") == 4


def test_foo5_sizeof():
    assert sizeof("struct Foo5") == 24


def test_foo10_sizeof():
    assert sizeof("struct Foo10") == 24
