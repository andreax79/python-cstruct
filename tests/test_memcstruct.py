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
from cstruct import sizeof, typedef
import os


MBR_DATA = bytes(
    [
        0xEB,
        0x48,
        0x90,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x3,
        0x2,
        0xFF,
        0x0,
        0x0,
        0x80,
        0x61,
        0xCB,
        0x4,
        0x0,
        0x0,
        0x8,
        0xFA,
        0x80,
        0xCA,
        0x80,
        0xEA,
        0x53,
        0x7C,
        0x0,
        0x0,
        0x31,
        0xC0,
        0x8E,
        0xD8,
        0x8E,
        0xD0,
        0xBC,
        0x0,
        0x20,
        0xFB,
        0xA0,
        0x40,
        0x7C,
        0x3C,
        0xFF,
        0x74,
        0x2,
        0x88,
        0xC2,
        0x52,
        0xBE,
        0x79,
        0x7D,
        0xE8,
        0x34,
        0x1,
        0xF6,
        0xC2,
        0x80,
        0x74,
        0x54,
        0xB4,
        0x41,
        0xBB,
        0xAA,
        0x55,
        0xCD,
        0x13,
        0x5A,
        0x52,
        0x72,
        0x49,
        0x81,
        0xFB,
        0x55,
        0xAA,
        0x75,
        0x43,
        0xA0,
        0x41,
        0x7C,
        0x84,
        0xC0,
        0x75,
        0x5,
        0x83,
        0xE1,
        0x1,
        0x74,
        0x37,
        0x66,
        0x8B,
        0x4C,
        0x10,
        0xBE,
        0x5,
        0x7C,
        0xC6,
        0x44,
        0xFF,
        0x1,
        0x66,
        0x8B,
        0x1E,
        0x44,
        0x7C,
        0xC7,
        0x4,
        0x10,
        0x0,
        0xC7,
        0x44,
        0x2,
        0x1,
        0x0,
        0x66,
        0x89,
        0x5C,
        0x8,
        0xC7,
        0x44,
        0x6,
        0x0,
        0x70,
        0x66,
        0x31,
        0xC0,
        0x89,
        0x44,
        0x4,
        0x66,
        0x89,
        0x44,
        0xC,
        0xB4,
        0x42,
        0xCD,
        0x13,
        0x72,
        0x5,
        0xBB,
        0x0,
        0x70,
        0xEB,
        0x7D,
        0xB4,
        0x8,
        0xCD,
        0x13,
        0x73,
        0xA,
        0xF6,
        0xC2,
        0x80,
        0xF,
        0x84,
        0xF0,
        0x0,
        0xE9,
        0x8D,
        0x0,
        0xBE,
        0x5,
        0x7C,
        0xC6,
        0x44,
        0xFF,
        0x0,
        0x66,
        0x31,
        0xC0,
        0x88,
        0xF0,
        0x40,
        0x66,
        0x89,
        0x44,
        0x4,
        0x31,
        0xD2,
        0x88,
        0xCA,
        0xC1,
        0xE2,
        0x2,
        0x88,
        0xE8,
        0x88,
        0xF4,
        0x40,
        0x89,
        0x44,
        0x8,
        0x31,
        0xC0,
        0x88,
        0xD0,
        0xC0,
        0xE8,
        0x2,
        0x66,
        0x89,
        0x4,
        0x66,
        0xA1,
        0x44,
        0x7C,
        0x66,
        0x31,
        0xD2,
        0x66,
        0xF7,
        0x34,
        0x88,
        0x54,
        0xA,
        0x66,
        0x31,
        0xD2,
        0x66,
        0xF7,
        0x74,
        0x4,
        0x88,
        0x54,
        0xB,
        0x89,
        0x44,
        0xC,
        0x3B,
        0x44,
        0x8,
        0x7D,
        0x3C,
        0x8A,
        0x54,
        0xD,
        0xC0,
        0xE2,
        0x6,
        0x8A,
        0x4C,
        0xA,
        0xFE,
        0xC1,
        0x8,
        0xD1,
        0x8A,
        0x6C,
        0xC,
        0x5A,
        0x8A,
        0x74,
        0xB,
        0xBB,
        0x0,
        0x70,
        0x8E,
        0xC3,
        0x31,
        0xDB,
        0xB8,
        0x1,
        0x2,
        0xCD,
        0x13,
        0x72,
        0x2A,
        0x8C,
        0xC3,
        0x8E,
        0x6,
        0x48,
        0x7C,
        0x60,
        0x1E,
        0xB9,
        0x0,
        0x1,
        0x8E,
        0xDB,
        0x31,
        0xF6,
        0x31,
        0xFF,
        0xFC,
        0xF3,
        0xA5,
        0x1F,
        0x61,
        0xFF,
        0x26,
        0x42,
        0x7C,
        0xBE,
        0x7F,
        0x7D,
        0xE8,
        0x40,
        0x0,
        0xEB,
        0xE,
        0xBE,
        0x84,
        0x7D,
        0xE8,
        0x38,
        0x0,
        0xEB,
        0x6,
        0xBE,
        0x8E,
        0x7D,
        0xE8,
        0x30,
        0x0,
        0xBE,
        0x93,
        0x7D,
        0xE8,
        0x2A,
        0x0,
        0xEB,
        0xFE,
        0x47,
        0x52,
        0x55,
        0x42,
        0x20,
        0x0,
        0x47,
        0x65,
        0x6F,
        0x6D,
        0x0,
        0x48,
        0x61,
        0x72,
        0x64,
        0x20,
        0x44,
        0x69,
        0x73,
        0x6B,
        0x0,
        0x52,
        0x65,
        0x61,
        0x64,
        0x0,
        0x20,
        0x45,
        0x72,
        0x72,
        0x6F,
        0x72,
        0x0,
        0xBB,
        0x1,
        0x0,
        0xB4,
        0xE,
        0xCD,
        0x10,
        0xAC,
        0x3C,
        0x0,
        0x75,
        0xF4,
        0xC3,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x80,
        0x0,
        0x2,
        0x0,
        0x83,
        0xFE,
        0x3F,
        0x86,
        0x1,
        0x0,
        0x0,
        0x0,
        0xC6,
        0x17,
        0x21,
        0x0,
        0x0,
        0x0,
        0x1,
        0x87,
        0x8E,
        0xFE,
        0xFF,
        0xFF,
        0xC7,
        0x17,
        0x21,
        0x0,
        0x4D,
        0xD3,
        0xDE,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x55,
        0xAA,
    ]
)


class Position(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


class Partition(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char status;       /* 0x80 - active */
            struct Position start;
            unsigned char partition_type;
            struct Position end;
            unsigned int start_sect;    /* starting sector counting from 0 */
            unsigned int sectors;       // nr of sectors in partition
        }
    """


class MBR(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            char unused[440];
            unsigned char disk_signature[4];
            unsigned char usualy_nulls[2];
            struct Partition partitions[4];
            char signature[2];
        }
    """


class Dummy(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
            struct {
            char c;
            char vc[10];
            int i;
            int vi[10];
            long long l;
            long vl[10];
            float f;
            float vf[10];
        }
    """


typedef('char', 'BYTE')
typedef('short', 'WORD')
typedef('int', 'DWORD')


class PartitionFlat(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            BYTE status;            // 0x80 for bootable, 0x00 for not bootable
            BYTE startAddrHead;     // head address of start of partition
            WORD startAddrCylSec;
            BYTE partType;
            BYTE endAddrHead;       // head address of start of partition
            WORD endAddrCylSec;
            DWORD startLBA;         // address of first sector in partition
            DWORD endLBA;           // address of last sector in partition
        }
    """


class PartitionNested(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            BYTE status;            // 0x80 for bootable, 0x00 for not bootable
            struct {
                BYTE addrHead;      // head address of start of partition
                WORD addrCylSec;
            } start;
            BYTE partType;
            struct b {
                BYTE addrHead;      // head address of start of partition
                WORD addrCylSec;
            } end;
            DWORD startLBA;         // address of first sector in partition
            DWORD endLBA;           // address of last sector in partition
        }
    """


def test_len():
    mbr = MBR()
    assert len(mbr) == 512
    assert mbr.size == 512


def test_pack_len():
    buffer = b'\x00' * 512
    mbr = MBR(buffer)
    d = mbr.pack()
    assert len(d) == 512
    mbr = MBR()
    mbr.unpack(MBR_DATA)
    d = mbr.pack()
    assert len(d) == 512
    mbr = MBR()
    d = mbr.pack()
    assert len(d) == 512


def test_sizeof():
    assert sizeof("struct Partition") == sizeof("struct PartitionFlat")
    assert sizeof("struct Partition") == sizeof("struct PartitionNested")


def test_unpack():
    mbr = MBR()
    mbr.unpack(MBR_DATA)
    assert mbr.signature[0] == 0x55
    assert mbr.signature[1] == 0xAA
    assert mbr.partitions[0].start.head == 0
    assert mbr.partitions[0].end.head == 0xFE
    assert mbr.partitions[1].start_sect == 0x2117C7


def test_pack():
    mbr = MBR(MBR_DATA)
    d = mbr.pack()
    assert MBR_DATA == d
    mbr.partitions[3].start.head = 123
    d1 = mbr.pack()
    mbr1 = MBR(d1)
    assert mbr1.partitions[3].start.head == 123


def test_init():
    p = Position(head=254, sector=63, cyl=134)
    mbr = MBR(MBR_DATA)
    assert mbr.partitions[0].end.head == p.head
    assert mbr.partitions[0].end.sector == p.sector
    assert mbr.partitions[0].end.cyl == p.cyl


def test_none():
    mbr = MBR()
    assert mbr.partitions[0].end.sector == 0
    mbr.unpack(None)
    assert mbr.partitions[0].end.head == 0


def test_clear():
    mbr = MBR()
    mbr.unpack(MBR_DATA)
    assert mbr.partitions[0].end.head == 0xFE
    mbr.clear()
    assert mbr.partitions[0].end.head == 0x00


def test_inline():
    TestStruct = cstruct.MemCStruct.parse(
        'struct { unsigned char head; unsigned char sector; unsigned char cyl; }', __byte_order__=cstruct.LITTLE_ENDIAN
    )
    s = TestStruct(head=254, sector=63, cyl=134)
    p = Position(head=254, sector=63, cyl=134)
    assert s.pack() == p.pack()


def test_dummy():
    dummy = Dummy()
    dummy.c = b'A'
    dummy.vc = b'ABCDEFGHIJ'
    dummy.i = 123456
    for i in range(0, 10):
        dummy.vi[i] = i * 10
    dummy.f = 123.456
    for i in range(0, 10):
        dummy.vf[i] = 10.0 / (i + 1)
    dummy.vl = list(range(0, 10))
    data = dummy.pack()
    dummy1 = Dummy(data)
    for i in range(0, 10):
        dummy1.vl[i] = dummy.vl[i]
    assert dummy.pack() == dummy1.pack()
    dummy2 = Dummy(data)
    dummy2.vf[2] = 79
    assert dummy.pack() != dummy2.pack()
    dummy3 = Dummy(data)
    dummy3.vl = list(range(1, 11))
    assert dummy.pack() != dummy3.pack()


def test_nested():
    data = os.urandom(sizeof("struct PartitionFlat"))
    flat = PartitionFlat(data)
    flat.unpack(data)
    nested = PartitionNested(data)
    nested.unpack(data)
    assert flat.status == nested.status
    assert flat.startAddrHead == nested.start.addrHead
    assert flat.startAddrCylSec == nested.start.addrCylSec
    assert flat.partType == nested.partType
    assert flat.endAddrHead == nested.end.addrHead
    assert flat.endAddrCylSec == nested.end.addrCylSec
    assert flat.startLBA == nested.startLBA
    assert flat.endLBA == nested.endLBA
