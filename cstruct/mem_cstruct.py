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

from typing import Any, List, Optional
import ctypes
import struct
from .abstract import AbstractCStruct


class CStructList(List[Any]):
    def __init__(self, values: List[Any], name: str, parent: Optional["MemCStruct"] = None) -> None:
        super().__init__(values)
        self.name = name
        self.parent = parent

    def __setitem__(self, key: int, value: List[Any]) -> None:  # noqa: F811
        super().__setitem__(key, value)
        # Notify the parent when a value is changed
        if self.parent is not None:
            self.parent.on_change_list(self.name, key, value)


class MemCStruct(AbstractCStruct):
    """
    Convert C struct definitions into Python classes.

    Attributes:
        __struct__ (str): definition of the struct (or union) in C syntax
        __byte_order__ (str): byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
        __is_union__ (bool): True for union definitions, False for struct definitions
        __mem__: mutable character buffer
        __size__ (int): size of the structure in bytes (flexible array member size is omitted)
        __fields__ (list): list of structure fields
        __fields_types__ (dict): dictionary mapping field names to types
    """

    __mem__ = None

    def unpack_from(self, buffer: Optional[bytes], offset: int = 0, flexible_array_length: Optional[int] = None) -> bool:
        """
        Unpack bytes containing packed C structure data

        Args:
            buffer: bytes to be unpacked
            offset: optional buffer offset
            flexible_array_length: optional flexible array lenght (number of elements)
        """
        self.set_flexible_array_length(flexible_array_length)
        self.__base__ = offset  # Base offset
        if buffer is None:
            # the buffer is one item larger than its size and the last element is NUL
            self.__mem__ = ctypes.create_string_buffer(self.size + 1)
        elif isinstance(buffer, ctypes.Array):
            self.__mem__ = buffer
        elif isinstance(buffer, int):
            # buffer is a pointer
            self.__mem__ = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char * self.size)).contents
        else:
            self.__mem__ = ctypes.create_string_buffer(buffer)
        for field, field_type in self.__fields_types__.items():
            if field_type.is_struct or field_type.is_union:
                setattr(self, field, field_type.unpack_from(self.__mem__, offset))
        return True

    def memcpy(self, destination: int, source: bytes, num: int) -> None:
        """
        Copies the values of num bytes from source to the struct memory

        Args:
            destination: destination address
            source: source data to be copied
            num: number of bytes to copy
        """
        ctypes.memmove(ctypes.byref(self.__mem__, destination), source, num)

    def pack(self) -> bytes:
        """
        Pack the structure data into bytes

        Returns:
            bytes: The packed structure
        """
        return self.__mem__.raw[:-1]  # the buffer is one item larger than its size and the last element is NUL

    def set_flexible_array_length(self, flexible_array_length: Optional[int]) -> None:
        """
        Set flexible array length (i.e. number of elements)

        Args:
            flexible_array_length: flexible array length
        """
        super().set_flexible_array_length(flexible_array_length)
        if self.__mem__ is not None:
            try:
                ctypes.resize(self.__mem__, self.size + 1)
            except ValueError:
                pass

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
        elif field_type.is_struct or field_type.is_union:
            object.__setattr__(self, attr, value)
        else:  # native
            if field_type.flexible_array and len(value) != field_type.vlen:
                # flexible array size changed, resize the buffer
                field_type.vlen = len(value)
                ctypes.resize(self.__mem__, self.size + 1)
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
