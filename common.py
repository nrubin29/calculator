"""
This file contains important information for the calculator.
"""

from collections import OrderedDict, namedtuple
from typing import List

Token = namedtuple('Token', ('name', 'value'))
Value = namedtuple('Value', ('type', 'value'))


class RuleMatch:
    def __init__(self, name: str, matched: List[Token]):
        self.name = name
        self.matched = matched
        self.value = None

    def __str__(self):
        return self._str(self)

    def __repr__(self):
        return str(self)

    def _str(self, ast, depth=0) -> str:
        output = (('\t' * depth) + ast.name + ' = ' + str(ast.value if ast.value else None)) + '\n'

        for matched in ast.matched:
            if isinstance(matched, RuleMatch) and matched.matched:
                output += self._str(matched, depth + 1)

            else:
                output += (('\t' * (depth + 1)) + matched.name + ': ' + matched.value) + '\n'

        return output


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


class ImmutableIndexedDict:
    def __init__(self, data):
        self._keys = tuple(item[0] for item in data)
        self._key_indices = {key: self._keys.index(key) for key in self._keys}  # Caching indices cuts down on runtime.
        self._len = len(self._keys)
        self._data = dict(data)

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return self._len

    def index(self, key):
        return self._key_indices[key]

    def key_at(self, i):
        return self._keys[i]


rules_map = ImmutableIndexedDict((
    ('asn', ('IDT EQL mat',)),
    ('mat', ('LBR mbd RBR',)),
    ('mbd', ('mrw PPE mbd', 'mrw')),
    ('mrw', ('add CMA mrw', 'add')),
    ('add', ('mul ADD add',)),
    ('mui', ('pow mul',)),
    ('mul', ('pow MUL mul',)),
    ('pow', ('opr POW pow',)),
    ('opr', ('OPR LPA mat RPA',)),
    ('neg', ('ADD num', 'ADD opr')),
    ('var', ('IDT',)),
    ('num', ('NUM', 'LPA add RPA')),
))


left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}


class EvaluationException(Exception):
    pass
