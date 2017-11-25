import copy
from typing import List, Tuple


class DynamicVector:
    """
    This class represents a vector which can be made up of parts with free variables (ex. [1, 2, 0] + [0, 0, 1] * x_1)
    """
    def __init__(self, size):
        self.size = size
        self.vectors = {'const': [0] * size}

    def add(self, row):
        # Adds a new free variable
        self.vectors[row] = [1 if x is row else 0 for x in range(self.size)]

    def add_missing(self, rows):
        # Adds any free variables that aren't already added.
        for row in rows:
            if row not in self.vectors and not self.vectors['const'][row]:
                self.add(row)

    def set(self, row, col, val):
        if col not in self.vectors:
            # We need to add a free variable.
            self.add(col)

        self.vectors[col][row] = val

    def const(self, row, val):
        # Sets the constant value for a given variable
        self.vectors['const'][row] = val

    def __str__(self):
        return str(self.vectors)


MatrixTyping = List[List[float]]


class MatrixTransformer:
    """
    This class is in charge of calculating rref and transformation matrices for a given matrix.
    """

    def __init__(self, matrix, answer=None):
        self.matrix = matrix
        self.transformation = self.identity
        self.answer = answer or [0] * len(self.matrix)

    def rref(self) -> Tuple[MatrixTyping, MatrixTyping, DynamicVector]:
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

            # Only add back up if the element above the pivot is zero
            for i in range(row - 1, -1, -1):
                if self.matrix[i][row] != 0: # The `row` is not a typo, we care about the pivot element, not the current element.
                    self._add_rows(row, i, col)

            row -= 1
            col -= 1

        # Replace negative zeroes with positive zeroes.
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):
                if self.matrix[row][col] == -0.0:
                    self.matrix[row][col] = 0.0

        for cell in range(len(self.answer)):
            if self.answer[cell] == -0.0:
                self.answer[cell] = 0.0

        dvec = DynamicVector(len(self.matrix))

        for row in range(len(self.matrix) - 1, -1, -1):
            num_zeroes = self._count_leading_zeroes(row)

            # An entire row of zeroes. Maybe this won't end up mattering?
            if num_zeroes == len(self.matrix[row]):
                pass

            else:
                dvec.const(num_zeroes, self.answer[row])

                for nxt in range(num_zeroes + 1, len(self.matrix[row])):
                    if self.matrix[row][nxt] != 0:
                        dvec.set(row, nxt, -matrix[row][nxt])

        dvec.add_missing(range(len(self.matrix)))

        return self.matrix, self.transformation, dvec

    @property
    def identity(self) -> MatrixTyping:
        # Returns a new identity matrix of the same size as self.matrix.
        return [[1 if col is row else 0 for col in range(len(self.matrix))] for row in range(len(self.matrix))]

    def _swap_rows(self, a, b):
        self.matrix[a], self.matrix[b] = self.matrix[b], self.matrix[a]
        self.transformation[a], self.transformation[b] = self.transformation[b], self.transformation[a]
        self.answer[a], self.answer[b] = self.answer[b], self.answer[a]

    def _divide_row(self, row, col):
        self.transformation[row] = [cell / self.matrix[row][col] for cell in self.transformation[row]]
        self.answer[row] /= self.matrix[row][col]
        self.matrix[row] = [cell / self.matrix[row][col] for cell in self.matrix[row]]

    def _add_rows(self, row_to_use, row_to_change, col):
        multiplier = -self.matrix[row_to_change][col] / self.matrix[row_to_use][col]
        self.matrix[row_to_change] = [cell + (self.matrix[row_to_use][c] * multiplier) for c, cell in enumerate(self.matrix[row_to_change])]
        self.transformation[row_to_change] = [cell + multiplier * self.transformation[row_to_use][c] for c, cell in enumerate(self.transformation[row_to_change])]
        self.answer[row_to_change] += multiplier * self.answer[row_to_use]

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
    # matrix = [[1, 2, 3, 4], [4, 2, 3, 7], [1, 2, 3, 8], [9, 2, 3, 3]]
    # matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    # matrix = [[1, 0, 0], [0, 1, 2], [0, 0, 0]]
    matrix = [[1, 0, -58/17], [0, 1, 29/19], [0, 0, 0]]
    # matrix = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    # matrix = [[1, 2, 0], [0, 0, 1], [0, 0, 0]]
    ans = [1, 2, 3]
    transformer = MatrixTransformer(copy.deepcopy(matrix), copy.deepcopy(ans))
    rref, transformation, answer = transformer.rref()
    print(rref, '|', ans, '->', answer, '\n')
    print(transformation)
    print(multiply_matrices(transformation, matrix))
