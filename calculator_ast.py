"""
A calculator implemented with an Abstract Syntax Tree (AST).
"""

import copy
import re
from collections import namedtuple, OrderedDict
from typing import List, Dict

import math

Token = namedtuple('Token', ('name', 'value'))
RuleMatch = namedtuple('RuleMatch', ('name', 'matched'))

token_map = OrderedDict((
    (r'\d+(?:\.\d+)?',    'NUM'),
    (r'sqrt',             'OPR'),
    (r'exp',              'OPR'),
    (r'[a-zA-Z_]+',       'IDT'),
    (r'=',                'EQL'),
    (r'\+',               'ADD'),
    (r'-',                'ADD'),
    (r'\*\*',             'POW'),
    (r'\*',               'MUL'),
    (r'\/',               'MUL'),
    (r'%',                'MUL'),
    (r'\^',               'POW'),
    (r'\(',               'LPA'),
    (r'\)',               'RPA')
))

rules_map = OrderedDict((
    ('idt', ('IDT EQL add', 'add')),
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

calc_map = {
    'add': lambda tokens: float(tokens[0].value) + float(tokens[2].value) if tokens[1].value == '+' else float(tokens[0].value) - float(tokens[2].value),
    'mul': lambda tokens: float(tokens[0].value) * float(tokens[2].value) if tokens[1].value == '*' else float(tokens[0].value) / float(tokens[2].value) if tokens[1].value == '/' else float(tokens[0].value) % float(tokens[2].value),
    'pow': lambda tokens: float(tokens[0].value) ** float(tokens[2].value),
    'opr': lambda tokens: {'sqrt': math.sqrt, 'exp': math.exp}[tokens[0].value](tokens[1].value),
    'neg': lambda tokens: float(tokens[1].value) if tokens[0].value == '+' else -float(tokens[1].value),
    'num': lambda tokens: float(tokens[0].value),
}


class Calculator:
    def __init__(self):
        self.vrs = {}

    def evaluate(self, eqtn: str):
        for e in eqtn.split(';'):
            ast = Ast(self._match(self._tokenize(e), 'idt')[0])
            print(ast)
            res = ast.evaluate(self.vrs)

            if isinstance(res, Token):
                return res.value

            elif isinstance(res, dict):
                self.vrs.update(res)

    def _tokenize(self, eqtn: str):
        tokens = []

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
            return self._fixed(ast.matched[0])

        # This flattens `num`s by removing parentheses.
        if ast.name == 'num' and len(ast.matched) is 3:
            return self._fixed(ast.matched[1])

        # This makes left-associative operations left-associative.
        for token_name, rule in left_assoc.items():
            if len(ast.matched) == 3 and ast.matched[1].name == token_name and isinstance(ast.matched[2], RuleMatch) and len(ast.matched[2].matched) == 3 and ast.matched[2].matched[1].name == token_name:
                ast.matched[0] = RuleMatch(rule, [ast.matched[0], ast.matched[1], ast.matched[2].matched[0]])
                ast.matched[1] = ast.matched[2].matched[1]
                ast.matched[2] = ast.matched[2].matched[2]
                return self._fixed(ast)

        # This converts implicit multiplication to regular multiplication.
        if ast.name == 'mui':
            m = RuleMatch('mul', [ast.matched[0], Token('MUL', '*'), ast.matched[1]])
            return self._fixed(m)

        # This removes the parentheses from an operation.
        if ast.name == 'opr' and len(ast.matched) == 4:
            ast.matched[1] = ast.matched[2]
            del ast.matched[3]
            del ast.matched[2]
            return self._fixed(ast)

        if isinstance(ast, RuleMatch):
            for i in range(len(ast.matched)):
                ast.matched[i] = self._fixed(ast.matched[i])

        return ast

    def evaluate(self, vrs: Dict[str, RuleMatch]):
        return self._evaluate(self.ast, vrs)

    def _evaluate(self, ast, vrs: Dict[str, RuleMatch]):
        if ast.name == 'idt':
            return {ast.matched[0].value: ast.matched[2]}

        for i in range(len(ast.matched)):
            token = ast.matched[i]

            if isinstance(token, RuleMatch):
                ast.matched[i] = self._evaluate(token, vrs)
                return self._evaluate(ast, vrs)
        else:
            if ast.matched[0].name == 'IDT':
                return self._evaluate(copy.deepcopy(vrs[ast.matched[0].value]), vrs)

            else:
                return Token('NUM', calc_map[ast.name](ast.matched))

    def infix(self):
        # TODO: Add parentheses where needed.
        return self._infix(self.ast)

    def _infix(self, ast: RuleMatch):
        return ' '.join(map(lambda t: t.value if isinstance(t, Token) else self._infix(t), ast.matched))

    def __str__(self):
        return self._str(self.ast)  # + '\n>> ' + self.infix()

    def _str(self, ast, depth=0):
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
