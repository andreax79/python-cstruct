#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from typing import Optional
from .base import CHAR_ZERO
from .abstract import CStructMeta, AbstractCStruct


class CStruct(AbstractCStruct):
    """
    Convert C struct definitions into Python classes.

    __struct__ = definition of the struct (or union) in C syntax
    __byte_order__ = (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
    __is_union__ = (optional) True for union definitions, False for struct definitions (default)

    The following fields are generated from the C struct definition
    __size__ = lenght of the structure in bytes
    __fields__ = list of structure fields
    __fields_types__ = dictionary mapping field names to types
    Every fields defined in the structure is added to the class

    """

    __size__: int = 0

    def unpack_from(self, buffer: Optional[bytes], offset: int = 0) -> bool:
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes to be unpacked
        :param offset: optional buffer offset
        """
        if buffer is None:
            buffer = CHAR_ZERO * self.__size__
        for field, field_type in self.__fields_types__.items():
            setattr(self, field, field_type.unpack_from(buffer, offset))
        return True

    def pack(self) -> bytes:
        """
        Pack the structure data into bytes
        """
        result = []
        for field in self.__fields__:
            field_type = self.__fields_types__[field]
            if isinstance(field_type.vtype, CStructMeta):
                if field_type.vlen == 1:  # single struct
                    v = getattr(self, field, field_type.vtype())
                    v = v.pack()
                    result.append(v)
                else:  # multiple struct
                    values = getattr(self, field, [])
                    for j in range(0, field_type.vlen):
                        try:
                            v = values[j]
                        except:
                            v = field_type.vtype()
                        v = v.pack()
                        result.append(v)
            else:
                data = getattr(self, field)
                result.append(field_type.pack(data))
        return bytes().join(result)
