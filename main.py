"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

from calculator import Calculator
import sys

if __name__ == '__main__':
    calc = Calculator()

    if len(sys.argv) > 1:
        for line in ' '.join(sys.argv[1:]).split(';'):
            print(calc.evaluate(line))

    else:
        while True:
            print(calc.evaluate(input('>> ')))
