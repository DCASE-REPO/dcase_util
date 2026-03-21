""" Unit tests for OneHotEncoder """

import pytest
import numpy
import dcase_util

from dcase_util.containers import MetaDataContainer
from dcase_util.data import OneHotEncoder

def test_construction():
    minimal_event_list = [
        {'scene_label': 'A'},
        {'scene_label': 'A'},
        {'scene_label': 'B'},
        {'scene_label': 'B'},
        {'scene_label': 'C'}
    ]
    meta = MetaDataContainer(minimal_event_list)

    target_binary_matrix = numpy.array([
        [1., 0., 0.],  # 0
        [1., 0., 0.],  # 1
        [1., 0., 0.],  # 2
    ]).T

    # Test #1
    binary_matrix = OneHotEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0
    ).encode(
        label='A',
        length_seconds=3,
    )

    numpy.testing.assert_array_equal(target_binary_matrix, binary_matrix.data)
    assert binary_matrix.shape[0] == target_binary_matrix.shape[0]
    assert binary_matrix.shape[1] == target_binary_matrix.shape[1]

    target_binary_matrix = numpy.array([
        [0., 1., 0.],  # 0
        [0., 1., 0.],  # 1
        [0., 1., 0.],  # 2
    ]).T

    # Test #1
    binary_matrix = OneHotEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0
    ).encode(
        label='B',
        length_seconds=3,
    )

    numpy.testing.assert_array_equal(target_binary_matrix, binary_matrix.data)
    assert binary_matrix.shape[0] == target_binary_matrix.shape[0]
    assert binary_matrix.shape[1] == target_binary_matrix.shape[1]

def test_log():
    with dcase_util.utils.DisableLogger():
        OneHotEncoder(
            label_list=['A', 'B', 'C'],
            time_resolution=1.0,
            filename='test.cpickle'
        ).log()

def test_unknown_label():
    with pytest.raises(ValueError):
        with dcase_util.utils.DisableLogger():
            OneHotEncoder(
                label_list=['A', 'B', 'C'],
                time_resolution=1.0,
                filename='test.cpickle'
            ).encode(
                label='BB',
                length_seconds=3,
            )
