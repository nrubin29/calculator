"""
This file contains methods to handle processing RuleMatches
"""
from typing import List

from common import Token, ProcessedRuleMatch
from token_value import Value
from vartypes import Number, MatrixRow, Matrix


def num(_, tokens: List[Token]) -> ProcessedRuleMatch:
    return ProcessedRuleMatch(Number.new, tokens, raw_args=True)


def mrw(values: List[Value], _) -> ProcessedRuleMatch:
    return ProcessedRuleMatch(MatrixRow.new, values, raw_args=True)


def mbd(values: List[Value], _) -> ProcessedRuleMatch:
    return ProcessedRuleMatch(Matrix.new, values, raw_args=True)


def num_hotfix(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    # In certain cases, we attempt to process a `num` even though it's already been processed.
    return ProcessedRuleMatch(lambda x: x, operands)


def add(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    return ProcessedRuleMatch({'+': operands[0].type.add, '-': operands[0].type.sub}[operator.value], operands)


def mul(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    return ProcessedRuleMatch({'*': operands[0].type.mul, '/': operands[0].type.div, '%': operands[0].type.mod}[operator.value], operands)


def pow(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    return ProcessedRuleMatch(operands[0].type.pow, operands)


def opr(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    return ProcessedRuleMatch(getattr(operands[0].type, operator.value), operands)


def neg(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    return ProcessedRuleMatch({'+': operands[0].type.pos, '-': operands[0].type.neg}[operator.value], operands)


def mat(operands: List[Value], operator: Token) -> ProcessedRuleMatch:
    # Since mbd creates the matrix, we just want this to return the matrix.
    return ProcessedRuleMatch(lambda x: x, operands)


# The mapping for num, mrw, mbd.
rule_process_value_map = {
    'num': num,
    'mrw': mrw,
    'mbd': mbd,
}

# The mapping for all other rules.
rule_process_map = {
    'add': add,
    'mul': mul,
    'pow': pow,
    'opr': opr,
    'neg': neg,
    'mat': mat,
    'num': num_hotfix
}
