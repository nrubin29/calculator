"""
This file contains the Ast class, which represents an abstract syntax tree which can be evaluated.
"""
import copy
from typing import Dict

from common import RuleMatch, remove, left_assoc, Token
from rules import rule_value_map, rule_value_operation_map


class Ast:
    def __init__(self, root: RuleMatch):
        self.root = self._fixed(root)

    def _fixed(self, node):
        # print('**_fixed ast', ast)

        if not isinstance(node, RuleMatch):
            return node

        # This removes extraneous symbols from the tree.
        for i in range(len(node.matched) - 1, -1, -1):
            if node.matched[i].name in remove:
                del node.matched[i]

        # This flattens rules with a single matched rule.
        if len(node.matched) is 1 and isinstance(node.matched[0], RuleMatch) and node.name not in ('mbd', 'mrw'):  # The last condition fixes small matrices like [1], [1,2], and [1|2].
            return self._fixed(node.matched[0])

        # This makes left-associative operations left-associative.
        for token_name, rule in left_assoc.items():
            if len(node.matched) == 3 and node.matched[1].name == token_name and isinstance(node.matched[2], RuleMatch) and len(node.matched[2].matched) == 3 and node.matched[2].matched[1].name == token_name:
                node.matched[0] = RuleMatch(rule, [node.matched[0], node.matched[1], node.matched[2].matched[0]])
                node.matched[1] = node.matched[2].matched[1]
                node.matched[2] = node.matched[2].matched[2]
                return self._fixed(node)

        # This converts implicit multiplication to regular multiplication.
        if node.name == 'mui':
            return self._fixed(RuleMatch('mul', [node.matched[0], Token('MUL', '*'), node.matched[1]]))

        # This flattens matrix rows into parent matrix rows.
        if node.name == 'mrw':
            for i in range(len(node.matched) - 1, -1, -1):
                if node.matched[i].name == 'mrw':
                    node.matched[i:] = node.matched[i].matched
                    return self._fixed(node)

        # This flattens matrix bodies into parent matrix bodies.
        if node.name == 'mbd':
            for i in range(len(node.matched) - 1, -1, -1):
                if node.matched[i].name == 'mbd':
                    node.matched[i:] = node.matched[i].matched
                    return self._fixed(node)

        if isinstance(node, RuleMatch):
            for i in range(len(node.matched)):
                node.matched[i] = self._fixed(node.matched[i])

        return node

    def evaluate(self, vrs: Dict[str, RuleMatch]):
        return self._evaluate(self.root, vrs)

    def _evaluate(self, node, vrs: Dict[str, RuleMatch]):
        if node.name == 'asn':
            return {node.matched[0].value: node.matched[1]}

        for token in node.matched:
            if isinstance(token, RuleMatch) and not token.value:
                token.value = self._evaluate(token, vrs)

        values = [token.value for token in node.matched if isinstance(token, RuleMatch) and token.value]
        tokens = [token for token in node.matched if not isinstance(token, RuleMatch)]

        if node.matched[0].name == 'IDT':
            return self._evaluate(copy.deepcopy(vrs[node.matched[0].value]), vrs)

        elif node.name in rule_value_map:
            return rule_value_map[node.name](values, tokens)

        else:
            return rule_value_operation_map[node.name](values, tokens[0] if len(tokens) > 0 else None)  # This extra rule is part of the num hotfix.

    def infix(self) -> str:
        # TODO: Add parentheses and missing tokens.
        return self._infix(self.root)

    def _infix(self, node: RuleMatch) -> str:
        return ' '.join(map(lambda t: t.value if isinstance(t, Token) else self._infix(t), node.matched))

    def __str__(self):
        return str(self.root)  # + '\n>> ' + self.infix()

    def __repr__(self):
        return str(self)
