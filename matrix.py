from functools import reduce
from typing import List, Tuple

import copy

MatrixTyping = List[List[float]]


class MatrixTransformer:
    """
    This class is in charge of calculating rref and transformation matrices for a given matrix.
    """

    def __init__(self, matrix):
        self.matrix = matrix
        self.transformation = self.identity

    def rref(self) -> Tuple[MatrixTyping, MatrixTyping]:
        row = 0
        col = 0

        self._arrange_by_leading_zeroes()

        while row < len(self.matrix) and col < len(self.matrix[row]):
            # If there is a leading 0, move column over but remain on the same row.
            if self.matrix[row][col] == 0:
                col += 1
                continue

            # Divide each cell in the row by the first cell to ensure that the row starts with a 1.
            self._divide_row(row, col)

            # Multiply all lower rows as needed.
            for i in range(row + 1, len(self.matrix)):
                self._add_rows(row, i, col)

            row += 1
            col += 1

            if self._arrange_by_leading_zeroes():
                row = 0
                col = 0

        row = len(self.matrix) - 1
        col = len(self.matrix[row]) - 1

        while row > 0:
            # The whole row is zeroes, ignore the row.
            if self._count_leading_zeroes(row) == len(self.matrix[row]):
                row -= 1
                continue

            # If the current value is a zero, try the next column over.
            elif self.matrix[row][col] == 0:
                # row -= 1
                col -= 1
                continue

            for i in range(row - 1, -1, -1):
                self._add_rows(row, i, col)

            row -= 1
            col -= 1

        return self.matrix, self.transformation

    @property
    def identity(self) -> MatrixTyping:
        # Returns a new identity matrix of the same size as self.matrix.
        return [[1 if col is row else 0 for col in range(len(self.matrix))] for row in range(len(self.matrix))]

    def _swap_rows(self, a, b):
        self.matrix[a], self.matrix[b] = self.matrix[b], self.matrix[a]
        self.transformation[a], self.transformation[b] = self.transformation[b], self.transformation[a]

    def _divide_row(self, row, col):
        self.transformation[row] = [cell / self.matrix[row][col] for cell in self.transformation[row]]
        self.matrix[row] = [cell / self.matrix[row][col] for cell in self.matrix[row]]

    def _add_rows(self, row_to_use, row_to_change, col):
        multiplier = -self.matrix[row_to_change][col] / self.matrix[row_to_use][col]
        self.matrix[row_to_change] = [cell + (self.matrix[row_to_use][c] * multiplier) for c, cell in enumerate(self.matrix[row_to_change])]
        self.transformation[row_to_change] = [cell + multiplier * self.transformation[row_to_use][c] for c, cell in enumerate(self.transformation[row_to_change])]

    def _arrange_by_leading_zeroes(self):
        swapped = False
        r = 0

        while r < len(self.matrix) - 1:
            if self._count_leading_zeroes(r) > self._count_leading_zeroes(r + 1):
                swapped = True
                self._swap_rows(r, r + 1)
                r = 0

            else:
                r += 1

        return swapped

    def _count_leading_zeroes(self, r):
        row = self.matrix[r]

        for i in range(len(row)):
            if row[i] != 0:
                return i

        return len(row)


def multiply_matrices(a: MatrixTyping, b: MatrixTyping) -> MatrixTyping:
    result = [[0 for _ in range(len(a))] for _ in range(len(a))]

    for i in range(len(result)):
        for j in range(len(result)):
            for k in range(len(result)):
                result[i][j] += a[i][k] * b[k][j]

    return result


if __name__ == '__main__':
    matrix = [[1, 2, 3, 4], [4, 2, 3, 7], [1, 2, 3, 8], [9, 2, 3, 3]]
    transformer = MatrixTransformer(copy.deepcopy(matrix))
    rref, transformation = transformer.rref()
    print(rref)
    print(transformation)
    print(multiply_matrices(transformation, matrix))
