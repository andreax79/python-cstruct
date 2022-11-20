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

import ast
import operator
from typing import Any, Callable, Dict, Union, Type, TYPE_CHECKING
from .base import DEFINES, STRUCTS
from .exceptions import EvalError

if TYPE_CHECKING:
    from .abstract import AbstractCStruct

__all__ = ["c_eval"]


def c_eval(expr: str) -> Union[int, float]:
    """
    Evaluate a C arithmetic/logic expression and return the result

    Examples:
        >>> c_eval('10 + (5 / 3)')
        11
        >>> c_eval('!0')
        1
        >>> c_eval('sizeof(x)')
        128

    Args:
        expr: C expression

    Returns:
        result: the expression evaluation result

    Raises:
        EvalError: expression evaluation error
    """
    try:
        expr = expr.replace("!", " not ").replace("&&", " and ").replace("||", " or ")
        return eval_node(ast.parse(expr.strip()).body[0])
    except EvalError:
        raise
    except Exception:
        raise EvalError


def eval_node(node: ast.stmt) -> Union[int, float]:
    handler = OPS[type(node)]
    result = handler(node)
    if isinstance(result, bool):  # convert bool to int
        return 1 if result else 0
    elif isinstance(result, str):  # convert char to int
        if len(result) != 1:
            raise EvalError("Multi-character constant")
        else:
            return ord(result)
    return result


def eval_get(node) -> Union[int, float, Type["AbstractCStruct"]]:
    "Get definition/struct by name"
    try:
        return DEFINES[node.id]
    except KeyError:
        return STRUCTS[node.id]


def eval_compare(node) -> bool:
    "Evaluate a compare node"
    right = eval_node(node.left)
    for operation, comp in zip(node.ops, node.comparators):
        left = right
        right = eval_node(comp)
        if not OPS[type(operation)](left, right):
            return False
    return True


def eval_div(node) -> Union[int, float]:
    "Evaluate div node (integer/float)"
    left = eval_node(node.left)
    right = eval_node(node.right)
    if isinstance(left, float) or isinstance(right, float):
        return operator.truediv(left, right)
    else:
        return operator.floordiv(left, right)


def eval_call(node) -> Union[int, float]:
    from . import sizeof

    if node.func.id == "sizeof":
        args = [eval_node(x) for x in node.args]
        return sizeof(*args)
    raise KeyError(node.func.id)


try:
    Constant = ast.Constant
except AttributeError:  # python < 3.8
    Constant = ast.NameConstant

OPS: Dict[Type[ast.AST], Callable[[Any], Any]] = {
    ast.Expr: lambda node: eval_node(node.value),
    ast.Num: lambda node: node.n,
    ast.Name: eval_get,
    ast.Call: eval_call,
    Constant: lambda node: node.value,
    ast.Str: lambda node: node.s,  # python < 3.8
    # and/or
    ast.BoolOp: lambda node: OPS[type(node.op)](node),  # and/or operator
    ast.And: lambda node: all(eval_node(x) for x in node.values),  # && operator
    ast.Or: lambda node: any(eval_node(x) for x in node.values),  # || operator
    # binary
    ast.BinOp: lambda node: OPS[type(node.op)](node),  # binary operators
    ast.Add: lambda node: operator.add(eval_node(node.left), eval_node(node.right)),  # + operator
    ast.Sub: lambda node: operator.sub(eval_node(node.left), eval_node(node.right)),  # - operator
    ast.Mult: lambda node: operator.mul(eval_node(node.left), eval_node(node.right)),  # * operator
    ast.Div: eval_div,
    ast.Mod: lambda node: operator.mod(eval_node(node.left), eval_node(node.right)),  # % operator
    ast.LShift: lambda node: operator.lshift(eval_node(node.left), eval_node(node.right)),  # << operator
    ast.RShift: lambda node: operator.rshift(eval_node(node.left), eval_node(node.right)),  # >> operator
    ast.BitOr: lambda node: operator.or_(eval_node(node.left), eval_node(node.right)),  # | operator
    ast.BitXor: lambda node: operator.xor(eval_node(node.left), eval_node(node.right)),  # ^ operator
    ast.BitAnd: lambda node: operator.and_(eval_node(node.left), eval_node(node.right)),  # & operator
    # unary
    ast.UnaryOp: lambda node: OPS[type(node.op)](node),  # unary operators
    ast.UAdd: lambda node: operator.pos(eval_node(node.operand)),  # unary + operator
    ast.USub: lambda node: operator.neg(eval_node(node.operand)),  # unary - operator
    ast.Not: lambda node: operator.not_(eval_node(node.operand)),  # ! operator
    ast.Invert: lambda node: operator.invert(eval_node(node.operand)),  # ~ operator
    # Compare
    ast.Compare: eval_compare,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
}
