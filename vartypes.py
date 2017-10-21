from abc import ABCMeta, abstractmethod
from typing import List

import math

import copy

from common import Value, Token, EvaluationException
from matrix import MatrixTransformer


class Type(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def new(tokens: List) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def pos(this: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def neg(this: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def add(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def sub(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def mul(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def div(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def mod(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def pow(this: Value, other: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def sqrt(this: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def exp(this: Value) -> Value:
        raise Exception('Operation not defined for this type.')

    @staticmethod
    def identity(this: Value) -> Value:
        raise Exception('Operation not defined for this type.')


class Variable(Type):
    @staticmethod
    def new(tokens: List) -> Value:
        return Value(Variable, tokens[0].value)


class Number(Type):
    @staticmethod
    def new(tokens: List[Token]) -> Value:
        return Value(Number, float(tokens[0].value))

    @staticmethod
    def pos(this: Value) -> Value:
        return Value(Number, this.value)

    @staticmethod
    def neg(this: Value) -> Value:
        return Value(Number, -this.value)

    @staticmethod
    def add(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value + other.value)

        else:
            raise Exception('Cannot add {} and {}'.format(this.type, other.type))

    @staticmethod
    def sub(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value - other.value)

        else:
            raise Exception('Cannot sub {} and {}'.format(this.type, other.type))

    @staticmethod
    def mul(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value * other.value)

        elif other.type is Matrix:
            return Matrix.mul(other, this)

        else:
            raise Exception('Cannot mul {} and {}'.format(this.type, other.type))

    @staticmethod
    def div(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value / other.value)

        else:
            raise Exception('Cannot div {} and {}'.format(this.type, other.type))

    @staticmethod
    def mod(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value % other.value)

        else:
            raise Exception('Cannot mod {} and {}'.format(this.type, other.type))

    @staticmethod
    def pow(this: Value, other: Value) -> Value:
        if other.type is Number:
            return Value(Number, this.value ** other.value)

        else:
            raise Exception('Cannot pow {} and {}'.format(this.type, other.type))

    @staticmethod
    def sqrt(this: Value) -> Value:
        return Value(Number, math.sqrt(this.value))

    @staticmethod
    def exp(this: Value) -> Value:
        return Value(Number, math.exp(this.value))

    @staticmethod
    def identity(this: Value) -> Value:
        return Value(Matrix, [[1 if col is row else 0 for col in range(int(this.value))] for row in range(int(this.value))])


class Matrix(Type):
    @staticmethod
    def new(tokens: List[Value]) -> Value:
        return Value(Matrix, list(map(lambda t: t.value, tokens)))

    @staticmethod
    def mul(this: Value, other: Value):
        if other.type == Number:
            # Number * Matrix
            return Value(Matrix, [[cell * other.value for cell in row] for row in other.value])

        elif other.type == Matrix:
            # Matrix * Matrix
            result = [[0 for _ in range(len(this.value))] for _ in range(len(other.value[0]))]

            for i in range(len(this.value)):
                for j in range(len(other.value[0])):
                    for k in range(len(other.value)):
                        result[i][j] += this.value[i][k] * other.value[k][j]

            return Value(Matrix, result)

        raise Exception('Cannot mul {} and {}'.format(this.type, other.type))

    @staticmethod
    def det(matrix: Value) -> Value:
        return Value(Number, Matrix._det(matrix.value))

    @staticmethod
    def _det(matrix: List[List[float]]) -> float:
        if len(matrix) is 2:
            return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])

        cofactors = []

        for col in range(len(matrix)):
            cofactors.append(Matrix._det([matrix[row][0:col] + matrix[row][col + 1:] for row in range(1, len(matrix))]) * matrix[0][col] * (1 if col % 2 is 0 else -1))

        return sum(cofactors)

    @staticmethod
    def trans(matrix: Value) -> Value:
        return Value(Matrix, list(map(list, zip(*matrix.value))))

    @staticmethod
    def cof(matrix: Value) -> Value:
        # TODO: This code is pretty ugly.

        cofactor_matrix = []
        mat = matrix.value

        for row in range(len(mat)):
            cofactor_matrix.append([])

            for col in range(len(mat[row])):
                minor = copy.deepcopy(mat)
                del minor[row]

                for r in minor:
                    del r[col]

                cofactor_matrix[row].append(Matrix._det(minor) * (1 if (row + col) % 2 is 0 else -1))

        return Value(Matrix, cofactor_matrix)

    @staticmethod
    def adj(matrix: Value) -> Value:
        return Matrix.trans(Matrix.cof(matrix))

    @staticmethod
    def inv(matrix: Value) -> Value:
        det = Matrix._det(matrix.value)

        if det == 0:
            raise EvaluationException('Cannot invert matrix with determinant of 0.')

        multiplier = 1 / det
        return Value(Matrix, [[cell * multiplier for cell in row] for row in Matrix.adj(matrix).value])

    @staticmethod
    def _rref(matrix):
        return MatrixTransformer(copy.deepcopy(matrix.value)).rref()

    @staticmethod
    def rref(matrix: Value) -> Value:
        return Value(Matrix, Matrix._rref(matrix)[0])

    @staticmethod
    def trnsform(matrix) -> Value:
        return Value(Matrix, Matrix._rref(matrix)[1])


class MatrixRow(Type):
    @staticmethod
    def new(tokens: List[Value]) -> Value:
        return Value(MatrixRow, list(map(lambda t: t.value, tokens)))
