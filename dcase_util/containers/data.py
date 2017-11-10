#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
from six import iteritems
import numpy
import copy
import os

from dcase_util.containers import ObjectContainer, RepositoryContainer
from dcase_util.ui import FancyStringifier
from dcase_util.utils import FileFormat, filelist_exists


class DataContainer(ObjectContainer):
    """Container class for data, inherited from ObjectContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional

        data : list, optional

        stats : dict, optional

        metadata : dict, optional

        time_resolution : float, optional

        processing_chain : ProcessingChain, optional

        """

        # Run ObjectContainer init
        ObjectContainer.__init__(self, **kwargs)

        # Run super init
        super(DataContainer, self).__init__(**kwargs)

        # Data
        self._data = None

        if data is None:
            data = numpy.ndarray((0, ))

        self.data = data

        # Stats
        if stats is None:
            stats = []

        self._stats = stats

        # Metadata
        if metadata is None:
            metadata = {}

        self.metadata = metadata

        # Matrix axis
        self.time_axis = 0

        # Timing
        self.time_resolution = time_resolution

        # Processing chain
        from dcase_util.processors import ProcessingChain
        if processing_chain is None:
            processing_chain = ProcessingChain()

        # Convert list to ProcessingChain
        if isinstance(processing_chain, list):
            processing_chain = ProcessingChain(processing_chain)
        self.processing_chain = processing_chain

        # Focus
        self._focus_start = None
        self._focus_stop = None

    def __getstate__(self):
        d = super(DataContainer, self).__getstate__()
        d.update({
            '_data': self._data,
            'time_axis': self.time_axis,
            'time_resolution': self.time_resolution,
            'metadata': self.metadata,
            'processing_chain': self.processing_chain,
            '_stats': self._stats,
            '_focus_start': self._focus_start,
            '_focus_stop': self._focus_stop
        })

        return d

    def __setstate__(self, d):
        super(DataContainer, self).__setstate__(d)

        self._data = d['_data']

        self.time_axis = d['time_axis']
        self.time_resolution = d['time_resolution']
        self.metadata = d['metadata']
        self.processing_chain = d['processing_chain']
        self._stats = d['_stats']

        self._focus_start = None
        self._focus_stop = None

        self.focus_start = d['_focus_start']
        self.focus_stop = d['_focus_stop']

    @property
    def data(self):
        """Data matrix

        Returns
        -------
        numpy.ndarray
            Data matrix

        """

        return self._data

    @data.setter
    def data(self, value):
        self._data = value

        # Reset stats
        self._stats = None

    @property
    def shape(self):
        """Shape of data matrix

        Returns
        -------
        tuple

        """

        if isinstance(self.data, numpy.ndarray):
            return self.data.shape

        else:
            return None

    @property
    def length(self):
        """Number of data columns

        Returns
        -------
        int

        """

        if isinstance(self.data, numpy.ndarray):
            return self.data.shape[self.time_axis]

        else:
            return 0

    @property
    def frames(self):
        """Number of data frames

        Returns
        -------
        int

        """

        return self.length

    def __str__(self):
        ui = FancyStringifier()

        output = super(DataContainer, self).__str__()

        output += ui.line(field='Data') + '\n'
        output += ui.data(indent=4, field='data', value=self.data) + '\n'

        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'

        output += ui.line(indent=4, field='Timing information') + '\n'
        output += ui.data(indent=6, field='time_resolution', value=self.time_resolution, unit="sec") + '\n'

        output += ui.line(field='Meta') + '\n'
        output += ui.data(indent=4, field='stats', value='Calculated' if self._stats is not None else '-') + '\n'
        output += ui.data(indent=4, field='metadata', value=self.metadata if self.metadata else '-') + '\n'
        output += ui.data(indent=4, field='processing_chain', value=self.processing_chain if self.processing_chain else '-') + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(indent=4, field='Frames', value=self.length) + '\n'

        if self.time_resolution:
            output += ui.data(indent=4, field='Seconds', value=self._frame_to_time(frame_id=self.length), unit='sec') + '\n'

        if self._focus_start is not None and self._focus_stop is not None:
            output += ui.line(field='Focus segment') + '\n'
            output += ui.line(indent=4, field='Duration') + '\n'
            output += ui.data(indent=6, field='Index', value=self._focus_stop - self._focus_start) + '\n'
            if self.time_resolution:
                output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(
                    frame_id=self._focus_stop - self._focus_start), unit='sec') + '\n'

            output += ui.line(indent=4, field='Start') + '\n'
            output += ui.data(indent=6, field='Index', value=self._focus_start) + '\n'
            if self.time_resolution:
                output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(frame_id=self._focus_start), unit='sec') + '\n'

            output += ui.line(indent=4, field='Stop') + '\n'
            output += ui.data(indent=6, field='Index', value=self._focus_stop) + '\n'
            if self.time_resolution:
                output += ui.data(indent=6, field='Seconds', value=self._frame_to_time(frame_id=self._focus_stop), unit='sec') + '\n'

        return output

    def __nonzero__(self):
        return self.length > 0

    def __len__(self):
        return self.length

    def push_processing_chain_item(self, processor_name, init_parameters=None, process_parameters=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict, optional
            Initialization parameters for the processors

        process_parameters : dict, optional
            Parameters for the process method of the Processor

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters
        )

        return self

    @property
    def focus_start(self):
        """Focus segment start

        Returns
        -------
        int

        """

        return self._focus_start

    @focus_start.setter
    def focus_start(self, value):
        if value is not None and value >= 0:
            self._focus_start = value

            if self._focus_stop is not None and self._focus_stop < self._focus_start:
                # focus points are reversed
                start = self._focus_start
                self._focus_start = self._focus_stop
                self._focus_stop = start

        else:
            # Keep focus start at zero
            self._focus_start = 0

    @property
    def focus_stop(self):
        """Focus segment stop

        Returns
        -------
        int

        """

        return self._focus_stop

    @focus_stop.setter
    def focus_stop(self, value):
        if value is not None and value < self.length:
            self._focus_stop = value

            if self._focus_start is not None and self._focus_stop < self._focus_start:
                # focus points are reversed
                start = self._focus_start
                self._focus_start = self._focus_stop
                self._focus_stop = start
        else:
            # Keep focus stop at the end
            self._focus_stop = self.length

    @property
    def stats(self):
        """Basic statistics of data matrix.

        Returns
        -------
        dict

        """

        if not self.empty():
            if not self._stats:
                self._stats = self._calculate_stats()

        return self._stats

    def _calculate_stats(self):
        """Calculate basic statistics of data matrix.

        Returns
        -------
        dict

        """

        return {
            'mean': numpy.mean(self.data, axis=self.time_axis),
            'std': numpy.std(self.data, axis=self.time_axis),
            'n': self.data.shape[self.time_axis],
            's1': numpy.sum(self.data, axis=self.time_axis),
            's2': numpy.sum(self.data ** 2, axis=self.time_axis),
        }

    def _time_to_frame(self, time, rounding_direction=None):
        """Time to frame index based on time resolution of the data matrix.

        Parameters
        ----------
        time : float
            Time stamp in seconds

        rounding_direction : str, optional
            Rounding direction, one of ['ceil', 'floor', None]

        Returns
        -------
        int

        """

        if rounding_direction is None:
            frame = int(time / float(self.time_resolution))

        elif rounding_direction == 'ceil':
            frame = int(numpy.ceil(time / float(self.time_resolution)))

        elif rounding_direction == 'floor':
            frame = int(numpy.floor(time / float(self.time_resolution)))

        # Handle negative index and index outside matrix
        if frame < 0:
            frame = 0

        elif frame > self.length:
            frame = self.length

        return frame

    def _frame_to_time(self, frame_id):
        """Frame index to time based on time resolution of the data matrix.

        Parameters
        ----------
        frame_id : int
            Frame index

        Returns
        -------
        float

        """

        return frame_id * self.time_resolution

    def set_focus(self,
                  start=None, stop=None, duration=None,
                  start_seconds=None, stop_seconds=None, duration_seconds=None):
        """Set focus segment

        Parameters
        ----------
        start : int, optional
            Frame index of focus segment start

        stop : int, optional
            Frame index of focus segment stop

        duration : int, optional
            Frame count of focus segment

        start_seconds : float, optional
            Time stamp (in seconds) of focus segment start, will be converted to frame index based on
            time resolution of the data matrix

        stop_seconds : float, optional
            Time stamp (in seconds) of focus segment stop, will be converted to frame index based on
            time resolution of the data matrix

        duration_seconds : float, optional
            Duration (in seconds) of focus segment, will be converted to frame index based on
            time resolution of the data matrix

        Returns
        -------
        self

        """

        if start is not None and stop is not None:
            # Set focus based start and stop given in index.
            self.focus_start = start
            self.focus_stop = stop

        elif start is not None and duration is not None:
            # Set focus based  start and duration given in index.
            self.focus_start = start
            self.focus_stop = start + duration

        elif start_seconds is not None and stop_seconds is not None:
            # Set focus based on start and stop given in seconds
            self.focus_start = self._time_to_frame(time=start_seconds)
            self.focus_stop = self._time_to_frame(time=stop_seconds)

        elif start_seconds is not None and duration_seconds is not None:
            # Set focus based on start and duration given in seconds
            self.focus_start = self._time_to_frame(time=start_seconds)
            self.focus_stop = self._time_to_frame(time=start_seconds + duration_seconds)

        else:
            # Focus segment not set, reset segment
            self._focus_start = None
            self._focus_stop = None

        return self

    def reset_focus(self):
        """Reset focus segment

        Returns
        -------
        self
        """

        self.set_focus()

        return self

    def get_focused(self):
        """Get focus segment from data array.

        Returns
        -------
        numpy.array

        """

        if self.focus_start is not None and self.focus_stop is not None:
            # Focus is set
            return self.data[self.focus_start:self.focus_stop]

        else:
            # Return all features
            return self.data

    def freeze(self):
        """Freeze focus segment, copy segment to be container's data.

        Returns
        -------
        self

        """

        self._data = self.get_focused()
        self.reset_focus()

        return self

    def get_frames(self, frame_ids=None, frame_hop=1, **kwargs):
        """Get frames from data array.

        Parameters
        ----------
        frame_ids : list of int, optional
            Frame ids of frames to be included.

        frame_hop : int, optional
            Frame hopping factor, with one every frame is included.

        Returns
        -------
        numpy.array

        """

        data = self.data

        # Apply frame_ids
        if frame_ids is not None:
            data = data[frame_ids]

        return data[::frame_hop]

    def plot(self):
        """Visualize data array.

        Returns
        -------
        self

        """

        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(self.get_focused())

        # Add filename to first subplot
        if self.filename:
            plt.title(self.filename)

        plt.tight_layout()
        plt.show()


class DataArrayContainer(DataContainer):
    """Array data container class, inherited from DataContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats
    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional

        data : list, optional

        stats : dict, optional

        metadata : dict, optional

        time_resolution : float

        processing_chain : ProcessingChain

        """

        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataContainer init
        DataContainer.__init__(self, **kwargs)

        # Run super init
        super(DataArrayContainer, self).__init__(**kwargs)


class DataMatrix2DContainer(DataContainer):
    """Two-dimensional data matrix container class, inherited from DataContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional

        data : list, optional

        stats : dict, optional

        metadata : dict, optional

        time_resolution : float

        processing_chain : ProcessingChain

        """
        if data is None:
            # Initialize with 2-matrix
            data = numpy.ndarray((0, 0))

        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataContainer init
        DataContainer.__init__(self, **kwargs)

        # Run super init
        super(DataMatrix2DContainer, self).__init__(**kwargs)

        # Matrix axis
        self.data_axis = 0
        self.time_axis = 1

    def __getstate__(self):
        d = super(DataMatrix2DContainer, self).__getstate__()
        d.update({
            'data_axis': self.data_axis,
            'time_axis': self.time_axis,
        })

        return d

    def __setstate__(self, d):
        super(DataMatrix2DContainer, self).__setstate__(d)
        self.data_axis = d['data_axis']
        self.time_axis = d['time_axis']

    def __str__(self):
        ui = FancyStringifier()

        output = super(DataMatrix2DContainer, self).__str__()

        output += ui.line(field='Data') + '\n'

        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=6, field='data_axis', value=self.data_axis) + '\n'

        return output

    @property
    def vector_length(self):
        """Data vector length

        Returns
        -------
            int

        """

        if isinstance(self.data, numpy.ndarray):
            return self.data.shape[self.data_axis]

        else:
            return 0

    @property
    def T(self):
        """Transposed data in a data container

        Returns
        -------
        DataMatrix2DContainer

        """

        transposed = copy.deepcopy(self)
        transposed.data = self.data.T

        # Flip axis
        transposed.time_axis = self.data_axis
        transposed.data_axis = self.time_axis

        return transposed

    def get_focused(self):
        """Get focus segment from data matrix.

        Returns
        -------
        numpy.ndarray

        """

        if self.focus_start is not None and self.focus_stop is not None:
            # Focus is set
            if self.time_axis == 1:
                return self.data[:, self.focus_start:self.focus_stop]

            else:
                return self.data[self.focus_start:self.focus_stop, :]

        else:
            # Return all features
            return self.data

    def get_frames(self, frame_ids=None, vector_ids=None, frame_hop=1):
        """Get frames from data matrix.

        Parameters
        ----------
        frame_ids : list of int, optional
            Frame ids of frames to be included.

        vector_ids : list of int, optional
            Data ids of frame's data vector to be included.

        frame_hop : int, optional
            Frame hopping factor, with one every frame is included.

        Returns
        -------
        numpy.ndarray

        """

        data = self.data
        if self.time_axis == 1:
            # Apply frame_ids
            if frame_ids is not None:
                data = data[:, frame_ids]

            # Apply vector_ids
            if vector_ids is not None:
                data = data[vector_ids, :]

            # Apply the frame hop
            if len(data.shape) > 1:
                return data[:, ::frame_hop]

            else:
                return data[::frame_hop]

        else:
            # Apply frame_ids
            if frame_ids is not None:
                data = data[frame_ids, :]

            # Apply vector_ids
            if vector_ids is not None:
                data = data[:, vector_ids]

            if len(data.shape) > 1:
                return data[::frame_hop, :]

            else:
                return data[::frame_hop]

    def plot(self):
        """Visualize data matrix.

        Returns
        -------
        self

        """

        from librosa.display import specshow
        import matplotlib.pyplot as plt
        plt.figure()

        data = self.get_focused()
        if self.time_axis == 0:
            # Make sure time is on x-axis
            data = data.T

        # Plot feature matrix
        if self.time_resolution:
            sr = int(1.0 / float(self.time_resolution))
            x_axis = 'time'
        else:
            sr = 1.0
            x_axis = None

        specshow(
            data,
            x_axis=x_axis,
            sr=sr,
            hop_length=1
        )

        # Add color bar
        plt.colorbar()

        # Add filename to first subplot
        if self.filename:
            plt.title(self.filename)

        plt.tight_layout()
        plt.show()


class DataMatrix3DContainer(DataMatrix2DContainer):
    """Three-dimensional data matrix container class, inherited from DataMatrix2DContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional

        data : list, optional

        stats : dict, optional

        metadata : dict, optional

        time_resolution : float, optional

        processing_chain : ProcessingChain, optional

        """

        if data is None:
            data = numpy.ndarray((0, 0, 0))

        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataMatrix2DContainer init
        DataMatrix2DContainer.__init__(self, **kwargs)

        # Run super init
        super(DataMatrix3DContainer, self).__init__(**kwargs)

        # Matrix axis
        self.data_axis = 0
        self.time_axis = 1
        self.sequence_axis = 2

    def __str__(self):
        ui = FancyStringifier()

        output = super(DataMatrix2DContainer, self).__str__()

        output += ui.line(field='Data') + '\n'
        output += ui.line(indent=4, field='Dimensions') + '\n'
        output += ui.data(indent=6, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=6, field='data_axis', value=self.data_axis) + '\n'
        output += ui.data(indent=6, field='sequence_axis', value=self.sequence_axis) + '\n'

        return output

    def plot(self):
        # TODO
        message = '{name}: plot-method not yet implemented.'.format(
            name=self.__class__.__name__
        )
        self.logger.exception(message)
        raise AssertionError(message)


class BinaryMatrix2DContainer(DataMatrix2DContainer):
    """Two-dimensional data matrix container class, inherited from DataContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, time_resolution=None, label_list=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional

        data : list, optional

        stats : dict, optional

        metadata : dict, optional

        time_resolution : float

        processing_chain : ProcessingChain

        """

        kwargs.update({
            'data': data,
            'time_resolution': time_resolution,
            'label_list': label_list,
            'processing_chain': processing_chain
        })

        # Run DataMatrix2DContainer init
        DataMatrix2DContainer.__init__(self, **kwargs)

        # Run super init
        super(BinaryMatrix2DContainer, self).__init__(**kwargs)

        self.label_list = label_list

    def __getstate__(self):
        d = super(BinaryMatrix2DContainer, self).__getstate__()
        d.update({
            'label_list': self.label_list
        })

        return d

    def __setstate__(self, d):
        super(BinaryMatrix2DContainer, self).__setstate__(d)

        self.label_list = d['label_list']

    def __str__(self):
        ui = FancyStringifier()

        output = super(BinaryMatrix2DContainer, self).__str__()

        output += ui.line(field='Labels') + '\n'
        output += ui.data(indent=4, field='label_list', value=self.label_list) + '\n'

        return output

    def pad(self, length, binary_matrix=None):
        """Pad binary matrix along time axis

        Parameters
        ----------
        length : int
            Length to be padded

        binary_matrix : np.ndarray, shape=(time steps, amount of classes)
            Binary matrix

        Returns
        -------
        np.ndarray [shape=(number of classes,t)]
            Padded binary matrix

        """

        if binary_matrix is None:
            binary_matrix = self.data

        if length > binary_matrix.shape[self.time_axis]:
            if self.time_axis == 0:
                padding = numpy.zeros((length - binary_matrix.shape[0], binary_matrix.shape[1]))
                self.data = numpy.vstack((binary_matrix, padding))

            else:
                padding = numpy.zeros((binary_matrix.shape[0], length - binary_matrix.shape[1]))
                self.data = numpy.hstack((binary_matrix, padding))

        elif length < binary_matrix.shape[self.time_axis]:
            if self.time_axis == 0:
                self.data = binary_matrix[0:length, :]
            else:
                self.data = binary_matrix[:, 0:length]

        return self

    def plot(self, binary_matrix=None, data_container=None):
        """Visualize binary matrix, and optionally synced data matrix.

        For example, this can be used to visualize sound event activity along with the acoustic features.

        Parameters
        ----------
        binary_matrix : numpy.ndarray
            Binary matrix, if None given internal data used.

        data_container : DataContainer
            Extra data matrix to be shown along with binary matrix.
             
        Returns
        -------
        None

        """

        import matplotlib.pyplot as plt
        import librosa
        from librosa.display import specshow

        if binary_matrix is None:
            binary_matrix = self.data

        if self.time_axis == 0:
            binary_matrix = binary_matrix.T

        if binary_matrix is not None and data_container is not None:
            plt.subplots(2, 1)

            # Features
            ax1 = plt.subplot(2, 1, 1)
            ax1.yaxis.set_label_position("right")
            specshow(binary_matrix,
                     x_axis='time',
                     sr=int(1 / float(self.time_resolution)),
                     hop_length=1,
                     cmap=plt.cm.gray_r
                     )
            y_ticks = numpy.arange(0, len(self.label_list)) + 0.5
            ax1.set_yticks(y_ticks)
            ax1.set_yticklabels(self.label_list)

            plt.ylabel('Binary matrix')

            # Binary matrix
            ax2 = plt.subplot(2, 1, 2)
            ax2.yaxis.set_label_position("right")
            specshow(data_container.data,
                     x_axis='time',
                     sr=int(1 / float(data_container.hop_length_seconds)),
                     hop_length=1
                     )
            plt.ylabel('Data')

        elif binary_matrix is not None and data_container is None:
            plt.subplots(1, 1)
            ax = plt.subplot(1, 1, 1)
            # Binary matrix
            ax.yaxis.set_label_position("right")
            specshow(binary_matrix,
                     x_axis='time',
                     sr=int(1 / float(self.time_resolution)),
                     hop_length=1,
                     cmap=plt.cm.gray_r
                     )
            y_ticks = numpy.arange(0, len(self.label_list)) + 0.5
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(self.label_list)

        plt.show()

    def _length_to_frames(self, time):
        return int(numpy.ceil(time * 1.0 / self.time_resolution))

    def _onset_to_frames(self, onset):
        return int(numpy.floor(onset * 1.0 / self.time_resolution))

    def _offset_to_frames(self, offset):
        return int(numpy.ceil(offset * 1.0 / self.time_resolution))


class DataRepository(RepositoryContainer):
    """Data repository container class to store multiple DataContainers together.

    Containers are stored in a dict, label is used as dictionary key and value is associated data container.

    """

    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, filename_dict=None, default_stream_id=0, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename_dict: dict
            Dict of file paths, feature extraction method label as key, and filename as value.
            If given, repository is loaded in the initialization stage.

        default_stream_id : str or int

        processing_chain : ProcessingChain

        """

        super(DataRepository, self).__init__(**kwargs)

        self.filename_dict = filename_dict
        self.default_stream_id = default_stream_id

        from dcase_util.processors import ProcessingChain
        if processing_chain is None:
            processing_chain = ProcessingChain()

        self.processing_chain = processing_chain

        self.item_class = DataMatrix2DContainer

        if data is not None and isinstance(data, dict):
            dict.update(self, data)

    def __str__(self):
        ui = FancyStringifier()

        output = ''
        output += ui.class_name(self.__class__.__name__) + '\n'

        if self.filename_dict:
            output += FancyStringifier().data(field='filename_dict', value=self.filename_dict) + '\n'

        output += ui.line(field='Repository info') + '\n'
        output += ui.data(indent=4, field='Item class', value=self.item_class.__name__) + '\n'
        output += ui.data(indent=4, field='Item count', value=len(self)) + '\n'
        output += ui.data(indent=4, field='Labels', value=list(self.keys())) + '\n'

        output += ui.line(field='Content') + '\n'
        for label, label_data in iteritems(self):
            print(label_data)
            if label_data:
                for stream_id, stream_data in iteritems(label_data):
                    output += ui.data(indent=4, field='['+str(label)+']' + '[' + str(stream_id) + ']', value=stream_data) + '\n'

        output += '\n'

        return output

    @property
    def labels(self):
        """Item labels stores in the repository.

        Returns
        -------
        list of str
        
        """
        
        return sorted(list(self.keys()))

    def stream_ids(self, label):
        """Stream ids stores for the label in the repository.

        Parameters
        ----------
        label : str
            Item label

        Returns
        -------
        list of str

        """

        if label in self:
            return sorted(list(self[label].keys()))
        else:
            return None

    def load(self, filename_dict=None):
        """Load file list

        Parameters
        ----------
        filename_dict : dict
            Dict of file paths, label as key, and filename as value or two-level dictionary label as key,
            stream as key and filename as value.

        Returns
        -------
        self

        """

        if filename_dict is not None:
            self.filename_dict = filename_dict

        if self.filename_dict is not None:
            if filelist_exists(self.filename_dict):
                dict.clear(self)
                sorted(self.filename_dict)

                for label, data in iteritems(self.filename_dict):
                    self[label] = {}
                    if not label.startswith('_'):
                        # Skip labels starting with '_', those are just for extra info
                        if isinstance(data, str):
                            # filename given directly, only one feature stream per method inputted.
                            self[label][self.default_stream_id] = self.item_class().load(filename=data)

                        elif isinstance(data, dict):
                            for stream, filename in iteritems(data):
                                self[label][stream] = self.item_class().load(filename=filename)

                return self

            else:
                # All filenames did not exists, find which ones is missing and raise error.
                for label, data in iteritems(self.filename_dict):
                    if isinstance(data, str) and not os.path.isfile(data):
                        message = '{name}: Repository cannot be loaded, file does not exists for method [{method}], file [{filename}]'.format(
                            name=self.__class__.__name__,
                            method=label,
                            filename=data
                        )
                        self.logger.exception(message)
                        raise IOError(message)

                    elif isinstance(data, dict):
                        for stream, filename in iteritems(data):
                            if not os.path.isfile(filename):
                                message = '{name}: Repository cannot be loaded, file does not exists for method [{method}], stream [{stream}], file [{filename}]'.format(
                                    name=self.__class__.__name__,
                                    method=label,
                                    stream=stream,
                                    filename=filename
                                )
                                self.logger.exception(message)
                                raise IOError(message)

        else:
            message = '{name}: Repository cannot be loaded, no filename_dict set.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise IOError(message)

    def get_container(self, label, stream_id=None):
        """Get container from repository

        Parameters
        ----------
        label : str
            Label

        stream_id : str or int
            Stream id, if None, default_stream is used.

        Returns
        -------
        DataContainer

        """

        if stream_id is None:
            stream_id = self.default_stream_id

        return self.get(label).get(stream_id)

    def set_container(self, container, label, stream_id=None):
        """Store container to repository

        Parameters
        ----------
        container : DataContainer or dict or list
            Data container

        label : str
            Label assigned to the container

        stream_id : str or int
            Stream id, if None, default_stream is used.

        Returns
        -------
        self

        """

        if stream_id is None:
            stream_id = self.default_stream_id

        if label not in self:
            self[label] = {}

        self[label][stream_id] = container

        return self

    def push_processing_chain_item(self, processor_name, init_parameters=None, process_parameters=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict
            Initialization parameters for the processors

        process_parameters : dict
            Parameters for the process method of the Processor

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters
        )

        return self

    def plot(self):
        """Visualize data stored in the repository.

        Returns
        -------
        None

        """
        
        from librosa.display import specshow
        import matplotlib.pyplot as plt

        rows = len(list(self.keys()))

        labels = list(self.keys())
        labels.sort()

        plt.subplots(rows, 1)
        for label_id, label in enumerate(self.labels):
            for stream_id in self.stream_ids(label):
                plt.subplot(rows, 1, label_id+1)
                current_container = self.get_container(label=label, stream_id=stream_id)
                # Plot feature matrix
                specshow(current_container.data,
                         x_axis='time',
                         sr=int(1 / float(current_container.time_resolution)),
                         hop_length=1
                         )

                plt.ylabel('['+str(label)+']['+str(stream_id)+']')

        plt.show()
