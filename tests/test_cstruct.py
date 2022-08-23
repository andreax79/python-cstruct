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
import io
import os
from pathlib import Path

MBR_DATA = (Path(__file__).parent.parent / 'mbr').read_bytes()


class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


class Partition(cstruct.CStruct):
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


class MBR(cstruct.CStruct):
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


class Dummy(cstruct.CStruct):
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


class PartitionFlat(cstruct.CStruct):
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


class PartitionNested(cstruct.CStruct):
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
    f = io.BytesIO(MBR_DATA)
    mbr.unpack(f)
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
    StructT1 = cstruct.parse(
        'struct StructT1 { unsigned char head; unsigned char sector; unsigned char cyl; }',
        __byte_order__=cstruct.LITTLE_ENDIAN,
    )
    s = StructT1(head=254, sector=63, cyl=134)
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
