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
and add a C struct/union definition as a string in the `__def__` field.

The C struct/union definition is parsed at runtime and the struct format string
is generated. The class offers the method `unpack` for deserializing
an array of bytes into a Python object and the method `pack` for
serializing the values into an array of bytes.

[Api Documentation](https://python-cstruct.readthedocs.io/en/latest/)

Install
-------

```
pip install cstruct
```

Features
--------

### Structs

Struct definition subclassing `cstruct.MemCStruct`

```python
class Position(cstruct.MemCStruct):
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """

pos = Position(head=10, sector=20, cyl=30)
print(f"head: {pos.head} sector: {pos.sector} cyl: {pos.cyl}")
```

Struct definition using `cstruct.parse`

```python
Partition = cstruct.parse("""
    struct {
        #define ACTIVE_FLAG         0x80

        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    }
""")

part = Partition()
part.status = cstruct.getdef('ACTIVE_FLAG')
```

### Unions

Union definition subclassing `cstruct.MemCStruct`

```python
class Data(cstruct.MemCStruct):
    __def__ = """
        union {
            int integer;
            float real;
        }
    """

data = Data()
data.integer = 2
data.real = 3
assert data.integer != 2
```

### Enums

Enum definition subclassing `cstruct.CEnum`

```python
class HtmlFont(cstruct.CEnum):
    __size__ = 2
    __def__ = """
        #define NONE         0

        enum htmlfont {
            HTMLFONT_NONE = NONE,
            HTMLFONT_BOLD,
            HTMLFONT_ITALIC
        }
    """

assert HtmlFont.HTMLFONT_NONE == 0
assert HtmlFont.HTMLFONT_BOLD == 1
assert HtmlFont.HTMLFONT_ITALIC == 2
```

Different supported `__def__` styles:

```c
enum Type_A a;  // externally defined using CEnum
enum Type_B {A, B, C} b;
enum {A, B, C} c;
```

```python
class Type_A(cstruct.CEnum):
  __size__ = 2
  __enum__ = """
    #define SOME_DEFINE 7

    A,
    B,
    C = 5,
    D,
    E = 7 + SOME_DEFINE
  """

# this is a nice gimmick that works, but wasn't really planned to be supported
class Type_C(cstruct.CEnum):
  A = 0,
  B = 1,
  C = 2,
  D = 3
```

### Nested structures (named/anonymous)

```python
class Packet(cstruct.MemCStruct):
    __def__ = """
        struct Packet {
            uint8_t packetLength;
            union {
                struct {
                    uint16_t field1;
                    uint16_t field2;
                    uint16_t field3;
                } format1;
                struct {
                    double value1;
                    double value2;
                } format2;
            };
        };
    """
```

### Byte Order, Size, and Padding

Suported byte orders:

* `cstruct.LITTLE_ENDIAN` - Little endian byte order, standard size, no padding
* `cstruct.BIG_ENDIAN` - Big endian byte order, standard size, no padding
* `cstruct.NATIVE_ORDER` - Native byte order, native size, padding

```python
class Native(cstruct.MemCStruct):
    __byte_order__ = cstruct.NATIVE_ORDER
    __def__ = """
        struct {
            long p;
            char c;
            long x;
        }
    """
```

### Flexible Array Member

```python
class Pkg(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            uint16_t cmd;
            uint16_t length;
            uint8_t data[];
        }
    """

pkg = Pkg()
pkg.length = 4
pkg.data = [10, 20, 30, 40]
```

### Pack and Unpack

```python
class StructWithEnum(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct StructWithEnum {
            enum HtmlFont font;
            unsigned int font_size;
        }
    """

# Pack
s.font = HtmlFont.HTMLFONT_NONE
s.font_size = 20
assert s.font == HtmlFont.HTMLFONT_NONE
assert s.font_size == 20
packed = s.pack()

# Unpack
s1 = StructWithEnum()
s1.unpack(packed)
assert s1.font == HtmlFont.HTMLFONT_NONE
assert s1.font_size == 20
```

### Define, Sizeof, and Eval

Definitions in Struct declaration:

```python
class Packet(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        #define MaxPacket 20

        struct Packet {
            uint8_t bytes[MaxPacket];
        }
    """
```

Parse C definitions:

```python
cstruct.parse("""
    #define A1  10
    #define A2  10 + A1
    #define A3  30
""")
assert cstruct.getdef("A1") == 10
assert cstruct.getdef('A2') == 20
```

Get structure size:

```python
cstruct.sizeof(Partition)
```

Evaluate C expression:

```python
cstruct.c_eval("A1 / 10")
cstruct.c_eval("((A10 < 6) || (A10>10))")
```

C expressions are automatically evaluated during structure definitions:

```python
class MBR(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        #define MBR_SIZE                    512
        #define MBR_DISK_SIGNATURE_SIZE       4
        #define MBR_USUALY_NULLS_SIZE         2
        #define MBR_SIGNATURE_SIZE            2
        #define MBR_BOOT_SIGNATURE       0xaa55
        #define MBR_PARTITIONS_NUM            4
        #define MBR_PARTITIONS_SIZE  (sizeof(Partition) * MBR_PARTITIONS_NUM)
        #define MBR_UNUSED_SIZE      (MBR_SIZE - MBR_DISK_SIGNATURE_SIZE - MBR_USUALY_NULLS_SIZE - MBR_PARTITIONS_SIZE - MBR_SIGNATURE_SIZE)

        struct {
            char unused[MBR_UNUSED_SIZE];
            unsigned char disk_signature[MBR_DISK_SIGNATURE_SIZE];
            unsigned char usualy_nulls[MBR_USUALY_NULLS_SIZE];
            struct Partition partitions[MBR_PARTITIONS_NUM];
            uint16 signature;
        }
    """
```

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
        #define ACTIVE_FLAG         0x80

        typedef struct Position Position;

        struct {
            unsigned char status;       /* 0x80 - active */
            Position start;
            unsigned char partition_type;
            Position end;
            unsigned int start_sect;    /* starting sector counting from 0 */
            unsigned int sectors;       /* nr of sectors in partition */
        }
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
    __def__ = """
        #define MBR_SIZE                    512
        #define MBR_DISK_SIGNATURE_SIZE       4
        #define MBR_USUALY_NULLS_SIZE         2
        #define MBR_SIGNATURE_SIZE            2
        #define MBR_BOOT_SIGNATURE       0xaa55
        #define MBR_PARTITIONS_NUM            4
        #define MBR_PARTITIONS_SIZE  (sizeof(Partition) * MBR_PARTITIONS_NUM)
        #define MBR_UNUSED_SIZE      (MBR_SIZE - MBR_DISK_SIGNATURE_SIZE - MBR_USUALY_NULLS_SIZE - MBR_PARTITIONS_SIZE - MBR_SIGNATURE_SIZE)

        typedef struct Partition Partition;

        struct {
            char unused[MBR_UNUSED_SIZE];
            unsigned char disk_signature[MBR_DISK_SIGNATURE_SIZE];
            unsigned char usualy_nulls[MBR_USUALY_NULLS_SIZE];
            Partition partitions[MBR_PARTITIONS_NUM];
            uint16 signature;
        }
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

