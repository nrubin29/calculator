"""
A calculator implemented with the Shunting Yard Algorithm. The AST version is far superior and this version should be disregarded.
"""

import re
from collections import namedtuple
from operator import add, sub, mul, truediv, pow, mod

Operator = namedtuple('Operator', ('symbol', 'function', 'precedence', 'associativity'))

operators = {
    '+': Operator('+', add, 2, 'l'),
    '-': Operator('-', sub, 2, 'l'),
    '*': Operator('*', mul, 3, 'l'),
    '/': Operator('/', truediv, 3, 'l'),
    '%': Operator('%', mod, 3, 'l'),
    '^': Operator('^', pow, 4, 'r'),
    '(': Operator('(', None, 5, ''),
    ')': Operator(')', None, 5, '')
}

expr = r'[\+\-\*\/|\^\(\)]|\d+'
eqtn = '3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3'  # => 3.0001220703  # input()

rpn = []
ops = []

for token in re.findall(expr, eqtn):
    if re.match(r'\d+', token):
        rpn.append(token)

    elif token is '(':
        ops.append(token)

    elif token is ')':
        for op in reversed(list(map(operators.__getitem__, ops))):
            if op.symbol is not '(':
                rpn.append(ops.pop())

            else:
                break

        ops.pop()

    else:
        for op in reversed(list(map(operators.__getitem__, ops))):
            if op.symbol is not '(' and op.precedence >= operators[token].precedence and op.associativity is 'l':
                rpn.append(ops.pop())

            else:
                break

        ops.append(token)

    # print('{:20s}|{:20s}|{:20s}'.format(token, ' '.join(rpn), ' '.join(ops)).strip())

# print()

while len(ops) > 0:
    rpn.append(ops.pop())

print(' '.join(rpn))

output = []

while len(rpn) > 0:
    token = rpn.pop(0)
    if re.match(r'\d+', token):
        output.append(int(token))

    else:
        b, a = output.pop(), output.pop()
        output.append(operators[token].function(a, b))

print(output[0])
