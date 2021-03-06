import copy
import functools
import math
from abc import ABCMeta
from typing import List

from common import EvaluationException, operations
from matrix import MatrixTransformer, DynamicVector


def raise_exception(tpe, op):
    raise EvaluationException('{} does not have operation {}'.format(tpe, op))


class Value(metaclass=ABCMeta):
    __slots__ = ('type', 'value')

    def __init__(self):
        self.type = self.__class__.__name__

        for op in operations:
            if not hasattr(self, op):
                setattr(self, op, functools.partial(raise_exception, tpe=self.type, op=op))

    def __str__(self):
        return str(self.value)


class VariableValue(Value):
    def __init__(self, data):
        super().__init__()
        
        if isinstance(data, list):
            self.value = data[0].value
            
        else:
            self.value = data


class NumberValue(Value):
    def __init__(self, data):
        super().__init__()
        
        if isinstance(data, list):
            self.value = float(data[0].value)
        
        else:
            self.value = data
    
    def pos(self):
        return NumberValue(self.value)

    def neg(self):
        return NumberValue(-self.value)

    def add(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value + other.value)

        else:
            raise EvaluationException('Cannot add {} and {}'.format(self.type, other.type))

    def sub(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value - other.value)

        else:
            raise EvaluationException('Cannot sub {} and {}'.format(self.type, other.type))

    def mul(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value * other.value)

        elif isinstance(other, MatrixValue):
            return other.mul(self)

        else:
            raise EvaluationException('Cannot mul {} and {}'.format(self.type, other.type))

    def div(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value / other.value)

        else:
            raise EvaluationException('Cannot div {} and {}'.format(self.type, other.type))

    def mod(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value % other.value)

        else:
            raise EvaluationException('Cannot mod {} and {}'.format(self.type, other.type))

    def pow(self, other):
        if isinstance(other, NumberValue):
            return NumberValue(self.value ** other.value)

        else:
            raise EvaluationException('Cannot pow {} and {}'.format(self.type, other.type))

    def sqrt(self):
        return NumberValue(math.sqrt(self.value))

    def exp(self):
        return NumberValue(math.exp(self.value))

    def identity(self):
        return MatrixValue([[1 if col is row else 0 for col in range(int(self.value))] for row in range(int(self.value))])

    def zeroes(self, other):
        return MatrixValue([[0 for _ in range(int(other.value))] for _ in range(int(self.value))])


class MatrixValue(Value):
    def __init__(self, data):
        super().__init__()
        
        if isinstance(data[0], Value):
            self.value = list(map(lambda t: t.value, data))
        
        else:
            self.value = data

        self._rref_cache = None

    def __str__(self):
        return '[\n' + '\n'.join(['[' + ', '.join(map(lambda cell: str(round(cell, 5)), row)) + ']' for row in self.value]) + '\n]'

    def sub(self, other):
        if isinstance(other, MatrixValue):
            if len(self.value) != len(other.value) or len(self.value[0]) != len(other.value[0]):
                raise EvaluationException('Attempted to subtract two matrices of different dimensions')

            return MatrixValue([[self.value[row][col] - other.value[row][col] for col in range(len(self.value[row]))] for row in range(len(self.value))])

        raise EvaluationException('Cannot sub {} and {}'.format(self.type, other.type))

    def mul(self, other):
        if isinstance(other, NumberValue):
            # Matrix * Number
            return MatrixValue([[cell * other.value for cell in row] for row in self.value])

        elif isinstance(other, MatrixValue):
            # Matrix * Matrix
            if len(self.value[0]) != len(other.value):
                raise EvaluationException('Cannot multiply matrices of dimensions {} and {}'.format((len(self.value), len(self.value[0])), (len(other.value), len(other.value[0]))))

            result = [[0 for _ in range(len(other.value[0]))] for _ in range(len(self.value))]

            for i in range(len(self.value)):
                for j in range(len(other.value[0])):
                    for k in range(len(other.value)):
                        result[i][j] += self.value[i][k] * other.value[k][j]

            return MatrixValue(result)

        else:
            raise EvaluationException('Cannot mul {} and {}'.format(self.type, other.type))

    def div(self, other):
        if isinstance(other, NumberValue):
            # Matrix / Number
            return MatrixValue([[cell / other.value for cell in row] for row in self.value])

        else:
            raise EvaluationException('Cannot div {} and {}'.format(self.type, other.type))

    def det(self):
        return NumberValue(self._det(self.value))

    @staticmethod
    def _det(matrix: List[List[float]]) -> float:
        if len(matrix) is 1:
            return matrix[0][0]

        cofactors = []

        for col in range(len(matrix)):
            cofactors.append(MatrixValue._det([matrix[row][0:col] + matrix[row][col + 1:] for row in range(1, len(matrix))]) * matrix[0][col] * (1 if col % 2 is 0 else -1))

        return sum(cofactors)

    def trans(self):
        return MatrixValue(list(map(list, zip(*self.value))))

    def cof(self):
        cofactor_matrix = []

        for row in range(len(self.value)):
            cofactor_matrix.append([])

            for col in range(len(self.value[row])):
                minor = copy.deepcopy(self.value)
                del minor[row]

                for r in minor:
                    del r[col]

                cofactor_matrix[row].append(self._det(minor) * (1 if (row + col) % 2 is 0 else -1))

        return MatrixValue(cofactor_matrix)

    def adj(self):
        return self.cof().trans()

    def inv(self):
        det = self._det(self.value)

        if det == 0:
            raise EvaluationException('Cannot invert matrix with determinant of 0.')

        multiplier = 1 / det
        return MatrixValue([[cell * multiplier for cell in row] for row in self.adj().value])

    def _rref(self):
        if not self._rref_cache:
            self._rref_cache = MatrixTransformer(copy.deepcopy(self.value)).rref()

        return self._rref_cache
    
    def rref(self):
        return MatrixValue(self._rref()[0])

    def trnsform(self):
        return MatrixValue(self._rref()[1])

    def solve(self, other):
        return DynamicVectorValue(MatrixTransformer(copy.deepcopy(self.value)).rref(other.value[0])[2])

    def ls(self, other):
        return (self.trans().mul(self)).inv().mul(self.trans()).mul(other)

    def norm(self):
        return NumberValue(math.sqrt(sum([sum([col * col for col in row]) for row in self.value])))

    def squeeze(self):
        return MatrixValue([[cell for row in self.value for cell in row]])

    def _col(self, col):
        """ Isolates an individual column from the matrix """
        return MatrixValue([[row[col]] for row in self.value])

    def qr(self):
        m = NumberValue(len(self.value))
        n = NumberValue(len(self.value[0]))

        Q = m.zeroes(m).value
        R = n.zeroes(n).value

        for j in range(n.value):
            v = self._col(j)

            for i in range(j):
                R[i][j] = MatrixValue(Q)._col(i).trans().mul(self._col(j)).value[0][0]
                v = v.squeeze().sub(MatrixValue(Q)._col(i).trans().mul(NumberValue(R[i][j])))

            R[j][j] = v.norm().value

            val = v.div(NumberValue(R[j][j])).squeeze().value[0]
            for row in range(len(Q)):
                Q[row][j] = val[row]

        return TupleValue([MatrixValue(Q), MatrixValue(R)])


class MatrixRowValue(Value):
    def __init__(self, data):
        super().__init__()

        if isinstance(data[0], Value):
            self.value = list(map(lambda t: t.value, data))

        else:
            self.value = data


class TupleValue(Value):
    def __init__(self, args: List):
        super().__init__()

        self.value = args


class DynamicVectorValue(Value):
    def __init__(self, dvec: DynamicVector):
        super().__init__()

        self.value = dvec

    def eval(self, *args):
        dvec = copy.deepcopy(self.value)
        ans = dvec.vectors.pop('const')

        i = 0
        for _, free_var in dvec.vectors.items():
            row = [x * int(args[i].value) for x in free_var]
            ans = [ans[i] + row[i] for i in range(len(ans))]
            i += 1

        return MatrixValue([ans])
