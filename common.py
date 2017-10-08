"""
This file contains important information for the calculator.
"""

from collections import OrderedDict
from typing import List

from token_value import Token
from vartypes import Number, Matrix, MatrixRow


class RuleMatch:
    def __init__(self, name: str, matched: List[Token]):
        self.name = name
        self.matched = matched
        self.processed = None

    def __str__(self):
        return self._str(self)  # + '\n>> ' + self.infix()

    def __repr__(self):
        return str(self)

    def _str(self, ast, depth=0) -> str:
        output = (('\t' * depth) + ast.name + ' = ' + str(ast.processed.value if ast.processed else None)) + '\n'

        for matched in ast.matched:
            if isinstance(matched, RuleMatch) and matched.matched:
                output += self._str(matched, depth + 1)

            else:
                output += (('\t' * (depth + 1)) + matched.name + ': ' + matched.value) + '\n'

        return output

    # def __str__(self):
    #     return 'RuleMatch(' + ', '.join(map(str, [self.name, self.matched])) + ')'
    #
    # def __repr__(self):
    #     return str(self)


class ProcessedRuleMatch:
    def __init__(self, operation, operands: List, raw_args=False):
        self.operation = operation
        self.operands = operands

        if raw_args:
            self.value = operation(operands)
        else:
            self.value = operation(*operands)


token_map = OrderedDict((
    (r'\d+(?:\.\d+)?',      'NUM'),
    (r'sqrt',               'OPR'),
    (r'exp',                'OPR'),
    (r'det',                'OPR'),
    (r'adj',                'OPR'),
    (r'trans',              'OPR'),
    (r'cof',                'OPR'),
    (r'inv',                'OPR'),
    (r'identity',           'OPR'),
    (r'trnsform',           'OPR'),
    (r'rref',               'OPR'),
    (r'[a-zA-Z_]+',         'IDT'),
    (r'=',                  'EQL'),
    (r'\+',                 'ADD'),
    (r'-',                  'ADD'),
    (r'\*\*',               'POW'),
    (r'\*',                 'MUL'),
    (r'\/',                 'MUL'),
    (r'%',                  'MUL'),
    (r'\^',                 'POW'),
    (r'\(',                 'LPA'),
    (r'\)',                 'RPA'),
    (r'\[',                 'LBR'),
    (r'\]',                 'RBR'),
    (r'\,',                 'CMA'),
    (r'\|',                 'PPE')
))

remove = ('EQL', 'LPA', 'RPA', 'LBR', 'RBR', 'CMA', 'PPE')

rules_map = OrderedDict((
    ('idt', ('IDT EQL add',)),
    ('mat', ('LBR mbd RBR',)),
    ('mbd', ('mrw PPE mbd',)),
    ('mrw', ('add CMA mrw',)),
    ('add', ('mul ADD add',)),
    ('mui', ('pow mul',)),
    ('mul', ('pow MUL mul',)),
    ('pow', ('opr POW pow',)),
    ('opr', ('OPR LPA mat RPA',)),
    ('neg', ('ADD num', 'ADD opr')),
    ('num', ('NUM', 'IDT', 'LPA add RPA')),
))


def rm_index(key):
    return list(rules_map.keys()).index(key)


def rm_key_at(i):
    return list(rules_map.keys())[i]


left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}

value_map = {
    'NUM': Number,
    'MAT': Matrix,
    'MRW': MatrixRow
}
