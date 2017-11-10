#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import numpy

from dcase_util.containers import BinaryMatrix2DContainer
from dcase_util.ui import FancyStringifier


class BinaryMatrixEncoder(BinaryMatrix2DContainer):
    """Binary matrix encoder base class"""
    def __init__(self, label_list=None, time_resolution=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list

        time_resolution : float
            Time resolution

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(BinaryMatrixEncoder, self).__init__(**kwargs)


class OneHotEncoder(BinaryMatrixEncoder):
    """One hot encoder class"""
    def __init__(self, label_list=None, time_resolution=None, length_frames=None, length_seconds=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list

        time_resolution : float
            Time resolution

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(OneHotEncoder, self).__init__(**kwargs)

        self.length_frames = length_frames

        if self.length_frames is None and length_seconds is not None:
            self.length_frames = self._length_to_frames(length_seconds)

    def __str__(self):
        ui = FancyStringifier()

        output = super(OneHotEncoder, self).__str__()

        output += ui.line(field='Data') + '\n'
        output += ui.data(indent=4, field='data', value=self.data) + '\n'

        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=6, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=4, field='Timing information') + '\n'
        output += ui.data(indent=6, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(indent=6, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=4, field='Labels') + '\n'
        output += ui.data(indent=6, field='label_list', value=self.label_list) + '\n'

        return output

    def encode(self, label, length_frames=None, length_seconds=None):
        """Generate one hot binary matrix

        Parameters
        ----------
        label : str
            Class label to be hot

        length_frames : int
            length of binary matrix in frames, use either this or length_seconds, if none set, one set in
            constructor is used.

        length_seconds : float
            length of binary matrix in seconds, use either this or length_frames, if none set, one set in
            constructor is used.

        Returns
        -------
        self

        """

        if length_frames is None and length_seconds is None:
            length_frames = self.length_frames

        elif length_seconds is not None:
            length_frames = self._length_to_frames(length_seconds)

        # Initialize binary matrix
        binary_matrix = numpy.zeros((len(self.label_list), length_frames))

        # Find correct row
        if label in self.label_list:
            pos = self.label_list.index(label)

            # Mark row to be hot
            binary_matrix[pos, :] = 1

        else:
            # Unknown channel label given
            message = '{name}: Unknown label [{label}]'.format(name=self.__class__.__name__, label=label)
            self.logger.exception(message)
            raise ValueError(message)

        self.data = binary_matrix

        return self


class ManyHotEncoder(BinaryMatrixEncoder):
    """Many hot encoder class"""
    def __init__(self, label_list=None, time_resolution=None, length_frames=None, length_seconds=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list

        time_resolution : float
            Time resolution

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(ManyHotEncoder, self).__init__(**kwargs)

        self.length_frames = length_frames

        if self.length_frames is None and length_seconds is not None:
            self.length_frames = self._length_to_frames(length_seconds)

    def __str__(self):
        ui = FancyStringifier()

        output = super(ManyHotEncoder, self).__str__()

        output += ui.line(field='Data') + '\n'
        output += ui.data(indent=4, field='data', value=self.data) + '\n'

        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=6, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=4, field='Timing information') + '\n'
        output += ui.data(indent=6, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(indent=6, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=4, field='Labels') + '\n'
        output += ui.data(indent=6, field='label_list', value=self.label_list) + '\n'

        return output

    def encode(self, label_list, length_frames=None, length_seconds=None):
        """Generate one hot binary matrix

        Parameters
        ----------
        label_list : list of str
            Class labels to be hot

        length_frames : int
            length of binary matrix

        length_seconds : float
            length of binary matrix in seconds

        Returns
        -------
        self

        """

        if length_frames is None and length_seconds is None:
            length_frames = self.length_frames

        elif length_seconds is not None:
            length_frames = self._length_to_frames(length_seconds)

        # Initialize binary matrix
        binary_matrix = numpy.zeros((len(self.label_list), length_frames))

        for label in label_list:
            if label in self.label_list:
                # Find correct row
                pos = self.label_list.index(label)

                # Mark row to be hot
                binary_matrix[pos, :] = 1

            else:
                # Unknown channel label given
                message = '{name}: Unknown label [{label}]'.format(name=self.__class__.__name__, label=label)
                self.logger.exception(message)
                raise ValueError(message)

        self.data = binary_matrix

        return self


class EventRollEncoder(BinaryMatrixEncoder):
    """Event list encoder class"""
    def __init__(self, label_list=None, time_resolution=None, label='event_label', **kwargs):
        """Event roll

        Event roll is binary matrix indicating event activity withing time segment defined by time_resolution.

        Parameters
        ----------
        label_list : list
            List of labels in correct order

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.

        label : str
            Meta data field used to create event roll

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution,
            'label': label
        })

        super(EventRollEncoder, self).__init__(**kwargs)

        self.label = label

    def __str__(self):
        ui = FancyStringifier()

        output = super(EventRollEncoder, self).__str__()

        output += ui.line(field='Data') + '\n'
        output += ui.data(indent=4, field='data', value=self.data) + '\n'

        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=6, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=4, field='Timing information') + '\n'
        output += ui.data(indent=6, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(indent=6, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=4, field='Labels') + '\n'
        output += ui.data(indent=6, field='Label list', value=self.label_list) + '\n'
        output += ui.data(indent=6, field='label_field', value=self.label) + '\n'

        return output

    def encode(self, metadata_container, label=None, length_frames=None, length_seconds=None):
        """Generate event roll from MetaDataContainer

        Parameters
        ----------
        metadata_container : MetaDataContainer
            Meta data

        label : str
            Meta data field used to create event roll

        length_frames : int
            length of event roll

        length_seconds : int, optional
            length of event roll in seconds, if none given max offset of the meta data is used.


        Returns
        -------
        self

        """

        if label is None:
            label = self.label

        if length_frames is None:
            if length_seconds is None:
                max_offset_seconds = metadata_container.max_offset
            else:
                max_offset_seconds = length_seconds

            max_offset_frames = self._length_to_frames(max_offset_seconds)

        else:
            max_offset_frames = length_frames

        # Initialize event roll
        event_roll = numpy.zeros((len(self.label_list), max_offset_frames))

        # Fill-in event_roll
        for item in metadata_container:
            if item.onset is not None and item.offset is not None:
                if item[label]:
                    pos = self.label_list.index(item[label])
                    onset = self._onset_to_frames(item.onset)
                    offset = self._offset_to_frames(item.offset)

                    if offset > event_roll.shape[self.time_axis]:
                        # we have event which continues beyond max_offset_value
                        offset = event_roll.shape[self.time_axis]

                    if onset <= event_roll.shape[self.time_axis]:
                        # We have event inside the event roll
                        event_roll[pos, onset:offset] = 1

        self.data = event_roll
        return self
