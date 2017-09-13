"""
This file contains methods to handle calculation of all the rules.
"""
import math
from typing import List

from common import Token


def add(tokens: List[Token]) -> Token:
    return Token('NUM', float(tokens[0].value) + float(tokens[2].value) if tokens[1].value == '+' else float(tokens[0].value) - float(tokens[2].value))


def mul(tokens: List[Token]) -> Token:
    return Token('NUM', float(tokens[0].value) * float(tokens[2].value) if tokens[1].value == '*' else float(tokens[0].value) / float(tokens[2].value) if tokens[1].value == '/' else float(tokens[0].value) % float(tokens[2].value))


def pow(tokens: List[Token]) -> Token:
    return Token('NUM', float(tokens[0].value) ** float(tokens[2].value))


def opr(tokens: List[Token]) -> Token:
    return Token('NUM', {'sqrt': math.sqrt, 'exp': math.exp, 'det': det}[tokens[0].value](tokens[1].value))


def neg(tokens: List[Token]) -> Token:
    return Token('NUM', float(tokens[1].value) if tokens[0].value == '+' else -float(tokens[1].value))


def num(tokens: List[Token]) -> Token:
    return Token('NUM', float(tokens[0].value))


def mrw(tokens: List[Token]) -> Token:
    return Token('MRW', list(map(lambda t: float(t.value), tokens)))


def mbd(tokens: List[Token]) -> Token:
    return Token('MAT', list(map(lambda t: t.value, tokens)))


def mat(tokens: List[Token]) -> Token:
    return tokens[0]


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
