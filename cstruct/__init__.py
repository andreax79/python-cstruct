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

__author__ = "Andrea Bonomi <andrea.bonomi@gmail.com>"
__license__ = "MIT"
__version__ = "5.1"
__date__ = "15 August 2013"

from typing import Any, Dict, Optional, Type, Union
from .base import (
    LITTLE_ENDIAN,
    BIG_ENDIAN,
    NATIVE_ORDER,
    STRUCTS,
    ENUMS,
    DEFINES,
    TYPEDEFS,
    CHAR_ZERO,
)
from .abstract import CStructMeta, AbstractCStruct, AbstractCEnum
from .cstruct import CStruct
from .c_parser import parse_struct_def
from .mem_cstruct import MemCStruct
from .cenum import CEnum
from .native_types import get_native_type

__all__ = [
    "LITTLE_ENDIAN",
    "BIG_ENDIAN",
    "NATIVE_ORDER",
    "CHAR_ZERO",
    "CStruct",
    "MemCStruct",
    "CEnum",
    "define",
    "undef",
    "getdef",
    "typedef",
    "get_type",
    "sizeof",
    "parse",
]


def define(key: str, value: Any) -> None:
    """
    Define a constant that can be used in the C struct

    Examples:
        >>> define("INIT_THREAD_SIZE", 16384)

    Args:
        key: identifier
        value: value of the constant
    """
    DEFINES[key] = value


def undef(key: str) -> None:
    """
    Undefine a symbol that was previously defined with define

    Examples:
        >>> define("INIT_THREAD_SIZE", 16384)
        >>> undef("INIT_THREAD_SIZE")

    Args:
        key: identifier

    Raises:
        KeyError: If key is not defined
    """
    del DEFINES[key]


def getdef(key: str) -> Any:
    """
    Return the value for a constant

    Examples:
        >>> define("INIT_THREAD_SIZE", 16384)
        >>> getdef("INIT_THREAD_SIZE")

    Args:
        key: identifier

    Raises:
        KeyError: If key is not defined
    """
    return DEFINES[key]


def typedef(type_: str, alias: str) -> None:
    """
    Define an alias name for a data type

    Examples:
        >>> typedef("int", "status")
        >>> sizeof("status")
        4

    Args:
        type_: data type
        alias: new alias name
    """
    TYPEDEFS[alias] = type_


def get_type(type_: str) -> Any:
    """
    Get a data type (struct, union, enum) by name

    Examples:
        >>> get_type("struct Position")
        <class 'abc.Position'>
        >>> get_type("enum htmlfont")
        <enum 'htmlfont'>

    Args:
        type_: C type, struct or union (e.g. 'short int' or 'struct ZYZ'), enum or native type

    Returns:
        class: data type class

    Raises:
        KeyError: If type is not defined
    """
    while type_ in TYPEDEFS:
        type_ = TYPEDEFS[type_]
    if isinstance(type_, CStructMeta):
        return type_
    elif type_.startswith("struct ") or type_.startswith("union "):
        kind, type_ = type_.split(" ", 1)
        try:
            return STRUCTS[type_]
        except KeyError:
            raise KeyError(f"Unknown {kind} `{type_}`")
    elif type_.startswith("enum "):
        kind, type_ = type_.split(" ", 1)
        try:
            return ENUMS[type_]
        except KeyError:
            raise KeyError(f"Unknown {kind} `{type_}`")
    else:
        return get_native_type(type_)


def sizeof(type_: str) -> int:
    """
    Return the size of the type.

    Examples:
        >>> sizeof("struct Position")
        16
        >>> sizeof('enum htmlfont')
        4
        >>> sizeof("int")
        4

    Args:
        type_: C type, struct or union (e.g. 'short int' or 'struct ZYZ'), enum or native type

    Returns:
        size: size in bytes

    Raises:
        KeyError: If type is not defined
    """
    while type_ in TYPEDEFS:
        type_ = TYPEDEFS[type_]
    data_type = get_type(type_)
    return data_type.sizeof()


def parse(
    __struct__: str, __cls__: Optional[Type[AbstractCStruct]] = None, **kargs: Dict[str, Any]
) -> Union[Type[AbstractCStruct], Type[AbstractCEnum], None]:
    """
    Return a new class mapping a C struct/union/enum definition.
    If the string does not contains any definition, return None.
    If the string contains multiple struct/union/enum definitions, returns the last definition.

    Examples:
        >>> cstruct.parse('struct Pair { unsigned char a; unsigned char b; };')
        <class 'abc.Pair'>

    Args:
        __struct__ (str): definition of the struct (or union/enum) in C syntax
        __cls__ (type): super class - CStruct(default) or MemCStruct
        __byte_order__ (str): byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER

    Returns:
        cls: __cls__ subclass

    Raises:
        cstruct.exceptions.ParserError: Parsing exception

    """
    if __cls__ is None:
        __cls__ = MemCStruct
    cls_def = parse_struct_def(__struct__, __cls__=__cls__, process_muliple_definition=True, **kargs)
    if cls_def is None:
        return None
    return cls_def["__cls__"].parse(cls_def, **kargs)
