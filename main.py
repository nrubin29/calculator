"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

from calculator import Calculator
import sys

if __name__ == '__main__':
    calc = Calculator()

    if len(sys.argv) > 1:
        print(calc.evaluate(' '.join(sys.argv[1:])))

    else:
        while True:
            print(calc.evaluate(input('>> ')))
