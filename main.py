"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

from calculator import Calculator
import sys

if __name__ == '__main__':
    calc = Calculator()

    if len(sys.argv) > 2:
        tpe = sys.argv[1]

        for line in ' '.join(sys.argv[2:]).split(';'):
            print(calc.evaluate(line, tpe))

    else:
        tpe = input('What type of expressions will you be inputting? Enter prefix, postfix, or infix: ')

        while True:
            print(calc.evaluate(input('>> '), tpe))
