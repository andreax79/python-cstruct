Python-CStruct
==============

C-style structs for Python

[![Build Status](https://github.com/andreax79/python-cstruct/workflows/Tests/badge.svg)](https://github.com/andreax79/python-cstruct/actions)
[![PyPI version](https://badge.fury.io/py/cstruct.svg)](https://badge.fury.io/py/cstruct)
[![PyPI](https://img.shields.io/pypi/pyversions/cstruct.svg)](https://pypi.org/project/cstruct)
[![Downloads](https://pepy.tech/badge/cstruct/month)](https://pepy.tech/project/cstruct)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Known Vulnerabilities](https://snyk.io/test/github/andreax79/python-cstruct/badge.svg)](https://snyk.io/test/github/andreax79/python-cstruct)
[![Documentation](https://readthedocs.org/projects/python-cstruct/badge/?version=latest)](https://python-cstruct.readthedocs.io/en/latest/)

Convert C struct/union definitions into Python classes with methods for
serializing/deserializing.
The usage is very simple: create a class subclassing cstruct.MemCStruct
and add a C struct/union definition as a string in the __struct__ field.
The C struct/union definition is parsed at runtime and the struct format string
is generated. The class offers the method "unpack" for deserializing
an array of bytes into a Python object and the method "pack" for
serializing the values into an array of bytes.

[Api Documentation](https://python-cstruct.readthedocs.io/en/latest/)

Example
-------

The following program reads the DOS partition information from a disk.

```python
#!/usr/bin/env python
import cstruct

class Position(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned char head;
        unsigned char sector;
        unsigned char cyl;
    """


class Partition(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        #define ACTIVE_FLAG         0x80

        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    """

    def print_info(self):
        print(f"bootable: {'Y' if self.status & cstruct.getdef('ACTIVE_FLAG') else 'N'}")
        print(f"partition_type: {self.partition_type:02X}")
        print(f"start: head: {self.start.head:X} sectory: {self.start.sector:X} cyl: {self.start.cyl:X}")
        print(f"end: head: {self.end.head:X} sectory: {self.end.sector:X} cyl: {self.end.cyl:X}")
        print(f"starting sector: {self.start_sect:08x}")
        print(f"size MB: {self.sectors / 2 / 1024}")


class MBR(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        #define MBR_SIZE                    512
        #define MBR_DISK_SIGNATURE_SIZE       4
        #define MBR_USUALY_NULLS_SIZE         2
        #define MBR_SIGNATURE_SIZE            2
        #define MBR_BOOT_SIGNATURE       0xaa55
        #define MBR_PARTITIONS_NUM            4
        #define MBR_PARTITIONS_SIZE  (sizeof(Partition) * MBR_PARTITIONS_NUM)
        #define MBR_UNUSED_SIZE      (MBR_SIZE - MBR_DISK_SIGNATURE_SIZE - MBR_USUALY_NULLS_SIZE - MBR_PARTITIONS_SIZE - MBR_SIGNATURE_SIZE)

        char unused[MBR_UNUSED_SIZE];
        unsigned char disk_signature[MBR_DISK_SIGNATURE_SIZE];
        unsigned char usualy_nulls[MBR_USUALY_NULLS_SIZE];
        struct Partition partitions[MBR_PARTITIONS_NUM];
        uint16 signature;
    """

    @property
    def disk_signature_str(self):
        return "".join(reversed([f"{x:02x}" for x in self.disk_signature]))

    def print_info(self):
        print(f"disk signature: {self.disk_signature_str}")
        for i, partition in enumerate(self.partitions):
            print("")
            print(f"partition: {i}")
            partition.print_info()

disk = "mbr"
with open(disk, "rb") as f:
    mbr = MBR()
    mbr.unpack(f)
    mbr.print_info()
```

