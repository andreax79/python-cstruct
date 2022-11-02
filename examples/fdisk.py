#!/usr/bin/env python

from pathlib import Path
import argparse
import cstruct
import sys

UNITS = ['B', 'K', 'M', 'G', 'T']
SECTOR_SIZE = 512
TYPES = {
    0x00: "Empty",
    0x01: "FAT12",
    0x05: "Extended",
    0x06: "FAT16",
    0x07: "HPFS/NTFS/exFAT",
    0x0B: "W95 FAT32",
    0x0C: "W95 FAT32 (LBA)",
    0x0E: "W95 FAT16 (LBA)",
    0x0F: "W95 extended (LBA)",
    0x11: "Hidden FAT12",
    0x14: "Hidden FAT16 <32M",
    0x16: "Hidden FAT16",
    0x17: "Hidden HPFS/NTFS",
    0x1B: "Hidden W95 FAT32",
    0x1C: "Hidden W95 FAT32 (LBA)",
    0x1E: "Hidden W95 FAT16 (LBA)",
    0x27: "Hidden NTFS WinRE",
    0x81: "Minix / old Linux",
    0x82: "Linux swap / Solaris",
    0x83: "Linux",
    0x85: "Linux extended",
    0x86: "NTFS volume set",
    0x87: "NTFS volume set",
    0x88: "Linux plaintext",
    0x8E: "Linux LVM",
    0x9F: "BSD/OS",
    0xA5: "FreeBSD",
    0xA6: "OpenBSD",
    0xAF: "HFS / HFS+",
    0xEA: "Linux extended boot",
    0xEE: "GPT",
    0xEF: "EFI (FAT-12/16/32)",
    0xF2: "DOS secondary",
    0xFB: "VMware VMFS",
    0xFC: "VMware VMKCORE",
    0xFD: "Linux raid autodetect",
}


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

    @property
    def bootable_str(self):
        return "*" if (self.status & cstruct.getdef("ACTIVE_FLAG")) else " "

    @property
    def end_sect(self):
        return self.start_sect + self.sectors - 1

    @property
    def part_size_str(self):
        val = self.sectors * SECTOR_SIZE
        for unit in UNITS:
            if val < 1000:
                break
            val = int(val / 1000)
        return f"{val}{unit}"

    @property
    def part_type_str(self):
        return TYPES.get(self.partition_type, "")

    def __str__(self):
        return f"{self.bootable_str} {self.start_sect:>10} {self.end_sect:>8} {self.sectors:>8} {self.part_size_str:>4} {self.partition_type:02x} {self.part_type_str}"


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
        print(f"Sector size: {cstruct.getdef('MBR_SIZE')}")
        if self.signature != cstruct.getdef('MBR_BOOT_SIGNATURE'):
            print("Invalid MBR signature")

        print(f"Disk identifier: 0x{self.disk_signature_str}")
        print()
        print("Device Boot   Start      End  Sectors Size Id Type")
        for i, partition in enumerate(self.partitions):
            if partition.sectors:
                print(f"part{i:<2} {partition}")


def main():
    parser = argparse.ArgumentParser(description="Display or manipulate a disk partition table.")
    parser.add_argument("disk")
    args = parser.parse_args()

    try:
        with Path(args.disk).open("rb") as f:
            mbr = MBR()
            data = f.read(len(mbr))
            mbr.unpack(data)
            mbr.print_info()
    except (IOError, OSError) as ex:
        print(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
