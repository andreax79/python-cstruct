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

__author__  = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__license__ = 'MIT'
__version__ = '1.9'
__date__ = '15 August 2013'

import struct
import hashlib
from .base import (
    STRUCTS,
    DEFINES,
    TYPEDEFS,
    C_TYPE_TO_FORMAT,
    CHAR_ZERO,
    EMPTY_BYTES_STRING
)
from .c_parser import Tokens
from .abstract import CStructMeta
from .cstruct import CStruct
from .mem_cstruct import MemCStruct

__all__ = [
    'LITTLE_ENDIAN',
    'BIG_ENDIAN',
    'CHAR_ZERO',
    'EMPTY_BYTES_STRING',
    'CStruct',
    'MemCStruct',
    'define',
    'undef',
    'typedef',
    'sizeof',
    'factory'
]

# little-endian, std. size & alignment
LITTLE_ENDIAN = '<'
# big-endian, std. size & alignment
BIG_ENDIAN = '>'
# native order, size & alignment
NATIVE_ORDER = '@'

def define(key, value):
    """
    Define a constant that can be used in the C struct

    :param key: identifier
    :param value: value of the constant
    """
    DEFINES[key] = value

def undef(key):
    """
    Undefine a symbol that was previously defined with define

    :param key: identifier
    """
    del DEFINES[key]

def typedef(type_, alias):
    """
    Define an alias name for a data type

    :param type_: data type
    :param alias: new alias name
    """
    TYPEDEFS[alias] = type_

def sizeof(type_):
    """
    Return the size of the type.

    :param type_: C type, struct or union (e.g. 'short int' or 'struct ZYZ')
    :return: size in bytes
    """
    while type_ in TYPEDEFS:
        type_ = TYPEDEFS[type_]
    if isinstance(type_, CStructMeta):
        return len(type_)
    elif type_.startswith('struct ') or type_.startswith('union '):
        kind, type_ = type_.split(' ', 1)
        t = STRUCTS.get(type_, None)
        if t is None:
            raise KeyError("Unknow %s \"%s\"" % (kind, type_))
        else:
            return t.size
    else:
        ttype = C_TYPE_TO_FORMAT.get(type_, None)
        if ttype is None:
            raise KeyError("Unknow type \"" + type_ + "\"")
        else:
            return struct.calcsize(ttype)

def factory(__struct__, __cls__=None, __name__=None, **kargs):
    """
    Return a new class mapping a C struct definition.

    :param __struct__:     definition of the struct (or union) in C syntax
    :param __cls__:        (optional) super class - CStruct(default) or MemCStruct
    :param __name__:       (optional) name of the new class. If empty, a name based on the __struct__ hash is generated
    :param __byte_order__: (optional) byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
    :param __is_union__:   (optional) True for union, False for struct (default)
    :returns:              __cls__ subclass
    """
    kargs = dict(kargs)
    if not isinstance(__struct__, Tokens):
        __struct__ = Tokens(__struct__)
    kargs['__struct__'] = __struct__
    if __name__ is None: # Anonymous struct
        __name__ = 'CStruct%s' % hashlib.sha1(str(__struct__).encode('utf-8')).hexdigest()
        kargs['__anonymous__'] = True
    kargs['__name__'] = __name__
    if __cls__ is None:
        __cls__ = CStruct
    return type(__name__, (__cls__,), kargs) # TODO


