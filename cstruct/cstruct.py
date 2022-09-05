#!/usr/bin/env python
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

from typing import List, Optional
from .base import CHAR_ZERO
from .abstract import AbstractCStruct


class CStruct(AbstractCStruct):
    """
    Convert C struct definitions into Python classes.

    Attributes:
        __struct__ (str): definition of the struct (or union) in C syntax
        __byte_order__ (str): byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
        __is_union__ (bool): True for union definitions, False for struct definitions
        __size__ (int): size of the structure in bytes (flexible array member size is omitted)
        __fields__ (list): list of structure fields
        __fields_types__ (dict): dictionary mapping field names to types
    """

    def unpack_from(self, buffer: Optional[bytes], offset: int = 0, flexible_array_length: Optional[int] = None) -> bool:
        """
        Unpack bytes containing packed C structure data

        Args:
            buffer: bytes to be unpacked
            offset: optional buffer offset
            flexible_array_length: optional flexible array lenght (number of elements)
        """
        self.set_flexible_array_length(flexible_array_length)
        if buffer is None:
            buffer = CHAR_ZERO * self.size
        for field, field_type in self.__fields_types__.items():
            setattr(self, field, field_type.unpack_from(buffer, offset))
        return True

    def pack(self) -> bytes:
        """
        Pack the structure data into bytes

        Returns:
            bytes: The packed structure
        """
        result: List[bytes] = []
        for field, field_type in self.__fields_types__.items():
            if field_type.is_struct or field_type.is_union:
                if field_type.vlen == 1:  # single struct
                    v = getattr(self, field, field_type.ref())
                    v = v.pack()
                    result.append(v)
                else:  # multiple struct
                    values = getattr(self, field, [])
                    for j in range(0, field_type.vlen):
                        try:
                            v = values[j]
                        except KeyError:
                            v = field_type.ref()
                        v = v.pack()
                        result.append(v)
            else:
                data = getattr(self, field)
                result.append(field_type.pack(data))
        return bytes().join(result)
