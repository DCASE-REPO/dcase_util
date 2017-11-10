""" Unit tests for EventRollEncoder """

import nose.tools
import numpy
import dcase_util

from dcase_util.containers import MetaDataContainer
from dcase_util.data import EventRollEncoder


def test_construction():
    minimal_event_list = [
        {'event_label': 'A', 'onset': 0, 'offset': 1, },
        {'event_label': 'A', 'onset': 5, 'offset': 15, },
        {'event_label': 'B', 'onset': 1, 'offset': 2, },
        {'event_label': 'B', 'onset': 4, 'offset': 5, },
        {'event_label': 'C', 'onset': 7, 'offset': 12, }
    ]
    meta = MetaDataContainer(minimal_event_list)

    target_event_roll = numpy.array([
        [1., 0., 0.],  # 0
        [0., 1., 0.],  # 1
        [0., 0., 0.],  # 2
        [0., 0., 0.],  # 3
        [0., 1., 0.],  # 4
        [1., 0., 0.],  # 5
        [1., 0., 0.],  # 6
        [1., 0., 1.],  # 7
        [1., 0., 1.],  # 8
        [1., 0., 1.],  # 9
        [1., 0., 1.],  # 10
        [1., 0., 1.],  # 11
        [1., 0., 0.],  # 12
        [1., 0., 0.],  # 13
        [1., 0., 0.],  # 14
    ]).T

    # Test #1
    event_roll = EventRollEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0,
        label='event_label'
    ).encode(metadata_container=meta)

    numpy.testing.assert_array_equal(target_event_roll, event_roll.data)
    nose.tools.assert_equal(event_roll.shape[0], target_event_roll.shape[0])
    nose.tools.assert_equal(event_roll.shape[1], target_event_roll.shape[1])


def test_pad():
    minimal_event_list = [
        {'event_label': 'A', 'onset': 0, 'offset': 1, },
        {'event_label': 'A', 'onset': 5, 'offset': 15, },
        {'event_label': 'B', 'onset': 1, 'offset': 2, },
        {'event_label': 'B', 'onset': 4, 'offset': 5, },
        {'event_label': 'C', 'onset': 7, 'offset': 12, }
    ]
    meta = MetaDataContainer(minimal_event_list)

    target_event_roll = numpy.array([
        [1., 0., 0.],  # 0
        [0., 1., 0.],  # 1
        [0., 0., 0.],  # 2
        [0., 0., 0.],  # 3
        [0., 1., 0.],  # 4
        [1., 0., 0.],  # 5
        [1., 0., 0.],  # 6
        [1., 0., 1.],  # 7
        [1., 0., 1.],  # 8
        [1., 0., 1.],  # 9
        [1., 0., 1.],  # 10
        [1., 0., 1.],  # 11
        [1., 0., 0.],  # 12
        [1., 0., 0.],  # 13
        [1., 0., 0.],  # 14
        [0., 0., 0.],  # 15
    ]).T

    # Test #1
    roller = EventRollEncoder(
        label_list=['A', 'B', 'C'],
        time_resolution=1.0
    )
    event_roll = roller.encode(
        metadata_container=meta,
        length_seconds=16
    )

    numpy.testing.assert_array_equal(target_event_roll, event_roll.data)
    nose.tools.assert_equal(event_roll.shape[0], target_event_roll.shape[0])
    nose.tools.assert_equal(event_roll.shape[1], target_event_roll.shape[1])

    padded_event_roll = roller.pad(length=18)
    nose.tools.assert_equal(padded_event_roll.length, 18)
    nose.tools.assert_equal(padded_event_roll.shape[1], event_roll.shape[1])

    padded_event_roll = roller.pad(length=10)
    nose.tools.assert_equal(padded_event_roll.length, 10)
    nose.tools.assert_equal(padded_event_roll.shape[1], event_roll.shape[1])


def test_log():
    with dcase_util.utils.DisableLogger():
        EventRollEncoder(
            label_list=['A', 'B', 'C'],
            time_resolution=1.0,
            filename='event_roller.cpickle'
        ).log()

