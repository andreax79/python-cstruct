#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************************************************************
#
# Copyright (c) 2013 Andrea Bonomi <andrea.bonomi@gmail.com>
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

#            pts/1        2013-06-06 18:09             23120 id=ts/1  term=0 exit=0
#            system boot  2013-05-20 21:27
#            run-level 2  2013-05-20 21:27
# LOGIN      tty4         2013-05-20 21:27              1631 id=4
# LOGIN      tty5         2013-05-20 21:27              1645 id=5
# LOGIN      tty2         2013-05-20 21:27              1657 id=2
# LOGIN      tty3         2013-05-20 21:27              1658 id=3
# LOGIN      tty6         2013-05-20 21:27              1661 id=6
# LOGIN      tty1         2013-05-20 21:27              2879 id=1
#            pts/22       2013-06-06 07:43               972 id=s/22  term=0 exit=0
# andreax  + pts/0        2013-08-22 09:04   .         15682 (l26.box)
#            pts/34       2013-06-12 15:04             26396 id=s/34  term=0 exit=0
#            pts/21       2013-06-25 11:12             32321 id=s/21  term=0 exit=0
#            pts/24       2013-07-02 22:04             29473 id=/24   term=0 exit=0
#            pts/27       2013-07-03 12:04              8492 id=/27   term=0 exit=0
#            pts/31       2013-07-18 18:49             27215 id=s/31  term=0 exit=0
#            pts/30       2013-07-24 14:40             19054 id=s/30  term=0 exit=0
#            pts/28       2013-07-30 20:49             24942 id=s/28  term=0 exit=0
#            pts/27       2013-08-02 17:59             31326 id=s/27  term=0 exit=0
# 012345678901234567890123456789012345678901234567890123456789012345678901234567890
from cstruct import parse, getdef, typedef, MemCStruct, NATIVE_ORDER
from pathlib import Path
import argparse
import sys
import time

DEFAULT_FILENAME = "/var/run/utmp"

parse(
    """
/* Values for ut_type field, below */

#define EMPTY             0 /* Record does not contain valid info
                              (formerly known as UT_UNKNOWN on Linux) */
#define RUN_LVL           1 /* Change in system run-level (see
                              init(1)) */
#define BOOT_TIME         2 /* Time of system boot (in ut_tv) */
#define NEW_TIME          3 /* Time after system clock change
                              (in ut_tv) */
#define OLD_TIME          4 /* Time before system clock change
                              (in ut_tv) */
#define INIT_PROCESS      5 /* Process spawned by init(1) */
#define LOGIN_PROCESS     6 /* Session leader process for user login */
#define USER_PROCESS      7 /* Normal process */
#define DEAD_PROCESS      8 /* Terminated process */
#define ACCOUNTING        9 /* Not implemented */

#define UT_LINESIZE      32
#define UT_NAMESIZE      32
#define UT_HOSTSIZE     256
"""
)

typedef("int", "pid_t")
typedef("long", "time_t")


class ExitStatus(MemCStruct):
    __struct__ = """
        short   e_termination;      /* Process termination status.  */
        short   e_exit;             /* Process exit status.  */
    """


class Timeval(MemCStruct):
    __struct__ = """
        int32_t tv_sec;             /* Seconds.  */
        int32_t tv_usec;            /* Microseconds.  */
    """


def str_from_c(string):
    return string.decode().split("\0")[0]


class Utmp(MemCStruct):
    __byte_order__ = NATIVE_ORDER
    __struct__ = """
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
    """

    @property
    def user(self):
        return str_from_c(self.ut_user)

    @property
    def line(self):
        return str_from_c(self.ut_line)

    @property
    def time(self):
        return time.strftime("%Y-%m-%d %H:%M", time.gmtime(self.ut_tv.tv_sec))

    @property
    def host(self):
        if str_from_c(self.ut_host):
            host = str_from_c(self.ut_host)
            return f"({host})"
        elif self.ut_id:
            ut_id = str_from_c(self.ut_id)
            return f"id={ut_id}"
        else:
            return ""

    def __str__(self):
        return f"{self.user:<10s} {self.line:<12s} {self.time:<15s} {self.ut_pid:>15} {self.host:<8s}"

    def print_info(self, show_all):
        if show_all or self.ut_type in (getdef('LOGIN_PROCESS'), getdef('USER_PROCESS')):
            print(self)


def main():
    parser = argparse.ArgumentParser(description="Print information about users who are currently logged in.")
    parser.add_argument("-a", "--all", action="store_true", dest="show_all", help="show all enties")
    parser.add_argument("file", nargs="?", help="if FILE is not specified use /var/run/utmp", default=DEFAULT_FILENAME)
    args = parser.parse_args()

    utmp = Utmp()
    try:
        with Path(args.file).open("rb") as f:
            while utmp.unpack(f):
                utmp.print_info(args.show_all)
    except (IOError, OSError) as ex:
        print(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
