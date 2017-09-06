"""
Unit tests for the AST calculator.
"""

import random
import unittest

from calculator_ast import Calculator


def evaluate(eqtn: str):
    print(eqtn)
    calc = Calculator()
    res = calc.evaluate(eqtn)
    print(res)
    return res.value


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
        # self.assertEqual(evaluate('[1,2]'), [1.0])
        # self.assertEqual(evaluate('[1,2|4,5]'), [1.0])
        self.assertEqual(evaluate('[1,0,0|0,1,0|0,0,1]'), [1.0])


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
