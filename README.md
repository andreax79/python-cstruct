Python-CStruct
==============

C-style structs for Python

Convert C struct definitions into Python classes with methods for
serializing/deserializing.
The usage is very simple: create a class subclassing cstruct.CStruct
and add a C struct definition as a string in the __struct__ field.
The C struct definition is parsed at runtime and the struct format string
is generated. The class offers the method "unpack" for deserializing
a string of bytes into a Python object and the method "pack" for
serializing the values into a string.

Example
-------

The following program reads the DOS partition information from a disk.

```python
#!/usr/bin/python
import cstruct

class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned char head;
        unsigned char sector;
        unsigned char cyl;
    """

class Partition(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    """

    def print_info(self):
        print("bootable: %s" % ((self.status & 0x80) and "Y" or "N"))
        print("partition_type: %02X" % self.partition_type)
        print("start: head: %X sectory: %X cyl: %X" % (self.start.head, self.start.sector, self.start.cyl))
        print("end: head: %X sectory: %X cyl: %X" % (self.end.head, self.end.sector, self.end.cyl))
        print("starting sector: %08X" % self.start_sect)
        print("size MB: %s" % (self.sectors / 2 / 1024))

class MBR(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        char unused[440];
        unsigned char disk_signature[4];
        unsigned char usualy_nulls[2];
        struct Partition partitions[4];
        char signature[2];
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
    data = f.read(len(mbr))
    mbr.unpack(data)
    mbr.print_info()
```

