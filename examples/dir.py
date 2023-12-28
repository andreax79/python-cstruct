#!/usr/bin/env python
import ctypes
import sys

import cstruct

libc = ctypes.cdll.LoadLibrary("libc.so.6")
# opendir
libc.opendir.argtypes = [ctypes.c_char_p]
libc.opendir.restype = ctypes.c_void_p
# readdir
libc.readdir.argtypes = [ctypes.c_void_p]
libc.readdir.restype = ctypes.c_void_p
# closedir
libc.closedir.argtypes = [ctypes.c_void_p]
libc.closedir.restype = ctypes.c_int


class DType(cstruct.CEnum):
    __size__ = 1
    __def__ = """
        enum d_type {
            DT_UNKNOWN = 0x0,
            DT_FIFO = 0x1,
            DT_CHR = 0x2,
            DT_DIR = 0x4,
            DT_BLK = 0x6,
            DT_REG = 0x8,
            DT_LNK = 0xa,
            DT_SOCK = 0xc
        };
    """

    def __str__(self):
        return {
            DType.DT_UNKNOWN: "<unknown>",
            DType.DT_FIFO: "<fifo>",
            DType.DT_CHR: "<char>",
            DType.DT_DIR: "<dir>",
            DType.DT_BLK: "<block>",
            DType.DT_REG: "<regular>",
            DType.DT_LNK: "<link>",
            DType.DT_SOCK: "<socket>",
        }[self]


class Dirent(cstruct.MemCStruct):
    __def__ = """
        #define PATH_MAX 4096

        typedef long ino_t;
        typedef long off_t;

        struct dirent {
            ino_t          d_ino;       /* Inode number */
            off_t          d_off;       /* Not an offset */
            unsigned short d_reclen;    /* Length of this record */
            unsigned char  d_type;      /* Type of file; not supported
                                           by all filesystem types */
            char           d_name[256]; /* Null-terminated filename */
        };
    """

    @property
    def name(self):
        return ctypes.c_char_p(self.d_name).value.decode("ascii")

    @property
    def type(self):
        return DType(self.d_type)


def main():
    if len(sys.argv) > 1:
        cwd = ctypes.create_string_buffer(sys.argv[1].encode("ascii"))
    else:
        # Get current dir
        cwd = ctypes.create_string_buffer(cstruct.getdef("PATH_MAX") + 1)
        assert libc.getcwd(cwd, ctypes.sizeof(cwd)) != 0
    # Open dir
    dp = libc.opendir(cwd)
    assert dp != 0
    # Read dir entries
    ep = libc.readdir(dp)
    while ep:
        contents = ctypes.cast(ep, ctypes.POINTER(ctypes.c_char * Dirent.size)).contents
        dirent = Dirent(contents)
        print(f"{dirent.d_ino:8} {dirent.type:10} {dirent.name}")
        ep = libc.readdir(dp)
    # Close dir
    libc.closedir(dp)


if __name__ == "__main__":
    main()
