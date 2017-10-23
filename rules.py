"""
This file contains methods to handle Valueing RuleMatches
"""
from typing import List

from common import Token
from vartypes import VariableValue, NumberValue, MatrixRowValue, MatrixValue, Value


def var(_, tokens: List[Token]) -> VariableValue:
    return VariableValue(tokens)


def num(_, tokens: List[Token]) -> NumberValue:
    return NumberValue(tokens)


def mrw(values: List[Value], _) -> MatrixRowValue:
    return MatrixRowValue(values)


def mbd(values: List[Value], _) -> MatrixValue:
    return MatrixValue(values)


def add(operands: List[Value], operator: Token) -> Value:
    return {'+': operands[0].add, '-': operands[0].sub}[operator.value](*operands[1:])


def mul(operands: List[Value], operator: Token) -> Value:
    return {'*': operands[0].mul, '/': operands[0].div, '%': operands[0].mod}[operator.value](*operands[1:])


def pow(operands: List[Value], _) -> Value:
    return operands[0].pow(*operands[1:])


def opr(operands: List[Value], operator: Token) -> Value:
    return getattr(operands[0], operator.value)(*operands[1:])


def neg(operands: List[Value], operator: Token) -> Value:
    return {'+': operands[0].pos, '-': operands[0].neg}[operator.value](*operands[1:])


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
