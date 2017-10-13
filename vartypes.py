from abc import ABCMeta, abstractmethod
from typing import List

import math

import copy

from common import Value, Token, EvaluationException


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

        else:
            # TODO: Support for scalar * matrix.
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
        # Returns the transformation matrix which, when multiplied by the original matrix, will give its rref form.
        mat = copy.deepcopy(matrix.value)
        ident = Number.identity(Value(Number, len(mat))).value
        row = 0
        col = 0

        def arrange_by_leading_zeroes():
            r = 0

            def count_leading_zeroes(row):
                for i in range(len(row)):
                    if row[i] != 0:
                        return i

                return len(row)

            while r < len(mat) - 1:
                if count_leading_zeroes(mat[r]) > count_leading_zeroes(mat[r + 1]):
                    mat[r], mat[r + 1] = mat[r + 1], mat[r]
                    ident[r], ident[r + 1] = ident[r + 1], ident[r]
                    r = 0

                else:
                    r += 1

        arrange_by_leading_zeroes()

        while row < len(mat) and col < len(mat[row]):
            # If there is a leading 0, move column over but remain on the same row.
            if mat[row][col] == 0:
                col += 1
                continue

            # Divide each cell in the row by the first cell to ensure that the row starts with a 1.
            mat[row] = [cell / mat[row][col] for cell in mat[row]]
            ident[row] = [cell / mat[row][col] for cell in ident[row]]

            # Multiply all lower rows as needed.
            for i in range(row + 1, len(mat)):
                multiplier = -mat[i][col] / mat[row][col]
                mat[i] = [cell + (mat[row][c] * multiplier) for c, cell in enumerate(mat[i])]
                ident[i] = [cell + (mat[row][c] * multiplier) for c, cell in enumerate(ident[i])]

            row += 1
            col += 1

            arrange_by_leading_zeroes()

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
                ident[i] = [cell + (mat[row][c] * multiplier) for c, cell in enumerate(ident[i])]

                # print('it is now', mat[i])

            row -= 1
            col -= 1

            arrange_by_leading_zeroes()

        return mat, ident

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