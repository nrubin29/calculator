"""
This file contains the Calculator class, which accept an equation and generates an AST, and also keeps track of variables.
"""
from typing import List

import re

from ast import Ast
from common import Token, token_map, rules_map, RuleMatch
from vartypes import Value


class Calculator:
    def __init__(self):
        self.vrs = {}

    def evaluate(self, eqtn: str, verbose=True) -> Value:
        for e in eqtn.split(';'):
            root, remaining_tokens = self._match(self._tokenize(e), 'asn')

            if remaining_tokens:
                raise Exception('Invalid equation (bad format)')

            ast = Ast(root)
            res = ast.evaluate(self.vrs)

            if isinstance(res, Value):
                ast.root.value = res

                if verbose:
                    print(ast)

                return res

            elif isinstance(res, dict):
                print(ast)
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

        if target_rule.isupper():  # This is a token, not a rule.
            if tokens and tokens[0].name == target_rule:
                return tokens[0], tokens[1:]

            return None, None

        for pattern in rules_map[target_rule]:
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

        idx = rules_map.index(target_rule)
        if idx is not None and idx + 1 < len(rules_map):
            return self._match(tokens, rules_map.key_at(idx + 1))

        return None, None
