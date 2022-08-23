#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from cstruct import MemCStruct
from pathlib import Path


class FlexArray(MemCStruct):
    __struct__ = """
      int length;
      uint32 checksum;
      long data[];
    """

    def set_length(self, length):
        self.length = length
        self.set_flexible_array_length(length)


def write(filename, length):
    print("---write---")
    flex = FlexArray()
    flex.set_length(length)
    # Generate random data
    flex.data = [random.randint(0, 2**63) for _ in range(0, length)]
    # Calculate the checksum
    flex.checksum = 0
    for num in flex.data:
        flex.checksum = (flex.checksum + num) % 2**32
    print(f"checksum: {flex.checksum}")
    # Write data
    with Path(filename).open("wb") as f:
        f.write(flex.pack())


def read(filename):
    print("---read---")
    with Path(filename).open("rb") as f:
        # Read the header
        flex = FlexArray(f)
        print(f"length: {flex.length}, checksum: {flex.checksum}")
        # Read header and data
        f.seek(0, 0)
        flex.unpack(f, flexible_array_length=flex.length)
        if len(flex.data) == flex.length:
            print("length ok")
        # Check the checksum
        checksum = 0
        for num in flex.data:
            checksum = (checksum + num) % 2**32
        if flex.checksum == checksum:
            print("checksum ok")


def main():
    filename = "tempfile"
    random.seed(5)
    write(filename, 1000)
    read(filename)


if __name__ == "__main__":
    main()
