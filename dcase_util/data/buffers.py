#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import collections
from dcase_util.containers import ObjectContainer
from dcase_util.ui import FancyStringifier


class DataBuffer(ObjectContainer):
    """Data buffer (First in, first out)

    Buffer can store data and meta data associated to it.

    """

    def __init__(self, size=10, **kwargs):
        """__init__ method.

        Parameters
        ----------
        size : int
            Number of item to store in the buffer
            Default value 10

        """

        super(DataBuffer, self).__init__(**kwargs)

        self.size = size

        self.index = collections.deque(maxlen=self.size)
        self.data_buffer = collections.deque(maxlen=self.size)
        self.meta_buffer = collections.deque(maxlen=self.size)

    def __str__(self):
        ui = FancyStringifier()

        output = super(DataBuffer, self).__str__()

        output += ui.data(field='size', value=self.size) + '\n'
        output += ui.data(field='index', value=self.index) + '\n'
        output += ui.line(field='Buffer') + '\n'
        output += ui.data(indent=4, field='data_buffer', value=self.data_buffer) + '\n'
        output += ui.data(indent=4, field='meta_buffer', value=self.meta_buffer) + '\n'

        return output

    @property
    def count(self):
        """Buffer usage

        Returns
        -------
        buffer length: int

        """

        return len(self.index)

    @property
    def full(self):
        """Buffer full

        Returns
        -------
        bool

        """

        if self.count == self.size:
            return True
        else:
            return False

    def key_exists(self, key):
        """Check that key exists in the buffer

        Parameters
        ----------
        key : str or number
            Key value

        Returns
        -------
        bool

        """

        if key in self.index:
            return True
        else:
            return False

    def set(self, key, data=None, meta=None):
        """Insert item to the buffer

        Parameters
        ----------
        key : str or number
            Key value

        data :
            Item data

        meta :
            Item meta

        Returns
        -------
        DataBuffer object

        """

        if not self.key_exists(key):
            self.index.append(key)
            self.data_buffer.append(data)
            self.meta_buffer.append(meta)

        return self

    def get(self, key):
        """Get item based on key

        Parameters
        ----------
        key : str or number
            Key value

        Returns
        -------
        data : (data, meta)

        """

        if self.key_exists(key):
            index = list(self.index).index(key)
            return self.data_buffer[index], self.meta_buffer[index]
        else:
            return None, None

    def clear(self):
        """Empty the buffer
        """

        self.index.clear()
        self.data_buffer.clear()
        self.meta_buffer.clear()
