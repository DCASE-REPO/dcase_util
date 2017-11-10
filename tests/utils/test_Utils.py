""" Unit tests for Utils """

import nose.tools
import dcase_util
from dcase_util.utils import get_parameter_hash, SimpleMathStringEvaluator


def test_get_parameter_hash():
    data = {
        'field1': {
            '1': [1, 2, 3],
            '2': 1234,
        },
        'field2': {
            'sub_field1': 1234
        }
    }
    data_hash_target = '064e6628408f570b9b5904f0af5228f5'

    nose.tools.eq_(get_parameter_hash(data), data_hash_target)

    data = {
        'field2': {
            'sub_field1': 1234
        },
        'field1': {
            '2': 1234,
            '1': [1, 2, 3],
        }
    }
    nose.tools.eq_(get_parameter_hash(data), data_hash_target)


def test_math_string_evaluator():
    data = [
        {
            'input': '2+2',
            'result': 4,
        },
        {
            'input': '10-2',
            'result': 8,
        },
        {
            'input': '2*3',
            'result': 6,
        },
        {
            'input': '10/5',
            'result': 2,
        },
        {
            'input': '8.0/5.0',
            'result': 1.6,
        },
        {
            'input': '5 > 3',
            'result': True,
        },
        {
            'input': '5 < 3',
            'result': False,
        },
        {
            'input': '5 <= 5',
            'result': True,
        }
    ]

    math_eval = SimpleMathStringEvaluator()

    for test_case in data:
        res = math_eval.eval(test_case['input'])
        nose.tools.eq_(res, test_case['result'])


def test_is_float():
    nose.tools.eq_(dcase_util.utils.is_float(10.0), True)
    nose.tools.eq_(dcase_util.utils.is_float(-2.0112121), True)
    nose.tools.eq_(dcase_util.utils.is_float(120), True)
    nose.tools.eq_(dcase_util.utils.is_float('str'), False)


def test_is_int():
    nose.tools.eq_(dcase_util.utils.is_float(10), True)
    nose.tools.eq_(dcase_util.utils.is_float(-21), True)
    nose.tools.eq_(dcase_util.utils.is_float(120.121), True)
    nose.tools.eq_(dcase_util.utils.is_float('str'), False)

