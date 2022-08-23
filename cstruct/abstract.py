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
from typing import cast, Any, BinaryIO, Optional, Type, Union
from .base import STRUCTS
import hashlib
from .c_parser import parse_struct, parse_def, Tokens

__all__ = ['CStructMeta', 'AbstractCStruct']


class CStructMeta(ABCMeta):
    def __new__(cls, name: str, bases, dct):
        __struct__ = dct.get("__struct__", None)
        dct['__cls__'] = bases[0]
        # Parse the struct
        if '__struct__' in dct:
            if isinstance(dct['__struct__'], ("".__class__, u"".__class__, Tokens)):
                dct.update(parse_struct(**dct))
            __struct__ = True
        if '__def__' in dct:
            dct.update(parse_def(**dct))
            __struct__ = True
        # Create the new class
        new_class = type.__new__(cls, name, bases, dct)
        # Register the class
        if __struct__ is not None and not dct.get('__anonymous__'):
            STRUCTS[name] = new_class
        return new_class

    def __len__(cls) -> int:
        return cls.__size__

    @property
    def size(cls) -> int:
        """Structure size (in bytes)"""
        return cls.__size__


# Workaround for Python 2.x/3.x metaclass, thanks to
# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/#using-the-metaclass-in-python-2-x-and-3-x
_CStructParent = CStructMeta('_CStructParent', (object,), {})


class AbstractCStruct(_CStructParent):
    def __init__(self, buffer=None, **kargs) -> None:
        if buffer is not None:
            self.unpack(buffer)
        else:
            try:
                self.unpack(buffer)
            except:
                pass
        for key, value in kargs.items():
            setattr(self, key, value)

    @classmethod
    def parse(cls, __struct__, __name__: Optional[str] = None, **kargs) -> Type[Any]:
        """
        Return a new class mapping a C struct/union definition.

        :param __struct__:     definition of the struct (or union) in C syntax
        :param __name__:       (optional) name of the new class. If empty, a name based on the __struct__ hash is generated
        :param __byte_order__: (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
        :param __is_union__:   (optional) True for union, False for struct (default)
        :returns:              cls subclass
        """
        kargs = dict(kargs)
        kargs['__struct__'] = __struct__
        if isinstance(__struct__, ("".__class__, u"".__class__, Tokens)):
            del kargs['__struct__']
            kargs.update(parse_def(__struct__, __cls__=cls, **kargs))
            kargs['__struct__'] = None
        if __name__ is None:  # Anonymous struct
            __name__ = cls.__name__ + '_' + hashlib.sha1(str(__struct__).encode('utf-8')).hexdigest()
            kargs['__anonymous__'] = True
        kargs['__name__'] = __name__
        return type(__name__, (cls,), kargs)

    def unpack(self, buffer: Optional[Union[bytes, BinaryIO]]) -> bool:
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes or binary stream to be unpacked
        """
        if hasattr(buffer, 'read'):
            buffer = buffer.read(self.__size__)
            if not buffer:
                return False
        return self.unpack_from(buffer)

    def unpack_from(self, buffer: Optional[bytes], offset: int = 0) -> bool:  # pragma: no cover
        """
        Unpack bytes containing packed C structure data

        :param buffer: bytes to be unpacked
        :param offset: optional buffer offset
        """
        raise NotImplementedError

    def pack(self) -> bytes:  # pragma: no cover
        """
        Pack the structure data into bytes
        """
        raise NotImplementedError

    def clear(self) -> None:
        self.unpack(None)

    def __len__(self) -> int:
        """Structure size (in bytes)"""
        return cast(int, self.__size__)

    @property
    def size(self) -> int:
        """Structure size (in bytes)"""
        return self.__size__

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        result = []
        for field in self.__fields__:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()
