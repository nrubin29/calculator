import re
from collections import namedtuple, OrderedDict
from typing import List

Token = namedtuple('Token', ('name', 'value'))
RuleMatch = namedtuple('RuleMatch', ('name', 'matched'))

token_map = {
    'NUM': r'\d+',
    'ADD': r'\+',
    'SUB': r'\-',
    'MUL': r'\*',
    'DIV': r'\/',
}

rules_map = OrderedDict((
    ('add', ('sub', 'mul ADD add', 'mul')),
    ('sub', ('NUM SUB mul', 'mul SUB add')),
    ('mul', ('div DIV mul', 'div', 'NUM MUL mul', 'NUM')),
    ('div', ('NUM DIV mul',))
))

calc_map = {
    'add': lambda tokens: float(tokens[0].value) + float(tokens[2].value),
    'sub': lambda tokens: float(tokens[0].value) - float(tokens[2].value),
    'mul': lambda tokens: float(tokens[0].value) * float(tokens[2].value),
    'div': lambda tokens: float(tokens[0].value) / float(tokens[2].value)
}


class Calculator:
    def __init__(self, eqtn: str):
        self.eqtn = eqtn
        self.tokens = [[Token(key, token) for key, value in token_map.items() if re.match(value, token)][0] for token in
                       eqtn.split(' ')]

    def ast(self):
        return Ast(self._match(self.tokens, 'add')[0])

    def _match(self, tokens: List[Token], target_rule: str=None):
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

        if (ast.name == 'mul' or ast.name == 'add') and len(ast.matched) is 1:
            return self._fixed(ast.matched[0])

        if isinstance(ast, RuleMatch):
            for i in range(len(ast.matched)):
                ast.matched[i] = self._fixed(ast.matched[i])

        return ast

    def evaluate(self):
        return self._evaluate(self.ast).value

    def _evaluate(self, ast):
        for i in range(len(ast.matched)):
            token = ast.matched[i]

            if isinstance(token, RuleMatch):
                ast.matched[i] = self._evaluate(token)
                return self._evaluate(ast)
        else:
            # print('can do operation for', ast)
            return Token('NUM', calc_map[ast.name](ast.matched))

    def __str__(self):
        return self._str(self.ast)

    def _str(self, ast, depth=0):
        output = (('\t' * depth) + ast.name) + '\n'

        for matched in ast.matched:
            # print('**matched', matched)
            if isinstance(matched, RuleMatch) and matched.matched:
                output += self._str(matched, depth + 1)

            else:
                output += (('\t' * (depth + 1)) + matched.name + ': ' + matched.value) + '\n'

        return output
