"""
This file contains the Ast class, which represents an abstract syntax tree which can be evaluated.
"""
import copy
from typing import Dict, Union

from common import RuleMatch, remove, left_assoc, Token, Value, value_map
from rules import calc_map


class Ast:
    def __init__(self, ast: RuleMatch):
        self.ast = self._fixed(ast)

    def _fixed(self, ast):
        # print('**_fixed ast', ast)

        if not isinstance(ast, RuleMatch):
            return ast

        # This flattens rules with a single matched element.
        if len(ast.matched) is 1 and ast.name != 'num' and ast.name != 'mbd':
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
        if ast.name == 'mbd' and len(ast.matched) > 1 and ast.matched[1].name == 'mbd':
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
