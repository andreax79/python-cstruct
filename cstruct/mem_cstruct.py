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

from typing import Any, List, Optional
import ctypes
import struct
from .abstract import CStructMeta, AbstractCStruct


class CStructList(List[Any]):
    def __init__(self, values: List[Any], name: str, parent: Optional['MemCStruct'] = None) -> None:
        super().__init__(values)
        self.name = name
        self.parent = parent

    def __setitem__(self, key: int, value: List[Any]) -> None:
        super().__setitem__(key, value)
        # Notify the parent when a value is changed
        if self.parent is not None:
            self.parent.on_change_list(self.name, key, value)


class MemCStruct(AbstractCStruct):
    """
    Convert C struct definitions into Python classes.

    __struct__ = definition of the struct (or union) in C syntax
    __byte_order__ = (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
    __is_union__ = (optional) True for union definitions, False for struct definitions (default)

    The following fields are generated from the C struct definition
    __mem_ = mutable character buffer
    __size__ = lenght of the structure in bytes
    __fields__ = list of structure fields
    __fields_types__ = dictionary mapping field names to types
    Every fields defined in the structure is added to the class

    """

    __size__: int = 0
    __mem__: ctypes.Array

    def unpack_from(self, buffer: Optional[bytes], offset: int = 0) -> bool:
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes to be unpacked
        :param offset: optional buffer offset
        """
        self.__base__ = offset  # Base offset
        if buffer is None:
            # the buffer is one item larger than its size and the last element is NUL
            self.__mem__ = ctypes.create_string_buffer(self.__size__ + 1)
        elif isinstance(buffer, ctypes.Array):
            self.__mem__ = buffer
        else:
            self.__mem__ = ctypes.create_string_buffer(buffer)
        for field, field_type in self.__fields_types__.items():
            if field_type.flexible_array:  # TODO
                raise NotImplementedError("Flexible array member are not supported")  # pragma: no cover
            if isinstance(field_type.vtype, CStructMeta):
                setattr(self, field, field_type.unpack_from(self.__mem__, offset))
        return True

    def memcpy(self, destination: int, source: bytes, num: int) -> None:
        """
        Copies the values of num bytes from source to the struct memory

        :param destination: destination address
        :param source: source data to be copied
        :param num: number of bytes to copy
        """
        ctypes.memmove(ctypes.byref(self.__mem__, destination), source, num)

    def pack(self) -> bytes:
        """
        Pack the structure data into bytes
        """
        return self.__mem__.raw[:-1]  # the buffer is one item larger than its size and the last element is NUL

    def __getattr__(self, attr: str) -> Any:
        field_type = self.__fields_types__[attr]
        result = field_type.unpack_from(self.__mem__, self.__base__)
        if isinstance(result, list):
            return CStructList(result, name=attr, parent=self)
        else:
            return result

    def __setattr__(self, attr: str, value: Any) -> None:
        field_type = self.__fields_types__.get(attr)
        if field_type is None:
            object.__setattr__(self, attr, value)
        else:
            if isinstance(field_type.vtype, CStructMeta):
                object.__setattr__(self, attr, value)
            else:
                addr = field_type.offset + self.__base__
                self.memcpy(addr, field_type.pack(value), field_type.vsize)

    def on_change_list(self, attr: str, key: int, value: Any) -> None:
        field_type = self.__fields_types__[attr]
        # Calculate the single field format and size
        fmt = (self.__byte_order__ + field_type.fmt[-1]) if self.__byte_order__ is not None else field_type.fmt[-1]
        size = struct.calcsize(fmt)
        # Calculate the single field memory position
        addr = field_type.offset + self.__base__ + size * key
        # Update the memory
        self.memcpy(addr, struct.pack(fmt, value), size)
