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

The usage is very simple: create a class subclassing
[`cstruct.MemCStruct`](https://python-cstruct.readthedocs.io/en/latest/api/mem_cstruct/)
and add a C struct/union definition as a string in the `__def__` field.

The C struct/union definition is parsed at runtime and the struct format string
is generated. The class offers the method `unpack` for deserializing
an array of bytes into a Python object and the method `pack` for
serializing the values into an array of bytes.

Install
-------

```
pip install cstruct
```

Examples
--------

* [Read the DOS-type (MBR) partition table](https://python-cstruct.readthedocs.io/en/latest/examples/fdisk/)
* [Print information about logged uses](https://python-cstruct.readthedocs.io/en/latest/examples/who/)
* [Flexible Array Member (FAM)](https://python-cstruct.readthedocs.io/en/latest/examples/flexible_array/)
* [libc integration (using ctypes)](https://python-cstruct.readthedocs.io/en/latest/examples/dir/)


Features
--------

### Structs

Struct definition subclassing `cstruct.MemCStruct`. Methods can access stuct values as instance variables.

```python
class Position(cstruct.MemCStruct):
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """
    @property
    def lba(self):
        return (self.cyl * 16 + self.head) * 63 + (self.sector - 1)

pos = Position(cyl=15, head=15, sector=63)
print(f"head: {pos.head} sector: {pos.sector} cyl: {pos.cyl} lba: {pos.lba}")
```

Struct definition using `cstruct.parse`.

```python
Partition = cstruct.parse("""
    #define ACTIVE_FLAG         0x80

    struct Partition {
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

Union definition subclassing `cstruct.MemCStruct`.

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

Enum definition subclassing `cstruct.CEnum`.

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

Different enum styles are supported in struct/union definitions.

```c
enum Type_A a;  // externally defined using CEnum
enum Type_B {A, B, C} b;
enum {A, B, C} c;
enum Type_D : short {A, B, C} d; // specify the underlying type
enum Direction { left = 'l', right = 'r' };
```

### Nested structs/unions

Nested stucts and unions are supported, both named and anonymous.

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

A code example illustrating how to use
[`pack`](https://python-cstruct.readthedocs.io/en/latest/api/abstract/#cstruct.abstract.AbstractCStruct.pack) to pack a structure into binary form.

```python
class Position(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """

pos = Position(head=10, sector=20, cyl=3)
packed = pos.pack()
```

Binary representation can be converted into structure using
[`unpack`](https://python-cstruct.readthedocs.io/en/latest/api/abstract/#cstruct.abstract.AbstractCStruct.unpack).

```
pos1 = Position()
pos1.unpack(packed)
assert pos1.head == 10
assert pos1.sector == 20
assert pos1.cyl == 3
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

Evaluate C expression using [`c_eval`](https://python-cstruct.readthedocs.io/en/latest/api/c_expr/):

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

### Ispect memory

The [`inspect`](https://python-cstruct.readthedocs.io/en/latest/api/abstract/#cstruct.abstract.AbstractCStruct.inspect) methods displays memory contents in hexadecimal.

```python
print(mbr.inspect())
```

Output example:
```
00000000  eb 48 90 00 00 00 00 00  00 00 00 00 00 00 00 00  |.H..............|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 03 02  |................|
00000040  ff 00 00 80 61 cb 04 00  00 08 fa 80 ca 80 ea 53  |....a..........S|
00000050  7c 00 00 31 c0 8e d8 8e  d0 bc 00 20 fb a0 40 7c  ||..1....... ..@||
00000060  3c ff 74 02 88 c2 52 be  79 7d e8 34 01 f6 c2 80  |<.t...R.y}.4....|
00000070  74 54 b4 41 bb aa 55 cd  13 5a 52 72 49 81 fb 55  |tT.A..U..ZRrI..U|
00000080  aa 75 43 a0 41 7c 84 c0  75 05 83 e1 01 74 37 66  |.uC.A|..u....t7f|
00000090  8b 4c 10 be 05 7c c6 44  ff 01 66 8b 1e 44 7c c7  |.L...|.D..f..D|.|
000000a0  04 10 00 c7 44 02 01 00  66 89 5c 08 c7 44 06 00  |....D...f.\..D..|
000000b0  70 66 31 c0 89 44 04 66  89 44 0c b4 42 cd 13 72  |pf1..D.f.D..B..r|
000000c0  05 bb 00 70 eb 7d b4 08  cd 13 73 0a f6 c2 80 0f  |...p.}....s.....|
000000d0  84 f0 00 e9 8d 00 be 05  7c c6 44 ff 00 66 31 c0  |........|.D..f1.|
000000e0  88 f0 40 66 89 44 04 31  d2 88 ca c1 e2 02 88 e8  |..@f.D.1........|
000000f0  88 f4 40 89 44 08 31 c0  88 d0 c0 e8 02 66 89 04  |..@.D.1......f..|
00000100  66 a1 44 7c 66 31 d2 66  f7 34 88 54 0a 66 31 d2  |f.D|f1.f.4.T.f1.|
00000110  66 f7 74 04 88 54 0b 89  44 0c 3b 44 08 7d 3c 8a  |f.t..T..D.;D.}<.|
00000120  54 0d c0 e2 06 8a 4c 0a  fe c1 08 d1 8a 6c 0c 5a  |T.....L......l.Z|
00000130  8a 74 0b bb 00 70 8e c3  31 db b8 01 02 cd 13 72  |.t...p..1......r|
00000140  2a 8c c3 8e 06 48 7c 60  1e b9 00 01 8e db 31 f6  |*....H|`......1.|
00000150  31 ff fc f3 a5 1f 61 ff  26 42 7c be 7f 7d e8 40  |1.....a.&B|..}.@|
00000160  00 eb 0e be 84 7d e8 38  00 eb 06 be 8e 7d e8 30  |.....}.8.....}.0|
00000170  00 be 93 7d e8 2a 00 eb  fe 47 52 55 42 20 00 47  |...}.*...GRUB .G|
00000180  65 6f 6d 00 48 61 72 64  20 44 69 73 6b 00 52 65  |eom.Hard Disk.Re|
00000190  61 64 00 20 45 72 72 6f  72 00 bb 01 00 b4 0e cd  |ad. Error.......|
000001a0  10 ac 3c 00 75 f4 c3 00  00 00 00 00 00 00 00 00  |..<.u...........|
000001b0  00 00 00 00 00 00 00 00  40 e2 01 00 00 00 80 00  |........@.......|
000001c0  02 00 83 fe 3f 86 01 00  00 00 c6 17 21 00 00 00  |....?.......!...|
000001d0  01 87 8e fe ff ff c7 17  21 00 4d d3 de 00 00 00  |........!.M.....|
000001e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 55 aa  |..............U.|
```

Links
-----
* [C/C++ reference](https://en.cppreference.com/)
