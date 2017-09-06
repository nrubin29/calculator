"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

import copy
import re
from collections import namedtuple, OrderedDict
from enum import Enum
from typing import List, Dict, Union

import math

Token = namedtuple('Token', ('name', 'value'))
RuleMatch = namedtuple('RuleMatch', ('name', 'matched'))

token_map = OrderedDict((
    (r'\d+(?:\.\d+)?',      'NUM'),
    (r'sqrt',               'OPR'),
    (r'exp',                'OPR'),
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
    ('opr', ('OPR LPA add RPA', 'neg')),
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

calc_map = {
    'add': lambda tokens: Token('NUM', float(tokens[0].value) + float(tokens[2].value) if tokens[1].value == '+' else float(tokens[0].value) - float(tokens[2].value)),
    'mul': lambda tokens: Token('NUM', float(tokens[0].value) * float(tokens[2].value) if tokens[1].value == '*' else float(tokens[0].value) / float(tokens[2].value) if tokens[1].value == '/' else float(tokens[0].value) % float(tokens[2].value)),
    'pow': lambda tokens: Token('NUM', float(tokens[0].value) ** float(tokens[2].value)),
    'opr': lambda tokens: Token('NUM', {'sqrt': math.sqrt, 'exp': math.exp}[tokens[0].value](tokens[1].value)),
    'neg': lambda tokens: Token('NUM', float(tokens[1].value) if tokens[0].value == '+' else -float(tokens[1].value)),
    'num': lambda tokens: Token('NUM', float(tokens[0].value)),
    'mat': lambda tokens: Token('MAT', [float(tokens[1].value)])
}


class Calculator:
    def __init__(self):
        self.vrs = {}

    def evaluate(self, eqtn: str) -> Value:
        for e in eqtn.split(';'):
            root, remaining_tokens = self._match(self._tokenize(e), 'idt')

            if remaining_tokens:
                raise Exception('Invalid equation (bad format)')

            ast = Ast(root)
            print(ast)
            res = ast.evaluate(self.vrs)

            if isinstance(res, Value):
                return res

            elif isinstance(res, dict):
                self.vrs.update(res)

    def _tokenize(self, eqtn: str) -> List[Token]:
        tokens = []

        if re.sub('(' + ')|('.join(token_map.keys()) + ')', '', 'eqtn').strip():
            raise Exception('Invalid equation (illegal tokens)')

        for match in re.findall('(' + ')|('.join(token_map.keys()) + ')', eqtn):
            entry = next(filter(lambda entry: entry[1] != '', enumerate(match)), None)
            tokens.append(Token(list(token_map.values())[entry[0]], entry[1]))

        return tokens

    def _match(self, tokens: List[Token], target_rule: str):
        # print('match', tokens, target_rule)

        if tokens and tokens[0].name == target_rule:  # This is a token, not a rule.
            return tokens[0], tokens[1:]

        for pattern in rules_map.get(target_rule, ()):
            # print('trying pattern', pattern)

            remaining_tokens = tokens
            matched = []

            for pattern_token in pattern.split():
                # print('checking pattern_token', pattern_token)
                m, remaining_tokens = self._match(remaining_tokens, pattern_token)

                if not m:
                    # print('failed pattern match')
                    break

                matched.append(m)
            else:
                # Success!
                return RuleMatch(target_rule, matched), remaining_tokens
        return None, None


class Ast:
    def __init__(self, ast: RuleMatch):
        self.ast = self._fixed(ast)

    def _fixed(self, ast):
        # print('**_fixed ast', ast)

        if not isinstance(ast, RuleMatch):
            return ast

        # This flattens rules with a single matched element.
        if len(ast.matched) is 1 and ast.name != 'num':
            if ast.name != 'mat' or ast.matched[0].name != 'mbd':
                return self._fixed(ast.matched[0])

        # This removes extraneous symbols from the tree.
        for i in range(len(ast.matched) - 1, -1, -1):
            if ast.matched[i].name in remove:
                del ast.matched[i]

        # This makes left-associative operations left-associative.
        for token_name, rule in left_assoc.items():
            if len(ast.matched) == 3 and ast.matched[1].name == token_name and isinstance(ast.matched[2], RuleMatch) and len(ast.matched[2].matched) == 3 and ast.matched[2].matched[1].name == token_name:
                ast.matched[0] = RuleMatch(rule, [ast.matched[0], ast.matched[1], ast.matched[2].matched[0]])
                ast.matched[1] = ast.matched[2].matched[1]
                ast.matched[2] = ast.matched[2].matched[2]
                return self._fixed(ast)

        # This converts implicit multiplication to regular multiplication.
        if ast.name == 'mui':
            return self._fixed(RuleMatch('mul', [ast.matched[0], Token('MUL', '*'), ast.matched[1]]))

        # This flattens matrix rows into parent matrix rows.
        if ast.name == 'mrw' and ast.matched[1].name == 'mrw':
            ast.matched[1:] = ast.matched[1].matched
            return self._fixed(ast)

        # This flattens matrix bodies into parent matrix bodies.
        if ast.name == 'mbd' and ast.matched[1].name == 'mbd':
            ast.matched[1:] = ast.matched[1].matched
            return self._fixed(ast)

        if isinstance(ast, RuleMatch):
            for i in range(len(ast.matched)):
                ast.matched[i] = self._fixed(ast.matched[i])

        return ast

    def evaluate(self, vrs: Dict[str, RuleMatch]):
        res = self._evaluate(self.ast, vrs)

        if isinstance(res, Token):
            return Value(value_map[res.name], res.value)

        return res

    def _evaluate(self, ast, vrs: Dict[str, RuleMatch]) -> Union[Dict[str, RuleMatch], Token]:
        if ast.name == 'idt':
            return {ast.matched[0].value: ast.matched[1]}

        for i in range(len(ast.matched)):
            token = ast.matched[i]

            if isinstance(token, RuleMatch):
                ast.matched[i] = self._evaluate(token, vrs)
                return self._evaluate(ast, vrs)
        else:
            if ast.matched[0].name == 'IDT':
                return self._evaluate(copy.deepcopy(vrs[ast.matched[0].value]), vrs)

            else:
                return calc_map[ast.name](ast.matched)

    def infix(self) -> str:
        # TODO: Add parentheses where needed.
        return self._infix(self.ast)

    def _infix(self, ast: RuleMatch) -> str:
        return ' '.join(map(lambda t: t.value if isinstance(t, Token) else self._infix(t), ast.matched))

    def __str__(self):
        return self._str(self.ast)  # + '\n>> ' + self.infix()

    def _str(self, ast, depth=0) -> str:
        output = (('\t' * depth) + ast.name) + '\n'

        for matched in ast.matched:
            # print('**matched', matched)
            if isinstance(matched, RuleMatch) and matched.matched:
                output += self._str(matched, depth + 1)

            else:
                output += (('\t' * (depth + 1)) + matched.name + ': ' + matched.value) + '\n'

        return output


if __name__ == '__main__':
    calc = Calculator()

    while True:
        print(calc.evaluate(input('>> ')))
