import random
import unittest

from calculator_ast import Calculator


def evaluate(eqtn: str):
    calc = Calculator(eqtn)
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
        # self.assertEqual(evaluate('24 / 4 / 6'), 1.0)
        self.assertEqual(round(evaluate('2 / 3'), 3), 0.667)


class SimpleAdditionMultiplicationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 1 * 2'), 3.0)
        self.assertEqual(evaluate('1 * 2 + 1'), 3.0)


class CombinationTests(unittest.TestCase):
    def runTest(self):
        self.assertEqual(evaluate('1 + 2 * 3 + 4 * 5'), 27)


# class RandomTests(unittest.TestCase):
#     def runTest(self):
#         for _ in range(100):
#             eqtn = ''
#
#             for i in range(3):
#                 eqtn += '{} {} '.format(random.randint(0, 100), random.choice(('+', '-', '*', '/')))
#
#             eqtn = eqtn.strip()[:-2]
#
#             print(eqtn)
#             self.assertEqual(evaluate(eqtn), eval(eqtn))

if __name__ == '__main__':
    unittest.main()
