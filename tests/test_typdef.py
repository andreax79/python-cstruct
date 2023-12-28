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

from cstruct import NATIVE_ORDER, MemCStruct
from cstruct.base import TYPEDEFS


class ExitStatus(MemCStruct):
    __def__ = """
        struct ExitStatus {
            short   e_termination;      /* Process termination status.  */
            short   e_exit;             /* Process exit status.  */
        }
    """


class Utmp(MemCStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
        #define UT_NAMESIZE 32
        #define UT_LINESIZE 32
        #define UT_HOSTSIZE 256

        typedef int pid_t;
        typedef long time_t;
        typedef unsigned long int ulong;
        typedef struct ExitStatus ExitStatus;

        struct {
            short   ut_type;              /* Type of record */
            pid_t   ut_pid;               /* PID of login process */
            char    ut_line[UT_LINESIZE]; /* Device name of tty - "/dev/" */
            char    ut_id[4];             /* Terminal name suffix, or inittab(5) ID */
            char    ut_user[UT_NAMESIZE]; /* Username */
            char    ut_host[UT_HOSTSIZE]; /* Hostname for remote login, or kernel version for run-level messages */
            ExitStatus ut_exit;           /* Exit status of a process marked as DEAD_PROCESS; not used by Linux init (1 */
            int32_t ut_session;           /* Session ID (getsid(2)), used for windowing */
            struct {
               int32_t tv_sec;            /* Seconds */
               int32_t tv_usec;           /* Microseconds */
            } ut_tv;                      /* Time entry was made */
            int32_t ut_addr_v6[4];        /* Internet address of remote host; IPv4 address uses just ut_addr_v6[0] */
            char __unused[20];            /* Reserved for future use */
        }
    """


def test_typedef():
    assert TYPEDEFS["pid_t"] == "int"
    assert TYPEDEFS["time_t"] == "long"
    assert TYPEDEFS["ulong"] == "unsigned long"
    assert TYPEDEFS["ExitStatus"] == "struct ExitStatus"
