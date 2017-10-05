"""
This file contains methods to handle calculation of all the rules.
"""
import copy
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
    return Value(Type.Number, {'sqrt': math.sqrt, 'exp': math.exp, 'det': det, 'trans': trans, 'cof': cof, 'adj': adj, 'inv': inv, 'rref': rref}[tokens[0].value](tokens[1].value.value))


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


def trans(matrix: List[List[float]]) -> List[List[float]]:
    return list(map(list, zip(*matrix)))


def cof(matrix: List[List[float]]) -> List[List[float]]:
    # TODO: This code is pretty ugly.

    cofactor_matrix = []

    for row in range(len(matrix)):
        cofactor_matrix.append([])

        for col in range(len(matrix[row])):
            minor = copy.deepcopy(matrix)
            del minor[row]

            for r in minor:
                del r[col]

            cofactor_matrix[row].append(det(minor) * (1 if (row + col) % 2 is 0 else -1))

    return cofactor_matrix


def adj(matrix: List[List[float]]) -> List[List[float]]:
    return trans(cof(matrix))


def inv(matrix: List[List[float]]):
    multiplier = 1 / det(matrix)
    return [[cell * multiplier for cell in row] for row in adj(matrix)]


def rref(matrix: List[List[float]]):
    mat = copy.deepcopy(matrix)
    row = 0
    col = 0

    def count_leading_zeroes(row):
        for i in range(len(row)):
            if row[i] != 0:
                return i

        return len(row)

    # Sort the matrix by the number of 0s in each row with the most 0s going to the bottom.
    mat = sorted(mat, key=count_leading_zeroes)

    # print(mat)

    while row < len(mat) and col < len(mat[row]):
        # print(row, mat)

        # If there is a leading 0, move column over but remain on the same row.
        if mat[row][col] == 0:
            col += 1
            continue

        # Divide each cell in the row by the first cell to ensure that the row starts with a 1.
        mat[row] = [cell / mat[row][col] for cell in mat[row]]

        # Multiply all lower rows as needed.
        for i in range(row + 1, len(mat)):
            multiplier = -mat[i][col] / mat[row][col]
            mat[i] = [cell + (mat[row][c] * multiplier) for c, cell in enumerate(mat[i])]

        row += 1
        col += 1

    row = len(mat) - 1
    col = len(mat[row]) - 1

    # print('going back up', row, col)

    while row > 0:
        # If we have a 0 at this point, we don't need to go back up for this row.
        if mat[row][col] == 0:
            row -= 1
            col -= 1
            continue

        for i in range(row - 1, -1, -1):
            multiplier = -mat[i][col] / mat[row][col]

            # print('multiplier', multiplier)

            mat[i] = [cell + (mat[row][c] * multiplier) for c, cell in enumerate(mat[i])]

            # print('it is now', mat[i])

        row -= 1
        col -= 1

    return mat


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
