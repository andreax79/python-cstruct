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

from .base import STRUCTS
from .c_parser import parse_struct

__all__ = [
    'CStructMeta',
    'AbstractCStruct'
]

class CStructMeta(type):

    def __new__(mcs, name, bases, dict):
        __struct__ = dict.get("__struct__", None)
        dict['__cls__'] = bases[0]
        # Parse the struct
        if __struct__ is not None:
            dict.update(parse_struct(**dict))
        # Create the new class
        new_class = type.__new__(mcs, name, bases, dict)
        # Register the class
        if __struct__ is not None and not dict.get('__anonymous__'):
            STRUCTS[name] = new_class
        return new_class

    def __len__(cls):
        return cls.__size__

    @property
    def size(cls):
        """ Structure size (in bytes) """
        return cls.__size__

# Workaround for Python 2.x/3.x metaclass, thanks to
# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/#using-the-metaclass-in-python-2-x-and-3-x
_CStructParent = CStructMeta('_CStructParent', (object, ), {})


class AbstractCStruct(_CStructParent):

    def __init__(self, string=None, **kargs):
        if string is not None:
            self.unpack(string)
        else:
            try:
                self.unpack(string)
            except:
                pass
        for key, value in kargs.items():
            setattr(self, key, value)

    def unpack(self, buffer):
        """
        Unpack the string containing packed C structure data
        """
        return self.unpack_from(buffer)

    def unpack_from(self, buffer, offset=0): # pragma: no cover
        """
        Unpack the string containing packed C structure data
        """
        return NotImplemented

    def pack(self): # pragma: no cover
        """
        Pack the structure data into a string
        """
        return NotImplemented

    def clear(self):
        self.unpack(None)

    def __len__(self):
        """ Structure size (in bytes) """
        return self.__size__

    @property
    def size(self):
        """ Structure size (in bytes) """
        return self.__size__

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = []
        for field in self.__fields__:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"

    def __repr__(self): # pragma: no cover
        return self.__str__()


