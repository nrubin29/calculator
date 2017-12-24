"""
This file contains important information for the calculator.
"""

from collections import OrderedDict, namedtuple
from typing import List

Token = namedtuple('Token', ('name', 'value'))


class RuleMatch:
    def __init__(self, name: str, matched: List[Token]):
        self.name = name
        self.matched = matched
        self.value = None

    def __str__(self):
        return self._str(self)

    def __repr__(self):
        return str(self)

    def _str(self, node, depth=0) -> str:
        output = (('\t' * depth) + node.name + ' = ' + str(node.value.value if node.value else None)) + '\n'

        for matched in node.matched:
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
    (r'solve',              'OPR'),
    (r'eval',               'OPR'),
    (r'ls',                 'OPR'),
    (r'qr',                 'OPR'),
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
        self._keys = tuple(item[0] for item in data if not item[0].startswith('^'))
        self._data = {key.lstrip('^'): values for key, values in data}

        # Caching indices cuts down on runtime.
        idx = 0
        self._key_indices = {}

        for key in tuple(item[0] for item in data):
            if not key.startswith('^'):
                self._key_indices[key] = idx
                idx += 1

        self._len = len(self._key_indices)

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return self._len

    def index(self, key):
        return self._key_indices.get(key, None)

    def key_at(self, i):
        return self._keys[i]


rules_map = ImmutableIndexedDict((
    ('asn', ('asb EQL add',)),
    ('^asb', ('IDT CMA asb', 'IDT')),
    ('add', ('mul ADD add', 'mui ADD add',)),
    ('mui', ('pow mul',)),
    ('mul', ('pow MUL mul',)),
    ('pow', ('opr POW pow',)),
    ('opr', ('OPR LPA opb RPA',)),
    ('^opb', ('add CMA opb', 'add')),
    ('neg', ('ADD num', 'ADD opr')),
    ('var', ('IDT',)),
    ('num', ('NUM', 'LPA add RPA')),
    ('mat', ('LBR mbd RBR',)),
    ('^mbd', ('mrw PPE mbd', 'mrw')),
    ('^mrw', ('add CMA mrw', 'add')),
))


left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}

operations = ('pos', 'neg', 'add', 'sub', 'mul', 'div', 'mod', 'pow', 'sqrt', 'exp', 'identity', 'det', 'trans', 'cof', 'adj', 'inv', 'rref', 'trnsform', 'solve', 'ls', 'eval')


class EvaluationException(Exception):
    pass
