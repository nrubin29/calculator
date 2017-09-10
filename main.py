"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

from calculator import Calculator

if __name__ == '__main__':
    calc = Calculator()

    while True:
        print(calc.evaluate(input('>> ')))
