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

from abc import ABCMeta
from collections import OrderedDict
from typing import Any, BinaryIO, List, Dict, Optional, Type, Tuple, Union
import hashlib
from .base import STRUCTS
from .c_parser import parse_struct, parse_def, Tokens
from .field import calculate_padding, FieldType
from .exceptions import CStructException

__all__ = ['CStructMeta', 'AbstractCStruct']


class CStructMeta(ABCMeta):
    __size__: int = 0

    def __new__(metacls: Type[type], name: str, bases: Tuple[str], namespace: Dict[str, Any]) -> Type[Any]:
        __struct__ = namespace.get('__struct__', None)
        namespace['__cls__'] = bases[0] if bases else None
        # Parse the struct
        if '__struct__' in namespace:
            if isinstance(namespace['__struct__'], (str, Tokens)):
                namespace.update(parse_struct(**namespace))
            __struct__ = True
        if '__def__' in namespace:
            namespace.update(parse_def(**namespace))
            __struct__ = True
        # Create the new class
        new_class: Type[Any] = super().__new__(metacls, name, bases, namespace)
        # Register the class
        if __struct__ is not None and not namespace.get('__anonymous__'):
            STRUCTS[name] = new_class
        return new_class

    def __len__(cls) -> int:
        "Structure size (in bytes)"
        return cls.__size__

    @property
    def size(cls) -> int:
        "Structure size (in bytes)"
        return cls.__size__


class AbstractCStruct(metaclass=CStructMeta):
    """
    Abstract C struct to Python class
    """

    __size__: int = 0
    " Size in bytes "
    __fields__: List[str] = []
    " Struct/union fileds "
    __fields_types__: Dict[str, FieldType]
    " Dictionary mapping field names to types "
    __byte_order__: Optional[str] = None
    " Byte order "
    __alignment__: int = 0
    " Alignament "
    __is_union__: bool = False
    " True if the class is an union, False if it is a struct "

    def __init__(
        self, buffer: Optional[Union[bytes, BinaryIO]] = None, flexible_array_length: Optional[int] = None, **kargs: Dict[str, Any]
    ) -> None:
        self.set_flexible_array_length(flexible_array_length)
        self.__fields__ = [x for x in self.__fields__]  # Create a copy
        self.__fields_types__ = OrderedDict({k: v.copy() for k, v in self.__fields_types__.items()})  # Create a copy
        if buffer is not None:
            self.unpack(buffer)
        else:
            try:
                self.unpack(buffer)
            except Exception:
                pass
        for key, value in kargs.items():
            setattr(self, key, value)

    @classmethod
    def parse(
        cls,
        __struct__: Union[str, Tokens, Dict[str, Any]],
        __name__: Optional[str] = None,
        __byte_order__: Optional[str] = None,
        __is_union__: Optional[bool] = False,
        **kargs: Dict[str, Any]
    ) -> Type["AbstractCStruct"]:
        """
        Return a new class mapping a C struct/union definition.

        Args:
            __struct__:     definition of the struct (or union) in C syntax
            __name__:       name of the new class. If empty, a name based on the __struct__ hash is generated
            __byte_order__: byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
            __is_union__:   True for union, False for struct

        Returns:
            cls: a new class mapping the defintion
        """
        cls_kargs: Dict[str, Any] = dict(kargs)
        if __byte_order__ is not None:
            cls_kargs['__byte_order__'] = __byte_order__
        if __is_union__ is not None:
            cls_kargs['__is_union__'] = __is_union__
        cls_kargs['__struct__'] = __struct__
        if isinstance(__struct__, (str, Tokens)):
            del cls_kargs['__struct__']
            cls_kargs.update(parse_def(__struct__, __cls__=cls, **cls_kargs))
            cls_kargs['__struct__'] = None
        elif isinstance(__struct__, dict):
            del cls_kargs['__struct__']
            cls_kargs.update(__struct__)
            cls_kargs['__struct__'] = None
        if __name__ is None:  # Anonymous struct
            __name__ = cls.__name__ + '_' + hashlib.sha1(str(__struct__).encode('utf-8')).hexdigest()
            cls_kargs['__anonymous__'] = True
        cls_kargs['__name__'] = __name__
        return type(__name__, (cls,), cls_kargs)

    def set_flexible_array_length(self, flexible_array_length: Optional[int]) -> None:
        """
        Set flexible array length (i.e. number of elements)

        Args:
            flexible_array_length: flexible array length

        Raises:
            CStructException: If flexible array is not present in the structure
        """
        if flexible_array_length is not None:
            # Search for the flexible array
            flexible_array: Optional[FieldType] = [x for x in self.__fields_types__.values() if x.flexible_array][0]
            if flexible_array is None:
                raise CStructException("Flexible array not found in struct")
            flexible_array.vlen = flexible_array_length

    def unpack(self, buffer: Optional[Union[bytes, BinaryIO]], flexible_array_length: Optional[int] = None) -> bool:
        """
        Unpack bytes containing packed C structure data

        Args:
            buffer: bytes or binary stream to be unpacked
            flexible_array_length: flexible array length
        """
        self.set_flexible_array_length(flexible_array_length)
        if hasattr(buffer, 'read'):
            buffer = buffer.read(self.size)  # type: ignore
            if not buffer:
                return False
        return self.unpack_from(buffer)

    def unpack_from(
        self, buffer: Optional[bytes], offset: int = 0, flexible_array_length: Optional[int] = None
    ) -> bool:  # pragma: no cover
        """
        Unpack bytes containing packed C structure data

        Args:
            buffer: bytes to be unpacked
            offset: optional buffer offset
            flexible_array_length: flexible array length
        """
        raise NotImplementedError

    def pack(self) -> bytes:  # pragma: no cover
        """
        Pack the structure data into bytes

        Returns:
            bytes: The packed structure
        """
        raise NotImplementedError

    def clear(self) -> None:
        self.unpack(None)

    def __len__(self) -> int:
        "Actual structure size (in bytes)"
        return self.size

    @property
    def size(self) -> int:
        "Actual structure size (in bytes)"
        if not self.__fields_types__:  # no fields
            return 0
        elif self.__is_union__:  # C union
            # Calculate the sizeof union as size of its largest element
            return max(x.vsize for x in self.__fields_types__.values())
        else:  # C struct
            # Calculate the sizeof struct as last item's offset + size + padding
            last_field_type = list(self.__fields_types__.values())[-1]
            size = last_field_type.offset + last_field_type.vsize
            padding = calculate_padding(self.__byte_order__, self.__alignment__, size)
            return size + padding

    @classmethod
    def sizeof(cls) -> int:
        "Structure size in bytes (flexible array member size is omitted)"
        return cls.__size__

    def __eq__(self, other: Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        result = []
        for field in self.__fields__:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __getstate__(self) -> bytes:
        """
        This method is called and the returned object is pickled
        as the contents for the instance, instead of the contents of
        the instance’s dictionary

        Returns:
            bytes: The packed structure
        """
        return self.pack()

    def __setstate__(self, state: bytes) -> bool:
        """
        This method it is called with the unpickled state

        Args:
            state: bytes to be unpacked
        """
        return self.unpack(state)
