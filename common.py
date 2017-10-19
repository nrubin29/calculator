"""
This file contains important information for the calculator.
"""

from collections import OrderedDict, namedtuple
from typing import List, Dict

Token = namedtuple('Token', ('name', 'value'))
Value = namedtuple('Value', ('type', 'value'))


class RuleMatch:
    def __init__(self, name: str, matched: List[Token]):
        self.name = name
        self.matched = matched
        self.value = None

    def __str__(self):
        return self._str(self)  # + '\n>> ' + self.infix()

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
    def __init__(self, keys: List, data: Dict):
        self._keys = keys
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._keys)

    def index(self, key):
        return self._keys.index(key)

    def key_at(self, i):
        return self._keys[i]


class IndexedOrderedDict(OrderedDict):
    def index(self, key):
        return list(self.keys()).index(key)

    def key_at(self, i):
        return list(self.keys())[i]


rules_map = IndexedOrderedDict((
    ('asn', ('IDT EQL add',)),
    ('mat', ('LBR mbd RBR',)),
    ('mbd', ('mrw PPE mbd',)),
    ('mrw', ('add CMA mrw',)),
    ('add', ('mul ADD add',)),
    ('mui', ('pow mul',)),
    ('mul', ('pow MUL mul',)),
    ('pow', ('opr POW pow',)),
    ('opr', ('OPR LPA mat RPA',)),
    ('neg', ('ADD num', 'ADD opr')),
    ('var', ('IDT',)),
    ('num', ('NUM', 'LPA add RPA')),
))

# This helps a little bit, but not much.
# Perhaps construct a graph (single-linked list) (asn -> mat -> mbd, etc.) and pass nodes in evaluate().
rules_map = ImmutableIndexedDict(['asn', 'mat', 'mbd', 'mrw', 'add', 'mui', 'mul', 'pow', 'opr', 'neg', 'var', 'num'], dict((('asn', ('IDT EQL add',)),('mat', ('LBR mbd RBR',)),('mbd', ('mrw PPE mbd',)),('mrw', ('add CMA mrw',)),('add', ('mul ADD add',)),('mui', ('pow mul',)),('mul', ('pow MUL mul',)),('pow', ('opr POW pow',)),('opr', ('OPR LPA mat RPA',)),('neg', ('ADD num', 'ADD opr')),('var', ('IDT',)),('num', ('NUM', 'LPA add RPA')),)))


left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}


class EvaluationException(Exception):
    pass
