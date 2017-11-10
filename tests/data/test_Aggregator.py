""" Unit tests for Aggregator """

import nose.tools
import os
import numpy
import tempfile
import dcase_util

from dcase_util.containers import FeatureContainer
from dcase_util.data import Aggregator

data = numpy.array(
    [
        [0, 0],
        [1, 1],
        [2, 2],
        [3, 3],
        [4, 4],
        [5, 5],
        [6, 6],
        [7, 7],
        [8, 8],
        [9, 9],
        [10, 10],
    ]
).T


def test_aggregate_flatten():
    data_target = numpy.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [1, 1, 2, 2],
            [2, 2, 3, 3],
            [3, 3, 4, 4],
            [4, 4, 5, 5],
            [5, 5, 6, 6],
            [6, 6, 7, 7],
            [7, 7, 8, 8],
            [8, 8, 9, 9],
            [9, 9, 10, 10],
        ]
    ).T
    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['flatten']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_aggregate_mean():
    data_target = numpy.array(
        [
            [0,   0],
            [0.5, 0.5],
            [1.5, 1.5],
            [2.5, 2.5],
            [3.5, 3.5],
            [4.5, 4.5],
            [5.5, 5.5],
            [6.5, 6.5],
            [7.5, 7.5],
            [8.5, 8.5],
            [9.5, 9.5],
        ]
    ).T

    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['mean']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_aggregate_std():
    data_target = numpy.array(
        [
            [0.0, 0.0],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
        ]
    ).T

    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['std']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_aggregate_cov():
    data_target = numpy.array(
        [
            [0.0, 0.0, 0.0, 0.0],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
        ]
    ).T

    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['cov']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_aggregate_kurtosis():
    data_target = numpy.array(
        [
            [-3.0, -3.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
            [-2.0, -2.0],
        ]
    ).T

    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['kurtosis']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_aggregate_skew():
    data_target = numpy.array(
        [
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ]
    ).T

    container = FeatureContainer(
        data=data
    )

    agg = Aggregator(
        win_length_frames=2,
        hop_length_frames=1,
        recipe=['skew']
    )
    agg.aggregate(data=container)

    numpy.testing.assert_array_equal(data_target, container.data)


def test_save():
    data_target = numpy.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [1, 1, 2, 2],
            [2, 2, 3, 3],
            [3, 3, 4, 4],
            [4, 4, 5, 5],
            [5, 5, 6, 6],
            [6, 6, 7, 7],
            [7, 7, 8, 8],
            [8, 8, 9, 9],
            [9, 9, 10, 10],
        ]
    ).T
    container = FeatureContainer(
        data=data
    )

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir='/tmp', delete=False)
    try:
        agg = Aggregator(
            win_length_frames=2,
            hop_length_frames=1,
            recipe=['flatten']
        ).save(filename=tmp.name).load()
        agg.aggregate(data=container)

        numpy.testing.assert_array_equal(data_target, container.data)
    finally:
        os.unlink(tmp.name)


def test_log():
    with dcase_util.utils.DisableLogger():
        Aggregator(
            win_length_frames=2,
            hop_length_frames=1,
            recipe=['flatten'],
            filename='Aggregator.cpickle'
        ).log()

