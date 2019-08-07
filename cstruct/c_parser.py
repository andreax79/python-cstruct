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

import re
import struct
from .base import (
    NATIVE_ORDER,
    DEFINES,
    TYPEDEFS,
    STRUCTS,
    C_TYPE_TO_FORMAT
)

__all__ = [
    'FieldType',
    'Tokens',
    'parse_struct'
]

def align(__byte_order__):
    return __byte_order__ is None or __byte_order__ == NATIVE_ORDER

class FieldType(object):

    def __init__(self, vtype, vlen, vsize, fmt, offset, flexible_array):
        """
        Struct/Union field

        :param vtype: field type
        :param vlen: number of elements
        :param vsize: size in bytes
        :param fmt: struct format prefixed by byte order
        :param offset: relative memory position of the field (relative to the struct)
        :param flexible_array: True for flexible arrays
        """
        self.vtype = vtype
        self.vlen = vlen
        self.vsize = vsize
        self.fmt = fmt
        self.offset = offset
        self.flexible_array = flexible_array

    def unpack_from(self, buffer, offset=0):
        if self.flexible_array: # TODO
            raise NotImplementedError("Flexible array member are not supported") # pragma: no cover
        if isinstance(self.vtype, type): # is class
            if self.vlen == 1: # single struct/union
                result = self.vtype()
                result.unpack_from(buffer, self.offset + offset)
                return result
            else: # multiple struct/union
                result = []
                for j in range(0, self.vlen):
                    sub_struct = self.vtype()
                    sub_struct.unpack_from(buffer, self.offset + offset + j * sub_struct.size)
                    result.append(sub_struct)
                return result
        else:
            result = struct.unpack_from(self.fmt, buffer, self.offset + offset)
            if self.is_array:
                return list(result)
            else:
                return result[0]

    def pack(self, data):
        if self.is_array:
            return struct.pack(self.fmt, *data)
        else:
            return struct.pack(self.fmt, data)

    @property
    def is_array(self):
        return not (self.vlen == 1 or self.vtype == 'char')


class Tokens():

    def __init__(self, __struct__):
        # remove the comments
        st = __struct__.replace("*/","*/\n")
        st = "  ".join(re.split("/\*.*\*/",st))
        st = "\n".join([s.split("//")[0] for s in st.split("\n")])
        st = (st.replace("\n", " ")
                .replace(";", " ; ")
                .replace("{", " { ")
                .replace("}", " } "))
        self.tokens = st.split()

    def pop(self):
        return self.tokens.pop(0)

    def get(self):
        return self.tokens[0]

    def push(self, value):
        return self.tokens.insert(0, value)

    def __len__(self):
        return len(self.tokens)

    def __str__(self):
        return str(self.tokens)


def parse_type(tokens, __cls__, __byte_order__):
    if len(tokens) < 2:
        raise Exception("Parsing error")
    vtype = tokens.pop()
    # signed/unsigned/struct
    if vtype in ['signed', 'unsigned', 'struct', 'union'] and len(tokens) > 1:
        vtype = vtype + " " + tokens.pop()
    next_token = tokens.pop()
    # short int, long int, or long long
    if next_token in ['int', 'long']:
        vtype = vtype + " " + next_token
        next_token = tokens.pop()
    # void *
    if next_token.startswith("*"):
        next_token = next_token[1:]
        vtype = 'void *'
    # parse length
    vlen = 1
    flexible_array = False
    if "[" in next_token:
        t = next_token.split("[")
        if len(t) != 2:
            raise Exception("Error parsing: " + next_token)
        next_token = t[0].strip()
        vlen = t[1]
        vlen = vlen.split("]")[0].strip()
        if not vlen:
            flexible_array = True
            vlen = 0
        else:
            try:
                vlen = int(vlen)
            except:
                vlen = DEFINES.get(vlen, None)
                if vlen is None:
                    raise
                else:
                    vlen = int(vlen)
    tokens.push(next_token)
    # resolve typedefs
    while vtype in TYPEDEFS:
        vtype = TYPEDEFS[vtype]
    # calculate fmt
    if vtype.startswith('struct ') or vtype.startswith('union '): # struct/union
        __is_union__ = vtype.startswith('union ')
        kind, vtype = vtype.split(' ', 1)
        if tokens.get() == '{': # Named nested struct
            tokens.pop()
            vtype = __cls__.parse(tokens, __name__=vtype, __is_union__=__is_union__, __byte_order__=__byte_order__)
        elif vtype == '{': # Unnamed nested struct
            vtype = __cls__.parse(tokens, __is_union__=__is_union__, __byte_order__=__byte_order__)
        else:
            try:
                vtype = STRUCTS[vtype]
            except KeyError:
                raise Exception("Unknow %s \"%s\"" % (kind, vtype))
        ttype = "c"
        fmt = str(vlen * vtype.size) + ttype
        # alignment/
        alignment = vtype.__alignment__
    else: # other types
        ttype = C_TYPE_TO_FORMAT.get(vtype, None)
        if ttype is None:
            raise Exception("Unknow type \"" + vtype + "\"")
        fmt = (str(vlen) if vlen > 1 or flexible_array else '') + ttype
        # alignment
        alignment = struct.calcsize((__byte_order__ + ttype) if __byte_order__ is not None else ttype)
    fmt = (__byte_order__ + fmt) if __byte_order__ is not None else fmt
    vsize = struct.calcsize(fmt)
    return vtype, vlen, vsize, fmt, flexible_array, alignment


def parse_struct(__struct__, __cls__=None, __fields__=None, __is_union__=False, __byte_order__=None, **kargs):
    # naive C struct parsing
    __is_union__ = bool(__is_union__)
    fields = []
    fields_types = {}
    flexible_array = False
    offset = 0
    max_alignment = 0
    if isinstance(__struct__, Tokens):
        tokens = __struct__
    else:
        tokens = Tokens(__struct__)
    while len(tokens):
        if tokens.get() == '}':
            tokens.pop()
            break
        # flexible array member must be the last member of such a struct
        if flexible_array:
            raise Exception("Flexible array member must be the last member of such a struct")
        vtype, vlen, vsize, fmt, flexible_array, alignment = parse_type(tokens, __cls__, __byte_order__)
        vname = tokens.pop()
        fields.append(vname)
        # calculate the max field size (for the alignment)
        max_alignment = max(max_alignment, alignment)
        # align stuct if byte order is native
        if not __is_union__ and align(__byte_order__) and vtype != 'char':
            modulo = offset % alignment
            if modulo: # not aligned to the field size
                delta = alignment - modulo
                offset = offset + delta
        fields_types[vname] = FieldType(vtype, vlen, vsize, fmt, offset, flexible_array)
        if not __is_union__: # C struct
            offset = offset + vsize
        t = tokens.pop()
        if t != ';':
            raise(Exception("; expected but %s found" % t))

    if __is_union__: # C union
        # Calculate the union size as size of its largest element
        size = max([struct.calcsize(x.fmt) for x in fields_types.values()])
        fmt = '%ds' % size
    else: # C struct
        fmt = "".join(fmt)
        # add padding to stuct if byte order is native
        if not __is_union__ and align(__byte_order__):
            modulo = offset % max_alignment
            if modulo: # not aligned to the max field size
                delta = max_alignment - modulo
                offset = offset + delta
        size = offset # (offset is calculated as size sum)

    # Add the byte order as prefix
    if __byte_order__ is not None:
        fmt = __byte_order__ + fmt

    # Prepare the result
    result = {
        '__fields__': fields,
        '__fields_types__': fields_types,
        '__size__': size,
        '__is_union__': __is_union__,
        '__byte_order__': __byte_order__,
        '__alignment__': max_alignment
    }

    # Add the missing fields to the class
    for field in __fields__ or []:
        if field not in dict:
            result[field] = None
    return result
