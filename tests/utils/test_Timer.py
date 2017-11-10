""" Unit tests for Timer """

import nose.tools
import dcase_util
import time


def test_Timer():
    timer = dcase_util.utils.Timer()
    timer.start()
    time.sleep(0.1)
    elapsed = timer.elapsed()
    stop = timer.stop()
    nose.tools.assert_almost_equal(elapsed, 0.1, 1)
    nose.tools.assert_almost_equal(stop, 0.1, 1)
