""" Unit tests for BinaryMatrixEncoder """

import dcase_util

from dcase_util.data import BinaryMatrixEncoder


def test_log():
    with dcase_util.utils.DisableLogger():
        BinaryMatrixEncoder(
            label_list=['A', 'B', 'C'],
            time_resolution=1.0,
            filename='test.cpickle'
        ).log()
