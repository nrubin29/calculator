"""
Unit tests for the AST calculator.
"""
import decimal
import random
import unittest

import sympy

from calculator import Calculator
from common import EvaluationException


def evaluate(eqtn: str, tpe='infix', verbose=True):
    if verbose:
        print(eqtn)

    calc = Calculator()
    res = calc.evaluate(eqtn, tpe, verbose)

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
        self.assertEqual(evaluate('-2 * -2'), 4.0)
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
        self.assertEqual(evaluate('(1 + 2) * 3'), 9.0)
        self.assertEqual(evaluate('(1 + 2) ^ (2 * 3 - 2)'), 81.0)
        self.assertEqual(evaluate('2 (1 + 1)'), 4.0)


class IdentifierTests(unittest.TestCase):
    def runTest(self):
        pass
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
        rnd = lambda e: round(e, 5)
        more_zeroes = lambda n: n if n <= 75 else 0

        for r_dim in range(3, 4):
            print(r_dim)

            self.assertTrue(sympy.Matrix(evaluate('identity({})'.format(r_dim), False)).equals(sympy.Identity(r_dim)))

            for _ in range(5):
                print(_)

                mat = [[more_zeroes(random.randint(0, 100)) for _ in range(r_dim)] for _ in range(r_dim)]
                mat_str = '[' + '|'.join([','.join(map(str, line)) for line in mat]) + ']'

                sym_mat = sympy.Matrix(mat)
                rref = sym_mat.rref()[0]

                if not rref.equals(sympy.Identity(r_dim)):
                    print('rref not identity!', rref)

                try:
                    self.assertTrue(decimal.Context(prec=10).create_decimal(float(evaluate('det({})'.format(mat_str), False))) == decimal.Context(prec=10).create_decimal(float(sym_mat.det())))
                    self.assertTrue(
                        sympy.Matrix(evaluate('trans({})'.format(mat_str), False)).equals(sym_mat.transpose()))
                    self.assertTrue(sympy.Matrix(evaluate('inv({})'.format(mat_str), False)).applyfunc(rnd).equals(
                        sym_mat.inv().evalf().applyfunc(rnd)))
                    self.assertTrue(
                        sympy.Matrix(evaluate('cof({})'.format(mat_str), False)).equals(sym_mat.cofactor_matrix()))
                    self.assertTrue(sympy.Matrix(evaluate('rref({})'.format(mat_str), False)).equals(rref))
                    self.assertTrue(sympy.Matrix(evaluate('trnsform({})'.format(mat_str), False)).multiply(sym_mat).evalf().applyfunc(rnd).equals(rref.evalf().applyfunc(rnd)))
                    # TODO: trnsform doesn't work.
                except AssertionError:
                    print('FAILED')
                    print('matrix', sym_mat)
                    print('det', sym_mat.det())
                    print('trans', sym_mat.transpose())
                    print('inv', sym_mat.inv().evalf())
                    print('cof', sym_mat.cofactor_matrix())
                    print('rref', rref)
                    print('----')
                    print('det', evaluate('det({})'.format(mat_str), False))
                    print('trans', evaluate('trans({})'.format(mat_str), False))
                    print('inv', evaluate('inv({})'.format(mat_str), False))
                    print('cof', evaluate('cof({})'.format(mat_str), False))
                    print('rref', evaluate('rref({})'.format(mat_str), False))
                    print('trnsform', evaluate('trnsform({})'.format(mat_str), False))
                    print('trnsform * matrix', sympy.Matrix(evaluate('trnsform({})'.format(mat_str), False)).multiply(sym_mat))
                    print('trnsform * matrix with rounding',
                          sympy.Matrix(evaluate('trnsform({})'.format(mat_str), False)).multiply(sym_mat).evalf().applyfunc(rnd))
                    raise
                except EvaluationException as e:
                    print(e)
                    pass


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
