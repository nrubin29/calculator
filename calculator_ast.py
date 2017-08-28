import re
from collections import namedtuple, OrderedDict
from typing import List

Token = namedtuple('Token', ('name', 'value'))
RuleMatch = namedtuple('RuleMatch', ('name', 'matched'))

token_map = {
    r'\d+': 'NUM',
    r'\+':  'ADD',
    r'\-':  'ADD',
    r'\*':  'MUL',
    r'\/':  'MUL',
    r'\^':  'POW',
    r'\(':  'LPA',
    r'\)':  'RPA'
}

rules_map = OrderedDict((
    ('num', ('NUM', 'LPA add RPA')),
    ('add', ('mul ADD add', 'mul')),
    ('mul', ('pow MUL mul', 'pow mul', 'pow')),
    ('pow', ('num POW pow', 'num'))
))

left_assoc = {
    'ADD': 'add',
    'MUL': 'mul',
}

calc_map = {
    'add': lambda tokens: float(tokens[0].value) + float(tokens[2].value) if tokens[1].value == '+' else float(tokens[0].value) - float(tokens[2].value),
    'mul': lambda tokens: float(tokens[0].value) * float(tokens[2].value) if tokens[1].value == '*' else float(tokens[0].value) / float(tokens[2].value),
    'pow': lambda tokens: float(tokens[0].value) ** float(tokens[2].value)
}


class Calculator:
    def __init__(self, eqtn: str):
        self.eqtn = eqtn
        self.tokens = [[Token(value, token) for key, value in token_map.items() if re.match(key, token)][0] for token in
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

        if not isinstance(ast, RuleMatch):
            return ast

        # This flattens rules with a single matched element.
        if len(ast.matched) is 1:
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

        # This adds the multiplication symbol to implicit multiplication.
        if ast.name == 'mul' and len(ast.matched) == 2:
            ast.matched.append(ast.matched[1])
            ast.matched[1] = Token('MUL', '*')
            return self._fixed(ast)

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
