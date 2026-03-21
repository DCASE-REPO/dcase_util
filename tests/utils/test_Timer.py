""" Unit tests for Timer """

import pytest
import dcase_util
import time

def test_Timer():
    timer = dcase_util.utils.Timer()
    timer.start()
    time.sleep(0.1)
    elapsed = timer.elapsed()
    stop = timer.stop()
    assert elapsed == pytest.approx(0.1, abs=10 ** (-(1)))
    assert stop == pytest.approx(0.1, abs=10 ** (-(1)))
