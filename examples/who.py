#!/usr/bin/env python

import argparse
import sys
import time
from pathlib import Path

from cstruct import NATIVE_ORDER, MemCStruct, getdef, parse

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

typedef int pid_t;
typedef long time_t;
"""
)


class ExitStatus(MemCStruct):
    __def__ = """
        struct ExitStatus {
            short   e_termination;      /* Process termination status.  */
            short   e_exit;             /* Process exit status.  */
        }
    """


class Timeval(MemCStruct):
    __def__ = """
        struct {
            int32_t tv_sec;             /* Seconds.  */
            int32_t tv_usec;            /* Microseconds.  */
        }
    """


def str_from_c(string):
    return string.decode().split("\0")[0]


class Utmp(MemCStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = """
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
