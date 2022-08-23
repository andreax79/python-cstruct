Python-CStruct
==============

C-style structs for Python

[![Build Status](https://github.com/andreax79/python-cstruct/workflows/Tests/badge.svg)](https://github.com/andreax79/python-cstruct/actions)
[![PyPI version](https://badge.fury.io/py/cstruct.svg)](https://badge.fury.io/py/cstruct)
[![PyPI](https://img.shields.io/pypi/pyversions/cstruct.svg)](https://pypi.org/project/cstruct)
[![Downloads](https://pepy.tech/badge/cstruct/month)](https://pepy.tech/project/cstruct)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Known Vulnerabilities](https://snyk.io/test/github/andreax79/python-cstruct/badge.svg)](https://snyk.io/test/github/andreax79/python-cstruct)

Convert C struct/union definitions into Python classes with methods for
serializing/deserializing.
The usage is very simple: create a class subclassing cstruct.MemCStruct
and add a C struct/union definition as a string in the __struct__ field.
The C struct/union definition is parsed at runtime and the struct format string
is generated. The class offers the method "unpack" for deserializing
an array of bytes into a Python object and the method "pack" for
serializing the values into an array of bytes.

Example
-------

The following program reads the DOS partition information from a disk.

```python
#!/usr/bin/env python
import cstruct

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
            unsigned int sectors;       /* nr of sectors in partition */
        }
    """

    def print_info(self):
        print("bootable: %s" % ((self.status & 0x80) and "Y" or "N"))
        print("partition_type: %02X" % self.partition_type)
        print("start: head: %X sectory: %X cyl: %X" % (self.start.head, self.start.sector, self.start.cyl))
        print("end: head: %X sectory: %X cyl: %X" % (self.end.head, self.end.sector, self.end.cyl))
        print("starting sector: %08X" % self.start_sect)
        print("size MB: %s" % (self.sectors / 2 / 1024))

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

    def print_info(self):
        print("disk signature: %s" % "".join(["%02X" % x for x in self.disk_signature]))
        print("usualy nulls: %s" % "".join(["%02X" % x for x in self.usualy_nulls]))
        for i, partition in enumerate(self.partitions):
            print("")
            print("partition: %s" % i)
            partition.print_info()

disk = "mbr"
with open(disk, "rb") as f:
    mbr = MBR()
    mbr.unpack(f)
    mbr.print_info()
```

