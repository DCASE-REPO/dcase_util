#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import logging


class SimpleMathStringEvaluator(object):
    """Simple math string evaluator

    Uses pyparsing for safe string evaluation.

    Implementation after pyparsing example: http://pyparsing.wikispaces.com/file/view/eval_arith.py

    """

    def __init__(self):
        try:
            from pyparsing import Word, nums, alphas, Combine, oneOf, opAssoc, operatorPrecedence

        except ImportError:
            message = '{name}: Unable to import pyparsing module. You can install it with `pip install pyparsing`.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ImportError(message)

        # Define the parser
        integer = Word(nums).setParseAction(lambda t: int(t[0]))
        real = Combine(Word(nums) + "." + Word(nums))
        variable = Word(alphas, exact=1)
        operand = real | integer | variable

        # Operators
        self.operators = {
            'sign': oneOf('+ -'),
            'multiply': oneOf('* /'),
            'plus': oneOf('+ -'),
            'comparision': oneOf('< <= > >= != = <> LT GT LE GE EQ NE'),
        }

        def operator_operands(token_list):
            """generator to extract operators and operands in pairs."""
            it = iter(token_list)
            while True:
                try:
                    o1 = next(it)
                    o2 = next(it)
                    yield (o1, o2)
                except StopIteration:
                    break

        class EvalConstant(object):
            """Class to evaluate a parsed constant or variable."""

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, vars):
                if self.value in vars:
                    return vars[self.value]
                else:
                    try:
                        return int(self.value)
                    except ValueError:
                        return float(self.value)

        class EvalAddOp(object):
            """Class to evaluate addition and subtraction expressions."""

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, vars):
                sum = self.value[0].eval(vars)
                for op, val in operator_operands(self.value[1:]):
                    if op == '+':
                        sum += val.eval(vars)
                    if op == '-':
                        sum -= val.eval(vars)
                return sum

        class EvalSignOp(object):
            """Class to evaluate expressions with a leading + or - sign."""

            def __init__(self, tokens):
                self.sign, self.value = tokens[0]

            def eval(self, vars_):
                multiplier = {'+': 1, '-': -1}[self.sign]
                return multiplier * self.value.eval(vars_)

        class EvalMultiplicationOp(object):
            """Class to evaluate multiplication and division expressions."""

            def __init__(self, tokens):
                self.operator_map = {
                    '*': lambda a, b: a * b,
                    '/': lambda a, b: a / b,
                }
                self.value = tokens[0]

            def eval(self, vars):
                prod = self.value[0].eval(vars)
                for op, val in operator_operands(self.value[1:]):
                    fn = self.operator_map[op]
                    val2 = val.eval(vars)
                    prod = fn(prod, val2)
                return prod

        class EvalComparisonOp(object):
            """Class to evaluate comparison expressions"""

            def __init__(self, tokens):
                self.value = tokens[0]
                self.operator_map = {
                    "<": lambda a, b: a < b,
                    "<=": lambda a, b: a <= b,
                    ">": lambda a, b: a > b,
                    ">=": lambda a, b: a >= b,
                    "!=": lambda a, b: a != b,
                    "=": lambda a, b: a == b,
                    "LT": lambda a, b: a < b,
                    "LE": lambda a, b: a <= b,
                    "GT": lambda a, b: a > b,
                    "GE": lambda a, b: a >= b,
                    "NE": lambda a, b: a != b,
                    "EQ": lambda a, b: a == b,
                    "<>": lambda a, b: a != b,
                }

            def eval(self, vars):
                val1 = self.value[0].eval(vars)
                for op, val in operator_operands(self.value[1:]):
                    fn = self.operator_map[op]
                    val2 = val.eval(vars)
                    if not fn(val1, val2):
                        break
                    val1 = val2
                else:
                    return True
                return False

        operand.setParseAction(EvalConstant)
        self.arith_expr = operatorPrecedence(
            operand,
            [
                (self.operators['sign'], 1, opAssoc.RIGHT, EvalSignOp),
                (self.operators['multiply'], 2, opAssoc.LEFT, EvalMultiplicationOp),
                (self.operators['plus'], 2, opAssoc.LEFT, EvalAddOp),
                (self.operators['comparision'], 2, opAssoc.LEFT, EvalComparisonOp),
            ]
        )

    def eval(self, string):
        """Evaluate math in the string

        Parameters
        ----------
        string : str
            String to be evaluated

        Returns
        -------
        result : numeric
            Evaluation result
        """
        try:
            from pyparsing import ParseException

        except ImportError:
            message = '{name}: Unable to import pyparsing module. You can install it with `pip install pyparsing`.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ImportError(message)

        if not isinstance(string, str):
            # Bypass everything else than strings
            return string

        else:
            try:
                return int(string)

            except ValueError:
                try:
                    return float(string)

                except ValueError:
                    try:
                        ret = self.arith_expr.parseString(string, parseAll=True)[0]
                        result = ret.eval([])
                        return result

                    except ParseException:
                        # Bypass eval for strings which cannot be evaluated
                        return string

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            from dcase_util.utils import setup_logging
            setup_logging()

        return logger
