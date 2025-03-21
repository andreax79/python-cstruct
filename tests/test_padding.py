#!/usr/bin/env python

import cstruct
from cstruct import LITTLE_ENDIAN, NATIVE_ORDER, sizeof

DEFINITION = """
    struct struct1 {
        char      a[2];
        uint32_t  b;
    }
"""


class CStructNative(cstruct.CStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = DEFINITION


class MemCStructNative(cstruct.MemCStruct):
    __byte_order__ = NATIVE_ORDER
    __def__ = DEFINITION


class CStructLittleEndian(cstruct.CStruct):
    __byte_order__ = LITTLE_ENDIAN
    __def__ = DEFINITION


class MemCStructLittleEndian(cstruct.MemCStruct):
    __byte_order__ = LITTLE_ENDIAN
    __def__ = DEFINITION


def test_memcstruct_padding():
    for struct in (CStructNative, MemCStructNative):
        data = b"\x41\x42\x00\x00\x01\x00\x00\x00"
        assert sizeof(struct) == 8
        t = struct()
        t.unpack(data)
        assert t.a == b"AB"
        assert t.b == 1
        buf = t.pack()
        assert len(buf) == sizeof(struct)
        assert buf == data

        t2 = struct()
        t2.unpack(buf)
        assert t2.a == b"AB"
        assert t2.b == 1
        buf = t.pack()
        assert len(buf) == sizeof(struct)


def test_no_padding():
    for struct in (CStructLittleEndian, MemCStructLittleEndian):
        data = b"\x41\x42\x01\x00\x00\x00"
        assert sizeof(struct) == 6
        t = struct()
        t.unpack(data)
        assert t.a == b"AB"
        assert t.b == 1
        buf = t.pack()
        assert len(buf) == sizeof(struct)
        assert buf == data

        t2 = struct()
        t2.unpack(buf)
        assert t2.a == b"AB"
        assert t2.b == 1
        buf = t.pack()
        assert len(buf) == sizeof(struct)
