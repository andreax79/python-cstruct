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

import re
from collections import OrderedDict
from typing import Union, Optional, Any, Dict, List, Type, TYPE_CHECKING
from .base import DEFINES, ENUMS, TYPEDEFS, STRUCTS
from .field import calculate_padding, Kind, FieldType
from .c_expr import c_eval
from .exceptions import CStructException, ParserError
from .native_types import get_native_type

if TYPE_CHECKING:
    from .abstract import AbstractCStruct, AbstractCEnum

__all__ = ["parse_struct", "parse_struct_def", "parse_enum_def", "Tokens"]

SEPARATORS = [" ", "\t", "\n", ";", "{", "}", ":", ",", "="]
SPACES = [" ", "\t", "\n"]


class Tokens(object):
    def __init__(self, text: str) -> None:
        # remove the comments
        text = re.sub(r"//.*?$|/\*.*?\*/", "", text, flags=re.S | re.MULTILINE)
        # c preprocessor
        lines = []
        for line in text.split("\n"):
            if re.match(r"^\s*#define", line):
                try:
                    _, name, value = line.strip().split(maxsplit=2)
                    DEFINES[name] = c_eval(value)
                except Exception:
                    raise ParserError(f"Parsing line `{line}`")
            else:
                lines.append(line)
        text = "\n".join(lines)
        self.tokens = self.tokenize(text)

    def tokenize(self, text) -> List[str]:
        tokens: List[str] = []
        t: List[str] = []
        for c in text:
            if c in SEPARATORS:
                if t:
                    tokens.append("".join(t))
                    t.clear()
                if c not in SPACES:
                    tokens.append(c)
            else:
                t.append(c)
        if t:
            tokens.append(t.getvalue())
        return tokens

    def pop(self) -> str:
        return self.tokens.pop(0)

    def pop_c_type(self) -> str:
        c_type = self.pop()
        if c_type in ["signed", "unsigned"] and len(self) > 1:
            # short int, long int, or long long
            c_type = c_type + " " + self.pop()
        elif c_type in ["short", "long"] and len(self) > 1 and self.get() in ["int", "long"]:
            # short int, long int, or long long
            c_type = c_type + " " + self.pop()
        return c_type

    def get(self) -> str:
        return self.tokens[0]

    def push(self, value: str) -> None:
        return self.tokens.insert(0, value)

    def __len__(self) -> int:
        return len(self.tokens)

    def __str__(self) -> str:
        return str(self.tokens)


def parse_type(tokens: Tokens, __cls__: Type["AbstractCStruct"], byte_order: Optional[str], offset: int) -> "FieldType":
    if len(tokens) < 2:
        raise ParserError("Parsing error")
    c_type = tokens.pop()
    # signed/unsigned/struct
    if c_type in ["signed", "unsigned", "struct", "union", "enum"] and len(tokens) > 1:
        c_type = c_type + " " + tokens.pop()

    vlen = 1
    flexible_array = False

    if not c_type.endswith("{"):
        next_token = tokens.pop()
        # short int, long int, or long long
        if next_token in ["int", "long"]:
            c_type = c_type + " " + next_token
            next_token = tokens.pop()
        # void *
        if next_token.startswith("*"):
            next_token = next_token[1:]
            c_type = "void *"
        # parse length
        if "[" in next_token:
            t = next_token.split("[")
            if len(t) != 2:
                raise ParserError(f"Error parsing: `{next_token}`")
            next_token = t[0].strip()
            vlen_part = t[1]
            vlen_expr = []
            while not vlen_part.endswith("]"):
                vlen_expr.append(vlen_part.split("]")[0].strip())
                vlen_part = tokens.pop()
            t_vlen = vlen_part.split("]")[0].strip()
            vlen_expr.append(vlen_part.split("]")[0].strip())
            t_vlen = " ".join(vlen_expr)
            if not t_vlen:
                flexible_array = True
                vlen = 0
            else:
                try:
                    vlen = c_eval(t_vlen)
                except (ValueError, TypeError):
                    vlen = int(t_vlen)
        tokens.push(next_token)
        # resolve typedefs
        while c_type in TYPEDEFS:
            c_type = TYPEDEFS[c_type]

    # calculate fmt
    if c_type.startswith("struct ") or c_type.startswith("union "):  # struct/union
        c_type, tail = c_type.split(" ", 1)
        kind = Kind.STRUCT if c_type == "struct" else Kind.UNION
        if tokens.get() == "{":  # Named nested struct
            tokens.push(tail)
            tokens.push(c_type)
            ref: Union[Type[AbstractCEnum], Type[AbstractCStruct]] = __cls__.parse(tokens, __name__=tail, __byte_order__=byte_order)
        elif tail == "{":  # Unnamed nested struct
            tokens.push(tail)
            tokens.push(c_type)
            ref = __cls__.parse(tokens, __byte_order__=byte_order)
        else:
            try:
                ref = STRUCTS[tail]
            except KeyError:
                raise ParserError(f"Unknown `{c_type} {tail}`")
    elif c_type.startswith("enum"):
        from .cenum import CEnum

        c_type, tail = c_type.split(" ", 1)
        kind = Kind.ENUM
        if tokens.get() == "{":  # Named nested struct
            tokens.push(tail)
            tokens.push(c_type)
            ref = CEnum.parse(tokens, __name__=tail)
        elif tail == "{":  # unnamed nested struct
            tokens.push(tail)
            tokens.push(c_type)
            ref = CEnum.parse(tokens)
        else:
            try:
                ref = ENUMS[tail]
            except KeyError:
                raise ParserError(f"Unknown `{c_type} {tail}`")
    else:  # other types
        kind = Kind.NATIVE
        ref = None
    return FieldType(kind, c_type, ref, vlen, flexible_array, byte_order, offset)


def parse_typedef(tokens: Tokens, __cls__: Type["AbstractCStruct"], byte_order: Optional[str]) -> None:
    field_type = parse_type(tokens, __cls__, byte_order, 0)
    vname = tokens.pop()
    if field_type.ref is None:
        TYPEDEFS[vname] = field_type.c_type
    elif field_type.ref.__is_enum__:
        TYPEDEFS[vname] = f"enum {field_type.ref.__name__}"
    elif field_type.ref.__is_union__:
        TYPEDEFS[vname] = f"union {field_type.ref.__name__}"
    else:
        TYPEDEFS[vname] = f"struct {field_type.ref.__name__}"
    t = tokens.pop()
    if t != ";":
        raise ParserError(f"`;` expected but `{t}` found")


def parse_struct_def(
    __def__: Union[str, Tokens],
    __cls__: Type["AbstractCStruct"],
    __byte_order__: Optional[str] = None,
    process_muliple_definition: bool = False,
    **kargs: Any,  # Type['AbstractCStruct'],
) -> Optional[Dict[str, Any]]:
    # naive C struct parsing
    if isinstance(__def__, Tokens):
        tokens = __def__
    else:
        tokens = Tokens(__def__)
    result = None
    while tokens and (process_muliple_definition or not result):
        kind = tokens.pop()
        if kind == ";":
            pass

        elif kind == "typedef":
            if result:
                result["__cls__"].parse(result, **kargs)
            parse_typedef(tokens, __cls__, __byte_order__)

        elif kind == "enum":
            if result:
                result["__cls__"].parse(result, **kargs)
            name = tokens.pop()
            native_format = None
            if tokens.get() == ":":  # enumeration type declaration
                tokens.pop()  # pop ":"
                type_ = get_native_type(tokens.pop_c_type())
                native_format = type_.native_format
            if tokens.get() == "{":  # named enum
                tokens.pop()  # pop "{"
                result = parse_enum(tokens, __name__=name, native_format=native_format)
            elif name == "{":  # unnamed enum
                result = parse_enum(tokens, native_format=native_format)
            else:
                raise ParserError(f"`{name}` definition expected")

        elif kind in ["struct", "union"]:
            if result:
                result["__cls__"].parse(result, **kargs)
            __is_union__ = kind == "union"
            name = tokens.pop()
            if name == "{":  # unnamed nested struct
                result = parse_struct(tokens, __cls__=__cls__, __is_union__=__is_union__, __byte_order__=__byte_order__)
            elif tokens.get() == "{":  # Named nested struct
                tokens.pop()  # pop "{"
                result = parse_struct(
                    tokens, __cls__=__cls__, __is_union__=__is_union__, __byte_order__=__byte_order__, __name__=name
                )
            else:
                raise ParserError(f"`{name}` definition expected")

        else:
            raise ParserError(f"struct, union, or enum expected - `{kind}` found")
    return result


def parse_enum_def(__def__: Union[str, Tokens], **kargs: Any) -> Optional[Dict[str, Any]]:
    # naive C enum parsing
    if isinstance(__def__, Tokens):
        tokens = __def__
    else:
        tokens = Tokens(__def__)
    if not tokens:
        return None
    kind = tokens.pop()
    if kind not in ["enum"]:
        raise ParserError(f"enum expected - `{kind}` found")

    name = tokens.pop()
    native_format = None
    if tokens.get() == ":":  # enumeration type declaration
        tokens.pop()  # pop ":"
        type_ = get_native_type(tokens.pop_c_type())
        native_format = type_.native_format
    if tokens.get() == "{":  # named enum
        tokens.pop()  # pop "{"
        return parse_enum(tokens, __name__=name, native_format=native_format)
    elif name == "{":  # unnamed enum
        return parse_enum(tokens)
    else:
        raise ParserError(f"`{name}` definition expected")


def parse_enum(
    __enum__: Union[str, Tokens],
    __name__: Optional[str] = None,
    native_format: Optional[str] = None,
    **kargs: Any,
) -> Optional[Dict[str, Any]]:
    """
    Parser for C-like enum syntax.

    Args:
        __enum__:       definition of the enum in C syntax
        __name__:       enum name
        native_format:  struct module format

    Returns:
        dict: the parsed definition
    """
    from .cenum import CEnum

    constants: Dict[str, int] = OrderedDict()

    if isinstance(__enum__, Tokens):
        tokens = __enum__
    else:
        tokens = Tokens(__enum__)

    while len(tokens):
        if tokens.get() == "}":
            tokens.pop()
            break

        name = tokens.pop()
        next_token = tokens.pop()
        if next_token in {",", "}"}:  # enum-constant without explicit value
            if len(constants) == 0:
                value = 0
            else:
                value = next(reversed(constants.values())) + 1
        elif next_token == "=":  # enum-constant with explicit value
            exp_elems = []
            next_token = tokens.pop()
            while next_token not in {",", "}"}:
                exp_elems.append(next_token)
                if len(tokens) > 0:
                    next_token = tokens.pop()
                else:
                    break

            if len(exp_elems) == 0:
                raise ParserError("enum is missing value expression")

            int_expr = " ".join(exp_elems)
            try:
                value = c_eval(int_expr)
            except (ValueError, TypeError):
                value = int(int_expr)
        else:
            raise ParserError(f"`{__enum__}` is not a valid enum expression")

        if name in constants:
            raise ParserError(f"duplicate enum name `{name}`")
        constants[name] = value

        if next_token == "}":
            break

    result = {
        "__constants__": constants,
        "__is_struct__": False,
        "__is_union__": False,
        "__is_enum__": True,
        "__name__": __name__,
        "__native_format__": native_format,
        "__cls__": CEnum,
    }
    return result


def parse_struct(
    __struct__: Union[str, Tokens],
    __cls__: Type["AbstractCStruct"],
    __is_union__: bool = False,
    __byte_order__: Optional[str] = None,
    __name__: Optional[str] = None,
    **kargs: Any,
) -> Dict[str, Any]:
    """
    Parser for C-like struct syntax.

    Args:
        __struct__:     definition of the struct/union in C syntax
        __cls__:        base class (MemCStruct or CStruct)
        __is_union__:   True for union, False for struct
        __byte_order__: byte order, valid values are LITTLE_ENDIAN, BIG_ENDIAN, NATIVE_ORDER
        __name__:       struct/union name

    Returns:
        dict: the parsed definition
    """
    # naive C struct parsing
    from .abstract import AbstractCStruct
    from .mem_cstruct import MemCStruct

    if __cls__ is None or __cls__ == AbstractCStruct:
        __cls__ = MemCStruct
    __is_union__ = bool(__is_union__)
    fields_types: Dict[str, FieldType] = OrderedDict()
    flexible_array: bool = False
    offset: int = 0
    max_alignment: int = 0
    anonymous: int = 0
    if isinstance(__struct__, Tokens):
        tokens = __struct__
    else:
        tokens = Tokens(__struct__)
    while len(tokens):
        if tokens.get() == "}":
            tokens.pop()
            break
        # flexible array member must be the last member of such a struct
        if flexible_array:
            raise CStructException("Flexible array member must be the last member of such a struct")
        field_type = parse_type(tokens, __cls__, __byte_order__, offset)
        vname = tokens.pop()
        if vname in fields_types:
            raise ParserError(f"Duplicate member `{vname}`")
        if vname in dir(__cls__):
            raise ParserError(f"Invalid reserved member name `{vname}`")
        # anonymous nested union
        if vname == ";" and field_type.ref is not None and (__is_union__ or field_type.ref.__is_union__):
            # add the anonymous struct fields to the parent
            for nested_field_name, nested_field_type in field_type.ref.__fields_types__.items():
                if nested_field_name in fields_types:
                    raise ParserError(f"Duplicate member `{nested_field_name}`")
                fields_types[nested_field_name] = nested_field_type
            vname = f"__anonymous{anonymous}"
            anonymous += 1
            tokens.push(";")
        fields_types[vname] = field_type
        # calculate the max field size (for the alignment)
        max_alignment = max(max_alignment, field_type.alignment)
        # align struct if byte order is native
        if not __is_union__:  # C struct
            field_type.align_filed_offset()
            offset = field_type.offset + field_type.vsize
        t = tokens.pop()
        if t != ";":
            raise ParserError(f"`;` expected but `{t}` found")

    if __is_union__:  # C union
        # Calculate the sizeof union as size of its largest element
        size = max([x.vsize for x in fields_types.values()])
    else:  # C struct
        # add padding to struct if byte order is native
        size = offset + calculate_padding(__byte_order__, max_alignment, offset)

    # Prepare the result
    result = {
        "__fields__": list(fields_types.keys()),
        "__fields_types__": fields_types,
        "__size__": size,
        "__is_struct__": not __is_union__,
        "__is_union__": __is_union__,
        "__is_enum__": False,
        "__byte_order__": __byte_order__,
        "__alignment__": max_alignment,
        "__name__": __name__,
        "__cls__": __cls__,
    }
    return result
