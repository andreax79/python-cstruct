#!/usr/bin/python
#*****************************************************************************
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
#*****************************************************************************

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
#012345678901234567890123456789012345678901234567890123456789012345678901234567890
from cstruct import define, typedef, CStruct
import sys
import time

define("UT_NAMESIZE", 32)
define("UT_LINESIZE", 32)
define("UT_HOSTSIZE", 256)

typedef("int", "pid_t")
typedef("long", "time_t")
typedef("int32", "int32_t")

class ExitStatus(CStruct):
    __struct__ = """
        short   e_termination;      /* Process termination status.  */
        short   e_exit;             /* Process exit status.  */
    """
class Timeval(CStruct):
    __struct__ = """
        int32_t tv_sec;             /* Seconds.  */
        int32_t tv_usec;            /* Microseconds.  */
    """

def str_from_c(string):
    return string.split("\0")[0];

class Utmp(CStruct):
    __struct__ = """
        short int ut_type;          /* Type of login.  */
        pid_t ut_pid;               /* Process ID of login process.  */
        char ut_line[UT_LINESIZE];  /* Devicename.  */
        char ut_id[4];              /* Inittab ID.  */
        char ut_user[UT_NAMESIZE];  /* Username.  */
        char ut_host[UT_HOSTSIZE];  /* Hostname for remote login.  */
        struct ExitStatus ut_exit;  /* Exit status of a process marked as DEAD_PROCESS.  */
        int32_t ut_session;         /* Session ID, used for windowing.  */
        struct Timeval ut_tv;       /* Time entry was made.  */
        int32_t ut_addr_v6[4];      /* Internet address of remote host.  */
        char __unused[20];          /* Reserved for future use.  */
    """

    def print_info(self):
        "andreax  + pts/0        2013-08-21 08:58   .         32341 (l26.box)"
        "           pts/34       2013-06-12 15:04             26396 id=s/34  term=0 exit=0"
#        if self.ut_type not in [6,7]:
#            return
        print("%-10s %-12s %15s %15s %-8s" % (
                    str_from_c(self.ut_user),
                    str_from_c(self.ut_line),
                    time.strftime("%Y-%m-%d %H:%M", time.gmtime(self.ut_tv.tv_sec)),
                    self.ut_pid,
                    str_from_c(self.ut_host) and "(%s)" % str_from_c(self.ut_host) or str_from_c(self.ut_id) and "id=%s" % str_from_c(self.ut_id) or ""))

def main():
    utmp = len(sys.argv) > 1 and  sys.argv[1] or "/var/run/utmp"
    with open(utmp, "rb") as f:
        utmp = Utmp()
        data = f.read(len(utmp))
        while(data):
            utmp.unpack(data)
            utmp.print_info()
            data = f.read(len(utmp))

if __name__ == "__main__":
    main()

