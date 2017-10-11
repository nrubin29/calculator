"""
This file contains methods to handle Valueing RuleMatches
"""
from typing import List

from common import Token, Value
from vartypes import Number, MatrixRow, Matrix, Variable


def var(_, tokens: List[Token]) -> Value:
    return Variable.new(tokens)


def num(_, tokens: List[Token]) -> Value:
    return Number.new(tokens)


def mrw(values: List[Value], _) -> Value:
    return MatrixRow.new(values)


def mbd(values: List[Value], _) -> Value:
    return Matrix.new(values)


def add(operands: List[Value], operator: Token) -> Value:
    return {'+': operands[0].type.add, '-': operands[0].type.sub}[operator.value](*operands)


def mul(operands: List[Value], operator: Token) -> Value:
    return {'*': operands[0].type.mul, '/': operands[0].type.div, '%': operands[0].type.mod}[operator.value](*operands)


def pow(operands: List[Value], _) -> Value:
    return operands[0].type.pow(*operands)


def opr(operands: List[Value], operator: Token) -> Value:
    return getattr(operands[0].type, operator.value)(*operands)


def neg(operands: List[Value], operator: Token) -> Value:
    return {'+': operands[0].type.pos, '-': operands[0].type.neg}[operator.value](*operands)


# The mapping for num, mrw, mbd.
rule_value_map = {
    'var': var,
    'num': num,
    'mrw': mrw,
    'mbd': mbd,
}

# The mapping for all other rules.
rule_value_operation_map = {
    'add': add,
    'mul': mul,
    'pow': pow,
    'opr': opr,
    'neg': neg,
}
