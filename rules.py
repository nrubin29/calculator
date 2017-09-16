"""
This file contains methods to handle calculation of all the rules.
"""
import math
import operator
from typing import List, Union

from common import Token, Value, Type, RuleMatch


def add(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Number, {'+': operator.add, '-': operator.sub}[tokens[1].value](tokens[0].value.value, tokens[2].value.value))


def mul(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Number, {'*': operator.mul, '/': operator.truediv, '%': operator.mod}[tokens[1].value](tokens[0].value.value, tokens[2].value.value))


def pow(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Number, tokens[0].value.value ** tokens[2].value.value)


def opr(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Number, {'sqrt': math.sqrt, 'exp': math.exp, 'det': det}[tokens[0].value](tokens[1].value.value))


def neg(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Number, tokens[1].value.value if tokens[0].value == '+' else -tokens[1].value.value)


def num(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    if isinstance(tokens[0], RuleMatch):
        return tokens[0].value

    return Value(Type.Number, float(tokens[0].value))


def mrw(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.MatrixRow, list(map(lambda t: t.value.value, tokens)))


def mbd(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return Value(Type.Matrix, list(map(lambda t: t.value.value, tokens)))


def mat(tokens: List[Union[Token, Value, RuleMatch]]) -> Value:
    return tokens[0].value


def det(matrix: List[List[float]]) -> float:
    if len(matrix) is 2:
        return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])

    cofactors = []

    for col in range(len(matrix)):
        cofactors.append(det([matrix[row][0:col] + matrix[row][col + 1:] for row in range(1, len(matrix))]) * matrix[0][col] * (1 if col % 2 is 0 else -1))

    return sum(cofactors)


calc_map = {
    'add': add,
    'mul': mul,
    'pow': pow,
    'opr': opr,
    'neg': neg,
    'num': num,
    'mrw': mrw,
    'mbd': mbd,
    'mat': mat
}