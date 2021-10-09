#!/usr/bin/env python
#*****************************************************************************
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
#*****************************************************************************

from unittest import TestCase, main
import cstruct
from cstruct import (sizeof, typedef)
import io
import os


MBR_DATA = bytes([0xeb,0x48,0x90,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x3,0x2,0xff,0x0,0x0,0x80,0x61,0xcb,0x4,0x0,0x0,0x8,0xfa,0x80,0xca,0x80,0xea,0x53,0x7c,0x0,0x0,0x31,0xc0,0x8e,0xd8,0x8e,0xd0,0xbc,0x0,0x20,0xfb,0xa0,0x40,0x7c,0x3c,0xff,0x74,0x2,0x88,0xc2,0x52,0xbe,0x79,0x7d,0xe8,0x34,0x1,0xf6,0xc2,0x80,0x74,0x54,0xb4,0x41,0xbb,0xaa,0x55,0xcd,0x13,0x5a,0x52,0x72,0x49,0x81,0xfb,0x55,0xaa,0x75,0x43,0xa0,0x41,0x7c,0x84,0xc0,0x75,0x5,0x83,0xe1,0x1,0x74,0x37,0x66,0x8b,0x4c,0x10,0xbe,0x5,0x7c,0xc6,0x44,0xff,0x1,0x66,0x8b,0x1e,0x44,0x7c,0xc7,0x4,0x10,0x0,0xc7,0x44,0x2,0x1,0x0,0x66,0x89,0x5c,0x8,0xc7,0x44,0x6,0x0,0x70,0x66,0x31,0xc0,0x89,0x44,0x4,0x66,0x89,0x44,0xc,0xb4,0x42,0xcd,0x13,0x72,0x5,0xbb,0x0,0x70,0xeb,0x7d,0xb4,0x8,0xcd,0x13,0x73,0xa,0xf6,0xc2,0x80,0xf,0x84,0xf0,0x0,0xe9,0x8d,0x0,0xbe,0x5,0x7c,0xc6,0x44,0xff,0x0,0x66,0x31,0xc0,0x88,0xf0,0x40,0x66,0x89,0x44,0x4,0x31,0xd2,0x88,0xca,0xc1,0xe2,0x2,0x88,0xe8,0x88,0xf4,0x40,0x89,0x44,0x8,0x31,0xc0,0x88,0xd0,0xc0,0xe8,0x2,0x66,0x89,0x4,0x66,0xa1,0x44,0x7c,0x66,0x31,0xd2,0x66,0xf7,0x34,0x88,0x54,0xa,0x66,0x31,0xd2,0x66,0xf7,0x74,0x4,0x88,0x54,0xb,0x89,0x44,0xc,0x3b,0x44,0x8,0x7d,0x3c,0x8a,0x54,0xd,0xc0,0xe2,0x6,0x8a,0x4c,0xa,0xfe,0xc1,0x8,0xd1,0x8a,0x6c,0xc,0x5a,0x8a,0x74,0xb,0xbb,0x0,0x70,0x8e,0xc3,0x31,0xdb,0xb8,0x1,0x2,0xcd,0x13,0x72,0x2a,0x8c,0xc3,0x8e,0x6,0x48,0x7c,0x60,0x1e,0xb9,0x0,0x1,0x8e,0xdb,0x31,0xf6,0x31,0xff,0xfc,0xf3,0xa5,0x1f,0x61,0xff,0x26,0x42,0x7c,0xbe,0x7f,0x7d,0xe8,0x40,0x0,0xeb,0xe,0xbe,0x84,0x7d,0xe8,0x38,0x0,0xeb,0x6,0xbe,0x8e,0x7d,0xe8,0x30,0x0,0xbe,0x93,0x7d,0xe8,0x2a,0x0,0xeb,0xfe,0x47,0x52,0x55,0x42,0x20,0x0,0x47,0x65,0x6f,0x6d,0x0,0x48,0x61,0x72,0x64,0x20,0x44,0x69,0x73,0x6b,0x0,0x52,0x65,0x61,0x64,0x0,0x20,0x45,0x72,0x72,0x6f,0x72,0x0,0xbb,0x1,0x0,0xb4,0xe,0xcd,0x10,0xac,0x3c,0x0,0x75,0xf4,0xc3,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x80,0x0,0x2,0x0,0x83,0xfe,0x3f,0x86,0x1,0x0,0x0,0x0,0xc6,0x17,0x21,0x0,0x0,0x0,0x1,0x87,0x8e,0xfe,0xff,0xff,0xc7,0x17,0x21,0x0,0x4d,0xd3,0xde,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x55,0xaa])


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

typedef('char',  'BYTE')
typedef('short', 'WORD')
typedef('int',   'DWORD')

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


class TestCStruct(TestCase):

    def test_len(self):
        mbr = MBR()
        self.assertEqual(len(mbr), 512)
        self.assertEqual(mbr.size, 512)

    def test_sizeof(self):
        self.assertEqual(sizeof("struct Partition"), sizeof("struct PartitionFlat"))
        self.assertEqual(sizeof("struct Partition"), sizeof("struct PartitionNested"))

    def test_unpack(self):
        mbr = MBR()
        f = io.BytesIO(MBR_DATA)
        mbr.unpack(f)
        self.assertEqual(mbr.signature[0], 0x55)
        self.assertEqual(mbr.signature[1], 0xaa)
        self.assertEqual(mbr.partitions[0].start.head, 0)
        self.assertEqual(mbr.partitions[0].end.head, 0xfe)
        self.assertEqual(mbr.partitions[1].start_sect, 0x2117c7)

    def test_pack(self):
        mbr = MBR(MBR_DATA)
        d = mbr.pack()
        self.assertEqual(MBR_DATA, d)
        mbr.partitions[3].start.head = 123
        d1 = mbr.pack()
        mbr1 = MBR(d1)
        self.assertEqual(mbr1.partitions[3].start.head, 123)

    def test_init(self):
        p = Position(head=254, sector=63, cyl=134)
        mbr = MBR(MBR_DATA)
        self.assertEqual(mbr.partitions[0].end.head, p.head)
        self.assertEqual(mbr.partitions[0].end.sector, p.sector)
        self.assertEqual(mbr.partitions[0].end.cyl, p.cyl)

    def test_none(self):
        mbr = MBR()
        self.assertEqual(mbr.partitions[0].end.sector, 0)
        mbr.unpack(None)
        self.assertEqual(mbr.partitions[0].end.head, 0)

    def test_clear(self):
        mbr = MBR()
        mbr.unpack(MBR_DATA)
        self.assertEqual(mbr.partitions[0].end.head, 0xfe)
        mbr.clear()
        self.assertEqual(mbr.partitions[0].end.head, 0x00)

    def test_inline(self):
        TestStruct = cstruct.parse('struct TestStruct { unsigned char head; unsigned char sector; unsigned char cyl; }',__byte_order__=cstruct.LITTLE_ENDIAN)
        s = TestStruct(head=254, sector=63, cyl=134)
        p = Position(head=254, sector=63, cyl=134)
        self.assertEqual(s.pack(), p.pack())

    def test_dummy(self):
        dummy = Dummy()
        dummy.c = b'A'
        dummy.vc = b'ABCDEFGHIJ'
        dummy.i = 123456
        for i in range(0, 10):
            dummy.vi[i] = i * 10
        dummy.f = 123.456
        for i in range(0, 10):
            dummy.vf[i] = 10.0 / (i+1)
        dummy.vl = list(range(0, 10));
        data = dummy.pack()
        dummy1 = Dummy(data)
        for i in range(0, 10):
            dummy1.vl[i] = dummy.vl[i]
        self.assertEqual(dummy.pack(), dummy1.pack())
        dummy2 = Dummy(data)
        dummy2.vf[2] = 79
        self.assertNotEqual(dummy.pack(), dummy2.pack())
        dummy3 = Dummy(data)
        dummy3.vl = list(range(1, 11));
        self.assertNotEqual(dummy.pack(), dummy3.pack())

    def test_nested(self):
        data = os.urandom(sizeof("struct PartitionFlat") )
        flat = PartitionFlat(data)
        flat.unpack(data)
        nested = PartitionNested(data)
        nested.unpack(data)
        self.assertEqual(flat.status, nested.status)
        self.assertEqual(flat.startAddrHead, nested.start.addrHead)
        self.assertEqual(flat.startAddrCylSec, nested.start.addrCylSec)
        self.assertEqual(flat.partType, nested.partType)
        self.assertEqual(flat.endAddrHead, nested.end.addrHead)
        self.assertEqual(flat.endAddrCylSec, nested.end.addrCylSec)
        self.assertEqual(flat.startLBA, nested.startLBA)
        self.assertEqual(flat.endLBA, nested.endLBA)

if __name__ == '__main__':
    main()
