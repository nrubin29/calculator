"""
This file contains the Ast class, which represents an abstract syntax tree which can be evaluated.
"""
import copy
from typing import Dict

from common import RuleMatch, remove, left_assoc, Token, precedence
from rules import rule_value_map, rule_value_operation_map
from vartypes import TupleValue


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
        if len(node.matched) is 1 and isinstance(node.matched[0], RuleMatch) and node.name not in ('mbd', 'mrw', 'opb', 'asb'):  # The last condition fixes small matrices like [1], [1,2], and [1|2].
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

        # This flattens nested nodes into their parents if their parents are of the same type.
        for tpe in ('mrw', 'mbd', 'opb', 'asb'):
            if node.name == tpe:
                for i in range(len(node.matched) - 1, -1, -1):
                    if node.matched[i].name == tpe:
                        node.matched[i:] = node.matched[i].matched
                        return self._fixed(node)

        # This moves operators to the front of matched.
        if len(node.matched) == 3 and isinstance(node.matched[1], Token):
            node.matched = [node.matched[1]] + [node.matched[0]] + node.matched[2:]

        # This fixes the matched nodes.
        if isinstance(node, RuleMatch):
            for i in range(len(node.matched)):
                node.matched[i] = self._fixed(node.matched[i])

        return node

    def evaluate(self, vrs: Dict[str, RuleMatch]):
        return self._evaluate(self.root, vrs)

    def _evaluate(self, node, vrs: Dict[str, RuleMatch]):
        if node.name == 'asn':
            return {idt.value: (i, node.matched[1]) for i, idt in enumerate(node.matched[0].matched)}

        for token in node.matched:
            if isinstance(token, RuleMatch) and not token.value:
                token.value = self._evaluate(token, vrs)

        values = [token.value for token in node.matched if isinstance(token, RuleMatch) and token.value]
        tokens = [token for token in node.matched if not isinstance(token, RuleMatch)]

        if node.matched[0].name == 'IDT':
            i, rule = vrs[node.matched[0].value]
            result = self._evaluate(copy.deepcopy(rule), vrs)

            if isinstance(result, TupleValue):
                return result.value[i]

            return result

        elif node.name in rule_value_map:
            return rule_value_map[node.name](values, tokens)

        else:
            return rule_value_operation_map[node.name](values, tokens[0] if len(tokens) > 0 else None)  # This extra rule is part of the num hotfix.

    def infix(self) -> str:
        return self._infix(self.root)

    def _infix(self, node: RuleMatch) -> str:
        # TODO: Add missing tokens.
        s = ''

        if len(node.matched) == 1:
            s += node.matched[0].value

        else:
            for c in [node.matched[1]] + [node.matched[0]] + node.matched[2:]:
                if isinstance(c, RuleMatch):
                    if c.name in precedence and node.name in precedence and precedence.index(c.name) > precedence.index(node.name):
                        s += '(' + self._infix(c) + ') '

                    else:
                        s += self._infix(c) + ' '
                else:
                    s += c.value + ' '

        return s.strip()

    def prefix(self) -> str:
        return self._prefix(self.root)

    def _prefix(self, node: RuleMatch) -> str:
        s = ''

        for c in node.matched:
            if isinstance(c, RuleMatch):
                s += self._prefix(c) + ' '
            else:
                s += c.value + ' '

        return s.strip()

    def postfix(self) -> str:
        return self._postfix(self.root)

    def _postfix(self, node: RuleMatch) -> str:
        s = ''

        for c in node.matched[1:] + [node.matched[0]]:
            if isinstance(c, RuleMatch):
                s += self._postfix(c) + ' '
            else:
                s += c.value + ' '

        return s.strip()

    def __str__(self):
        return str(self.root)  # + '\n>> ' + self.infix()

    def __repr__(self):
        return str(self)
