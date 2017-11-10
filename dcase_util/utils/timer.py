#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import datetime
import time


class Timer(object):
    """Timer class"""

    def __init__(self):
        # Initialize internal properties
        self._start = None
        self._elapsed = None

    def start(self):
        """Start timer

        Returns
        -------
        self
        """

        self._elapsed = None
        self._start = time.time()
        return self

    def stop(self):
        """Stop timer

        Returns
        -------
        self
        """

        self._elapsed = (time.time() - self._start)
        return self._elapsed

    def elapsed(self):
        """Return elapsed time in seconds since timer was started

        Can be used without stopping the timer

        Returns
        -------
        float
            Seconds since timer was started
        """

        return time.time() - self._start

    def get_string(self, elapsed=None):
        """Get elapsed time in a string format

        Parameters
        ----------
        elapsed : float
            Elapsed time in seconds
            Default value "None"

        Returns
        -------
        str
            Time delta between start and stop
        """

        if elapsed is None:
            elapsed = (time.time() - self._start)

        return str(datetime.timedelta(seconds=elapsed))

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()
