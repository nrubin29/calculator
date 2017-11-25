import copy
import math
from abc import ABCMeta
from typing import List

from common import EvaluationException
from matrix import MatrixTransformer, DynamicVector


class Value(metaclass=ABCMeta):
    __slots__ = ('type', 'value')

    def __init__(self):
        self.type = self.__class__.__name__

    def __str__(self):
        return str(self.value)

    def pos(self):
        raise EvaluationException('Operation not defined for ' + self.type)

    def neg(self):
        raise EvaluationException('Operation not defined for ' + self.type)

    def add(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)

    def sub(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)

    def mul(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)

    def div(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)

    def mod(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)
    
    def pow(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)

    def sqrt(self):
        raise EvaluationException('Operation not defined for ' + self.type)

    def exp(self):
        raise EvaluationException('Operation not defined for ' + self.type)

    def identity(self):
        raise EvaluationException('Operation not defined for ' + self.type)

    def solve(self, other):
        raise EvaluationException('Operation not defined for ' + self.type)


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

    def mul(self, other):
        if isinstance(other, NumberValue):
            # Number * Matrix
            return MatrixValue([[cell * other.value for cell in row] for row in self.value])

        elif isinstance(other, MatrixValue):
            # Matrix * Matrix
            result = [[0 for _ in range(len(self.value))] for _ in range(len(other.value[0]))]

            for i in range(len(self.value)):
                for j in range(len(other.value[0])):
                    for k in range(len(other.value)):
                        result[i][j] += self.value[i][k] * other.value[k][j]

            return MatrixValue(result)

        else:
            raise EvaluationException('Cannot mul {} and {}'.format(self.type, other.type))
    
    def det(self):
        return NumberValue(self._det(self.value))

    @staticmethod
    def _det(matrix: List[List[float]]) -> float:
        if len(matrix) is 2:
            return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])

        cofactors = []

        for col in range(len(matrix)):
            cofactors.append(MatrixValue._det([matrix[row][0:col] + matrix[row][col + 1:] for row in range(1, len(matrix))]) * matrix[0][col] * (1 if col % 2 is 0 else -1))

        return sum(cofactors)

    def trans(self):
        return MatrixValue(list(map(list, zip(*self.value))))

    def cof(self):
        # TODO: self code is pretty ugly.

        cofactor_matrix = []
        mat = self.value

        for row in range(len(mat)):
            cofactor_matrix.append([])

            for col in range(len(mat[row])):
                minor = copy.deepcopy(mat)
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


class MatrixRowValue(Value):
    def __init__(self, data):
        super().__init__()

        if isinstance(data[0], Value):
            self.value = list(map(lambda t: t.value, data))

        else:
            self.value = data


class OperatorBodyValue(Value):
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
