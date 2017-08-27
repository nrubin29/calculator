import random
import unittest

from calculator_ast import Calculator


def evaluate(eqtn: str):
    print(eqtn)
    calc = Calculator(eqtn)
    # print(calc.tokens)
    ast = calc.ast()
    print(ast)
    print(ast.evaluate())
    return ast.evaluate()


class SimpleAdditionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 2'), 3.0)
        self.assertEqual(evaluate('2 + 3'), 5.0)


class SimpleSubtractionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 - 2'), -1.0)
        self.assertEqual(evaluate('3 - 2'), 1.0)


class SimpleMultiplicationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 * 1'), 1.0)
        self.assertEqual(evaluate('2 * 3'), 6.0)


class SimpleDivisionTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 / 1'), 1.0)
        self.assertEqual(evaluate('24 / 4 / 6'), 1.0)
        self.assertEqual(round(evaluate('2 / 3'), 3), 0.667)
        self.assertEqual(evaluate('112 / 2 / 4 / 7'), 2.0)


class SimplePowerTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('2 ^ 3'), 8.0)
        self.assertEqual(evaluate('2 ^ 2 ^ 2 ^ 2'), 65536.0)


class SimpleParenthesisTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('( 1 + 2 ) * 3'), 9.0)
        self.assertEqual(evaluate('( 1 + 2 ) ^ ( 2 * 3 - 2 )'), 81.0)


class CombinationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 2 * 3 + 4 * 5'), 27)
        self.assertEqual(evaluate('10 ^ 2 - 2 ^ 3 + 3 * 2 ^ 4'), 140.0)
        self.assertEqual(evaluate('1 + 2 - 3 ^ 4 * 5'), -402.0)
        self.assertEqual(evaluate('2 ^ 2 * 3 ^ 2'), 36.0)


class RandomTests(unittest.TestCase):
    def runTest(self):
        for _ in range(100):
            eqtn = ''

            for i in range(10):
                eqtn += '{} {} '.format(random.randint(1, 100), random.choice(('+', '-', '*', '/')))

            eqtn = eqtn.strip()[:-2]

            self.assertEqual(evaluate(eqtn), eval(eqtn.replace('^', '**')))

if __name__ == '__main__':
    unittest.main()
