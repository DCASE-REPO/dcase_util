""" Unit tests for OneHotEncoder """

import nose.tools
import numpy
import dcase_util

from dcase_util.containers import MetaDataContainer
from dcase_util.data import ManyHotEncoder


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
    binary_matrix = ManyHotEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0
    ).encode(
        label_list=['A'],
        length_seconds=3,
    )

    numpy.testing.assert_array_equal(target_binary_matrix, binary_matrix.data)
    nose.tools.assert_equal(binary_matrix.shape[0], target_binary_matrix.shape[0])
    nose.tools.assert_equal(binary_matrix.shape[1], target_binary_matrix.shape[1])

    target_binary_matrix = numpy.array([
        [0., 1., 0.],  # 0
        [0., 1., 0.],  # 1
        [0., 1., 0.],  # 2
    ]).T

    # Test #1
    binary_matrix = ManyHotEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0
    ).encode(
        label_list=['B'],
        length_seconds=3,
    )

    numpy.testing.assert_array_equal(target_binary_matrix, binary_matrix.data)
    nose.tools.assert_equal(binary_matrix.shape[0], target_binary_matrix.shape[0])
    nose.tools.assert_equal(binary_matrix.shape[1], target_binary_matrix.shape[1])


def test_log():
    with dcase_util.utils.DisableLogger():
        ManyHotEncoder(
            label_list=['A', 'B', 'C'],
            time_resolution=1.0,
            filename='test.cpickle'
        ).log()


@nose.tools.raises(ValueError)
def test_unknown_label():
    with dcase_util.utils.DisableLogger():
        ManyHotEncoder(
            label_list=['A', 'B', 'C'],
            time_resolution=1.0,
            filename='test.cpickle'
        ).encode(
            label_list=['BB'],
            length_seconds=3,
        )
