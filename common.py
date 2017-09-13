"""
This file contains important information for the calculator.
"""

from collections import namedtuple, OrderedDict
from enum import Enum

Token = namedtuple('Token', ('name', 'value'))
RuleMatch = namedtuple('RuleMatch', ('name', 'matched'))

token_map = OrderedDict((
    (r'\d+(?:\.\d+)?',      'NUM'),
    (r'sqrt',               'OPR'),
    (r'exp',                'OPR'),
    (r'det',                'OPR'),
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
    ('idt', ('IDT EQL add', 'mat')),
    ('mat', ('LBR mbd RBR', 'add')),
    ('mbd', ('mrw PPE mbd', 'mrw', 'add')),
    ('mrw', ('add CMA mrw', 'add')),
    ('add', ('mul ADD add', 'mui', 'mul')),
    ('mui', ('pow mul',)),
    ('mul', ('pow MUL mul', 'pow')),
    ('pow', ('opr POW pow', 'opr')),
    ('opr', ('OPR LPA mat RPA', 'neg')),
    ('neg', ('ADD num', 'ADD opr', 'num')),
    ('num', ('NUM', 'IDT', 'LPA add RPA')),
))

left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}


class Type(Enum):
    Number = 0
    Matrix = 1


Value = namedtuple('Value', ('type', 'value'))
value_map = {
    'NUM': Type.Number,
    'MAT': Type.Matrix
}