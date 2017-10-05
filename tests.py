"""
Unit tests for the AST calculator.
"""

import random
import unittest

import sympy

from calculator import Calculator


def evaluate(eqtn: str, verbose=True):
    if verbose:
        print(eqtn)

    calc = Calculator()
    res = calc.evaluate(eqtn, verbose)

    if verbose:
        print(res, '\n' + '-' * 50)

    return res.value


class InvalidEquationTests(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(Exception):
            evaluate('$')

        with self.assertRaises(Exception):
            evaluate('1 +')

        with self.assertRaises(Exception):
            evaluate('1 * / 2')


class AdditionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 2'), 3.0)
        self.assertEqual(evaluate('2 + 3'), 5.0)


class SubtractionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 - 2'), -1.0)
        self.assertEqual(evaluate('3 - 2'), 1.0)
        self.assertEqual(evaluate('-2'), -2.0)
        self.assertEqual(evaluate('-2 + 1'), -1.0)
        self.assertEqual(evaluate('1 + -2'), -1.0)


class MultiplicationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 * 1'), 1.0)
        self.assertEqual(evaluate('2 * 3'), 6.0)
        # self.assertEqual(evaluate('-2 * -2'), 4.0)
        self.assertEqual(evaluate('(2 * 3) (2 * 3)'), 36.0)


class DivisionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 / 1'), 1.0)
        self.assertEqual(evaluate('24 / 4 / 6'), 1.0)
        self.assertEqual(round(evaluate('2 / 3'), 3), 0.667)
        self.assertEqual(evaluate('112 / 2 / 4 / 7'), 2.0)
        self.assertEqual(evaluate('4 % 3'), 1.0)


class PowerTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('2 ^ 3'), 8.0)
        self.assertEqual(evaluate('2 ^ 2 ^ 2 ^ 2'), 65536.0)


class ParenthesisTests(unittest.TestCase):
    def runTest(self):
        # self.assertEqual(evaluate('(1 + 2) * 3'), 9.0)
        # self.assertEqual(evaluate('(1 + 2) ^ (2 * 3 - 2)'), 81.0)
        self.assertEqual(evaluate('2 (1 + 1)'), 4.0)


class IdentifierTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('r = 10; r'), 10.0)
        self.assertEqual(round(evaluate('r = 5.2 * (3 + 2 / (1 + 1/6)); pi = 3.14159; area = pi * r^2; area'), 5), 1887.93915)
        self.assertEqual(round(evaluate('area = pi * r^2; r = 5.2 * (3 + 2 / (1 + 1/6)); pi = 3.14159; area'), 5), 1887.93915)


class OperationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('sqrt(4)'), 2.0)
        self.assertEqual(evaluate('sqrt(8 + 1)'), 3.0)
        self.assertEqual(evaluate('sqrt((4 * 5 - 1) % 10)'), 3.0)
        self.assertEqual(round(evaluate('exp(3)'), 5), 20.08554)


class CombinationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 2 * 3 + 4 * 5'), 27)
        self.assertEqual(evaluate('10 ^ 2 - 2 ^ 3 + 3 * 2 ^ 4'), 140.0)
        self.assertEqual(evaluate('1 + 2 - 3 ^ 4 * 5'), -402.0)
        self.assertEqual(evaluate('2 ^ 2 * 3 ^ 2'), 36.0)
        self.assertEqual(evaluate('a = 2; b = 3; 3*(2 + a + 5*b*2 + 3)'), 111.0)


class MatrixTests(unittest.TestCase):
    def runTest(self):
        # self.assertEqual(evaluate('[1,2]'), [[1.0, 2.0]])
        # self.assertEqual(evaluate('det([1,2,3|4,5,6|7,8,8])'), 3.0)
        #
        # self.assertEqual(evaluate('[1,2|4,5]'), [[1.0, 2.0], [4.0, 5.0]])
        # self.assertEqual(evaluate('trans([1,2|4,5])'), [[1.0, 4.0], [2.0, 5.0]])
        #
        # self.assertEqual(evaluate('inv([1,4,7|3,0,5|-1,9,11])'), [[45/8, -19/8, -5/2], [19/4, -9/4, -2], [-27/8, 13/8, 3/2]])
        #
        # self.assertEqual(evaluate('[1,0,0|0,1,0|0,0,1]'), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        #
        # self.assertEqual(evaluate('[1,0,0,0|0,1,0,0|0,0,1,0|0,0,0,1]'), [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
        # self.assertEqual(evaluate('det([1,3,5,7|2,4,6,8|9,7,5,4|8,6,5,9])'), 2.0)
        #
        # self.assertEqual(evaluate('cof([1,2,3|0,4,5|1,0,6])'), [[24, 5, -4], [-12, 3, 2], [-2, -5, 4]])
        #
        # # Since we have floating-point issues, we have to test each value individually.
        # calc = evaluate('inv([1,2,3|0,4,5|1,0,6])')
        # print(calc)
        # ans = [[12/11, -6/11, -1/11], [5/22, 3/22, -5/22], [-2/11, 1/11, 2/11]]
        #
        # for row in range(len(calc)):
        #     for col in range(len(calc)):
        #         self.assertAlmostEqual(calc[row][col], ans[row][col])

        # self.assertEqual(evaluate('rref([1,2,3|4,5,6|7,8,8])'), [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        # self.assertEqual(evaluate('rref([1,2,4|4,7,6|7,1,8])'), [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assertEqual(evaluate('rref([1,2,3|4,5,6|4,5,6])'), [[1, 0, -1], [0, 1, 2], [0, 0, 0]])
        # self.assertEqual(evaluate('rref([1,2,3|4,5,6|7,8,9])'), [[1, 0, -1], [0, 1, 2], [0, 0, 0]])

        for r_dim in range(3, 10):
            print(r_dim)

            for _ in range(10):
                mat = [[random.randint(0, 100) for _ in range(r_dim)] for _ in range(r_dim)]
                mat_str = '[' + '|'.join([','.join(map(str, line)) for line in mat]) + ']'

                # print('*****<')
                # print(sympy.Matrix(mat))
                # print(sympy.Matrix(evaluate('rref({})'.format(mat_str), False)))
                # print(sympy.Matrix(mat).rref()[0])
                # print('>*****')

                self.assertTrue(sympy.Matrix(evaluate('rref({})'.format(mat_str), False)).equals(sympy.Matrix(mat).rref()[0]))


class RandomTests(unittest.TestCase):
    def runTest(self):
        for _ in range(100):
            eqtn = ''

            for i in range(10):
                eqtn += '{} {} '.format(random.randint(1, 100), random.choice(('+', '-', '*', '/', '%')))

            eqtn = eqtn.strip()[:-2]

            self.assertEqual(evaluate(eqtn), eval(eqtn))

if __name__ == '__main__':
    unittest.main()
