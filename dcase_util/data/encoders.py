#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import numpy

from dcase_util.containers import BinaryMatrix2DContainer, DataMatrix2DContainer
from dcase_util.ui import FancyStringifier


class BinaryMatrixEncoder(BinaryMatrix2DContainer):
    """Binary matrix encoder base class"""
    def __init__(self, label_list=None, time_resolution=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        time_resolution : float
            Time resolution
            Default value None

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(BinaryMatrixEncoder, self).__init__(**kwargs)

        if not self.time_resolution:
            message = '{name}: No time resolution set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def __call__(self, *args, **kwargs):
        return self.encode(*args, **kwargs)


class OneHotEncoder(BinaryMatrixEncoder):
    """One hot encoder class"""
    def __init__(self, label_list=None, time_resolution=1.0, length_frames=1, length_seconds=None, allow_unknown_labels=False, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        time_resolution : float
            Time resolution
            Default value 1.0

        length_frames : int
            length of binary matrix in frames
            Default value 1

        length_seconds : float
            length of binary matrix in seconds
            Default value None

        allow_unknown_labels : bool
            Allow unknown labels in the decoding. If False, labels not in the given label_list will produce an error.
            Default value False

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(OneHotEncoder, self).__init__(**kwargs)

        self.length_frames = length_frames
        self.allow_unknown_labels = allow_unknown_labels

        if self.length_frames is None and length_seconds is not None:
            self.length_frames = self._length_to_frames(length_seconds)

        if not self.label_list:
            message = '{name}: No label_list set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(OneHotEncoder, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='data', value=self.data) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=indent + 2, field='Timing information') + '\n'
        output += ui.data(indent=indent + 4, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration', indent=indent) + '\n'
        output += ui.data(indent=indent + 4, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=indent + 4, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=indent + 2, field='Labels') + '\n'
        output += ui.data(indent=indent + 4, field='label_list', value=self.label_list) + '\n'

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
            Default value None

        length_seconds : float
            length of binary matrix in seconds, use either this or length_frames, if none set, one set in
            constructor is used.
            Default value None

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

        elif not self.allow_unknown_labels:
            # Unknown label given
            message = '{name}: Unknown label [{label}]'.format(name=self.__class__.__name__, label=label)
            self.logger.exception(message)
            raise ValueError(message)

        self.data = binary_matrix

        return self


class ManyHotEncoder(BinaryMatrixEncoder):
    """Many hot encoder class"""
    def __init__(self, label_list=None, time_resolution=None, length_frames=None, length_seconds=None, allow_unknown_labels=False, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        time_resolution : float
            Time resolution
            Default value None

        length_frames : int
            length of binary matrix
            Default value None

        length_seconds : float
            length of binary matrix in seconds
            Default value None

        allow_unknown_labels : bool
            Allow unknown labels in the decoding. If False, labels not in the given label_list will produce an error.
            Default value False

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(ManyHotEncoder, self).__init__(**kwargs)

        self.length_frames = length_frames
        self.allow_unknown_labels = allow_unknown_labels

        if self.length_frames is None and length_seconds is not None:
            self.length_frames = self._length_to_frames(length_seconds)

        if not self.label_list:
            message = '{name}: No label_list set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(ManyHotEncoder, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='data', value=self.data) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=indent + 2, field='Timing information') + '\n'
        output += ui.data(indent=indent + 4, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration', indent=indent) + '\n'
        output += ui.data(indent=indent + 4, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=indent + 4, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=indent + 2, field='Labels') + '\n'
        output += ui.data(indent=indent + 4, field='label_list', value=self.label_list) + '\n'

        return output

    def encode(self, label_list, length_frames=None, length_seconds=None):
        """Generate one hot binary matrix

        Parameters
        ----------
        label_list : list of str
            Class labels to be hot

        length_frames : int
            length of binary matrix
            Default value None

        length_seconds : float
            length of binary matrix in seconds
            Default value None

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

            elif not self.allow_unknown_labels:
                # Unknown label given
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
            Default value None

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.
            Default value None

        label : str
            Meta data field used to create event roll
            Default value 'event_label'

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution,
            'label': label
        })

        super(EventRollEncoder, self).__init__(**kwargs)

        self.label = label

        if not self.label_list:
            message = '{name}: No label_list set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(EventRollEncoder, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='data', value=self.data) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=indent + 2, field='Timing information') + '\n'
        output += ui.data(indent=indent + 4, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration', indent=indent) + '\n'
        output += ui.data(indent=indent + 4, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=indent + 4, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=indent + 2, field='Labels') + '\n'
        output += ui.data(indent=indent + 4, field='Label list', value=self.label_list) + '\n'
        output += ui.data(indent=indent + 4, field='label_field', value=self.label) + '\n'

        return output

    def encode(self, metadata_container, label=None, length_frames=None, length_seconds=None):
        """Generate event roll from MetaDataContainer

        Parameters
        ----------
        metadata_container : MetaDataContainer
            Meta data

        label : str
            Meta data field used to create event roll
            Default value None

        length_frames : int
            length of event roll
            Default value None

        length_seconds : int, optional
            length of event roll in seconds, if none given max offset of the meta data is used.
            Default value None

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


class LabelMatrixEncoder(DataMatrix2DContainer):
    """Label matrix encoder base class"""
    def __init__(self, label_list=None, time_resolution=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        time_resolution : float
            Time resolution
            Default value None

        """

        kwargs.update({
            'time_resolution': time_resolution
        })

        self.label_list = label_list

        super(LabelMatrixEncoder, self).__init__(**kwargs)

        if not self.time_resolution:
            message = '{name}: No time resolution set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def __call__(self, *args, **kwargs):
        return self.encode(*args, **kwargs)


class OneHotLabelEncoder(LabelMatrixEncoder):
    """One Hot label encoder class"""
    def __init__(self, label_list=None, time_resolution=1.0, length_frames=1, length_seconds=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        time_resolution : float
            Time resolution
            Default value 1.0

        length_frames : int
            length of binary matrix in frames
            Default value 1

        length_seconds : float
            length of binary matrix in seconds
            Default value None

        """

        kwargs.update({
            'label_list': label_list,
            'time_resolution': time_resolution
        })

        super(OneHotLabelEncoder, self).__init__(**kwargs)

        self.length_frames = length_frames

        if self.length_frames is None and length_seconds is not None:
            self.length_frames = self._length_to_frames(length_seconds)

        if not self.label_list:
            message = '{name}: No label_list set.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(OneHotLabelEncoder, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='data', value=self.data) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'

        output += ui.line(indent=indent + 2, field='Timing information') + '\n'
        output += ui.data(indent=indent + 4, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Duration', indent=indent) + '\n'
        output += ui.data(indent=indent + 4, field='Frames', value=self.length) + '\n'
        if self.time_resolution:
            output += ui.data(indent=indent + 4, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        output += ui.line(indent=indent + 2, field='Labels') + '\n'
        output += ui.data(indent=indent + 4, field='label_list', value=self.label_list) + '\n'

        return output

    def encode(self, label, length_frames=None, length_seconds=None):
        """Generate one hot label matrix

        Parameters
        ----------
        label : str
            Class label to be hot

        length_frames : int
            length of label matrix in frames, use either this or length_seconds, if none set, one set in
            constructor is used.
            Default value None

        length_seconds : float
            length of label matrix in seconds, use either this or length_frames, if none set, one set in
            constructor is used.
            Default value None

        Returns
        -------
        self

        """

        if length_frames is None and length_seconds is None:
            length_frames = self.length_frames

        elif length_seconds is not None:
            length_frames = self._length_to_frames(length_seconds)

        # Initialize binary matrix
        label_matrix = numpy.ndarray((1, length_frames), dtype=object)

        if label in self.label_list:
            label_matrix[0, :] = label

        else:
            # Unknown channel label given
            message = '{name}: Unknown label [{label}]'.format(name=self.__class__.__name__, label=label)
            self.logger.exception(message)
            raise ValueError(message)

        self.data = label_matrix

        return self

