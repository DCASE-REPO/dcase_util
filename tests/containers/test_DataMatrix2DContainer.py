""" Unit tests for DataMatrix2DContainer """

import nose.tools
import dcase_util
import tempfile
import os
import numpy


def test_container():
    # 1
    data_container = dcase_util.containers.DataMatrix2DContainer(
        data=numpy.random.rand(10, 100),
        time_resolution=0.02
    )
    nose.tools.eq_(data_container.shape, (10, 100))
    nose.tools.eq_(data_container.length, 100)
    nose.tools.eq_(data_container.frames, 100)
    nose.tools.eq_(data_container.vector_length, 10)

    data_container.focus_start = 20
    data_container.focus_stop = 40

    nose.tools.eq_(data_container.get_focused().shape, (10, 20))
    data_container.reset_focus()

    data_container.focus_start = 40
    data_container.focus_stop = 20

    nose.tools.eq_(data_container.get_focused().shape, (10, 20))
    data_container.reset_focus()

    nose.tools.eq_(data_container.get_focused().shape, (10, 100))

    data_container.reset_focus()
    data_container.set_focus(start=20, stop=40)
    nose.tools.eq_(data_container.get_focused().shape, (10, 20))

    data_container.reset_focus()
    data_container.set_focus(start_seconds=1, stop_seconds=2)
    nose.tools.eq_(data_container.get_focused().shape, (10, 50))

    data_container.reset_focus()
    data_container.set_focus(start_seconds=1, duration_seconds=1)
    nose.tools.eq_(data_container.get_focused().shape, (10, 50))

    data_container.reset_focus()
    data_container.set_focus(start=20, duration=20)
    nose.tools.eq_(data_container.get_focused().shape, (10, 20))

    data_container.freeze()
    nose.tools.eq_(data_container.shape, (10, 20))

    # 2
    data_container = dcase_util.containers.DataMatrix2DContainer(
        data=numpy.random.rand(10, 100),
        time_resolution=0.02
    )
    nose.tools.eq_(data_container.stats['mean'].shape, (10, ))
    nose.tools.eq_(data_container.stats['std'].shape, (10,))
    nose.tools.eq_(data_container.stats['n'], 100)

    nose.tools.eq_(data_container.get_frames(frame_ids=[0, 1, 2, 3]).shape, (10, 4))
    nose.tools.eq_(data_container.get_frames(frame_ids=[0, 1, 2, 3], vector_ids=[0, 1, 2]).shape, (3, 4))
    nose.tools.eq_(data_container.get_frames(frame_hop=2).shape, (10, 50))

    # 3
    data_container = dcase_util.containers.DataMatrix2DContainer(
        data=numpy.random.rand(10, 100),
        time_resolution=0.02
    )
    transposed = data_container.T
    nose.tools.eq_(transposed.shape, (100, 10))

    nose.tools.eq_(transposed.get_frames(frame_ids=[0, 1, 2, 3]).shape, (4, 10))
    nose.tools.eq_(transposed.get_frames(frame_ids=[0, 1, 2, 3], vector_ids=[0, 1, 2]).shape, (4, 3))
    nose.tools.eq_(transposed.get_frames(frame_hop=2).shape, (50, 10))

    data_container = dcase_util.containers.DataMatrix2DContainer(time_resolution=0.02)
    nose.tools.eq_(data_container.shape, (0, 0))
    nose.tools.eq_(data_container.length, 0)
    nose.tools.eq_(data_container.frames, 0)
    nose.tools.eq_(data_container.vector_length, 0)


def test_log():
    with dcase_util.utils.DisableLogger():
        data_container = dcase_util.containers.DataMatrix2DContainer(
            data=numpy.random.rand(10, 100),
            time_resolution=0.02
        )
        data_container.set_focus(start=20, stop=40)
        data_container.log()
