#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
from six import iteritems
import numpy
import copy
import os
import glob
from past.builtins import basestring

from dcase_util.containers import ObjectContainer, RepositoryContainer, OneToOneMappingContainer
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
            File path
            Default value None

        data : numpy.ndarray, optional
            Data to initialize the container
            Default value None

        stats : dict, optional
            Statistics of the data
            Default value None

        metadata : dict or MetadataContainer, optional
            MetadataContainer
            Default value None

        time_resolution : float, optional
            Time resolution
            Default value None

        processing_chain : ProcessingChain, optional
            Processing chain.
            Default value None

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

        else:
            message = '{name}: Wrong type of processing_chain given to class initializer.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ValueError(message)

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

    def __add__(self, other):
        new = copy.deepcopy(self)
        if isinstance(other, DataContainer):
            new.data += other.data

        elif isinstance(other, numpy.ndarray):
            new.data += other

        return new

    def __iadd__(self, other):
        if isinstance(other, DataContainer):
            self.data += other.data

        elif isinstance(other, numpy.ndarray):
            self.data += other

        return self

    def __sub__(self, other):
        new = copy.deepcopy(self)
        if isinstance(other, DataContainer):
            new.data -= other.data

        elif isinstance(other, numpy.ndarray):
            new.data -= other

        return new

    def __isub__(self, other):
        if isinstance(other, DataContainer):
            self.data -= other.data

        elif isinstance(other, numpy.ndarray):
            self.data -= other

        return self

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

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(DataContainer, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data') + '\n'
        output += ui.data(
            indent=indent + 4,
            field='data',
            value=self.data
        ) + '\n'

        output += ui.line(
            indent=indent + 4,
            field='Dimensions'
        ) + '\n'
        output += ui.data(
            indent=indent + 6,
            field='time_axis',
            value=self.time_axis
        ) + '\n'

        output += ui.line(
            indent=indent + 4,
            field='Timing information'
        ) + '\n'

        output += ui.data(
            indent=indent + 6,
            field='time_resolution',
            value=self.time_resolution,
            unit="sec"
        ) + '\n'

        output += ui.line(field='Meta') + '\n'
        output += ui.data(
            indent=indent + 4,
            field='stats',
            value='Calculated' if self._stats is not None else '-'
        ) + '\n'

        output += ui.data(
            indent=indent + 4,
            field='metadata',
            value=self.metadata if self.metadata else '-'
        ) + '\n'

        output += ui.data(
            indent=indent + 4,
            field='processing_chain',
            value=self.processing_chain if self.processing_chain else '-'
        ) + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(
            indent=indent + 4,
            field='Frames',
            value=self.length
        ) + '\n'

        if self.time_resolution:
            output += ui.data(
                indent=indent + 4,
                field='Seconds',
                value=self._frame_to_time(frame_id=self.length),
                unit='sec'
            ) + '\n'

        if self._focus_start is not None and self._focus_stop is not None:
            output += ui.line(field='Focus segment', indent=indent) + '\n'
            output += ui.line(
                indent=indent + 4,
                field='Duration'
            ) + '\n'

            output += ui.data(
                indent=indent + 6,
                field='Index',
                value=self._focus_stop - self._focus_start
            ) + '\n'

            if self.time_resolution:
                output += ui.data(
                    indent=6, field='Seconds',
                    value=self._frame_to_time(frame_id=self._focus_stop - self._focus_start),
                    unit='sec'
                ) + '\n'

            output += ui.line(
                indent=indent + 4,
                field='Start'
            ) + '\n'

            output += ui.data(
                indent=indent + 6,
                field='Index',
                value=self._focus_start
            ) + '\n'

            if self.time_resolution:
                output += ui.data(
                    indent=indent + 6,
                    field='Seconds',
                    value=self._frame_to_time(frame_id=self._focus_start),
                    unit='sec'
                ) + '\n'

            output += ui.line(indent=indent + 4, field='Stop') + '\n'
            output += ui.data(
                indent=indent + 6,
                field='Index',
                value=self._focus_stop
            ) + '\n'

            if self.time_resolution:
                output += ui.data(
                    indent=indent + 6,
                    field='Seconds',
                    value=self._frame_to_time(frame_id=self._focus_stop),
                    unit='sec'
                ) + '\n'

        return output

    def __nonzero__(self):
        return self.length > 0

    def __len__(self):
        return self.length

    def push_processing_chain_item(self, processor_name, init_parameters=None, process_parameters=None,
                                   preprocessing_callbacks=None,
                                   input_type=None, output_type=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict, optional
            Initialization parameters for the processors
            Default value None

        process_parameters : dict, optional
            Parameters for the process method of the Processor
            Default value None

        preprocessing_callbacks : list of dicts
            Callbacks used for preprocessing
            Default value None

        input_type : ProcessingChainItemType
            Input data type
            Default value None

        output_type : ProcessingChainItemType
            Output data type
            Default value None

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters,
            preprocessing_callbacks=preprocessing_callbacks,
            input_type=input_type,
            output_type=output_type,
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
            Default value None

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

        else:
            frame = int(time / float(self.time_resolution))

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

    def _length_to_frames(self, time):
        return int(numpy.ceil(time * 1.0 / self.time_resolution))

    def _onset_to_frames(self, onset):
        return int(numpy.floor(onset * 1.0 / self.time_resolution))

    def _offset_to_frames(self, offset):
        return int(numpy.ceil(offset * 1.0 / self.time_resolution))

    def set_focus(self,
                  start=None, stop=None, duration=None,
                  start_seconds=None, stop_seconds=None, duration_seconds=None):
        """Set focus segment

        Parameters
        ----------
        start : int, optional
            Frame index of focus segment start.
            Default value None

        stop : int, optional
            Frame index of focus segment stop.
            Default value None

        duration : int, optional
            Frame count of focus segment.
            Default value None


        start_seconds : float, optional
            Time stamp (in seconds) of focus segment start, will be converted to frame index based on
            time resolution of the data matrix.
            Default value None

        stop_seconds : float, optional
            Time stamp (in seconds) of focus segment stop, will be converted to frame index based on
            time resolution of the data matrix.
            Default value None

        duration_seconds : float, optional
            Duration (in seconds) of focus segment, will be converted to frame index based on
            time resolution of the data matrix.
            Default value None

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
            Default value None

        frame_hop : int, optional
            Frame hopping factor, with one every frame is included.
            Default value 1

        Returns
        -------
        numpy.array

        """

        data = self.data

        # Apply frame_ids
        if frame_ids is not None:
            data = data[frame_ids]

        return data[::frame_hop]

    def plot(self, plot=True, figsize=None):
        """Visualize data array.

        Parameters
        ----------
        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        Returns
        -------
        self

        """

        if figsize is None:
            figsize = (10, 5)

        import matplotlib.pyplot as plt
        from librosa.core import frames_to_time
        from librosa.display import TimeFormatter

        if plot:
            plt.figure(figsize=figsize)

        # Plot feature matrix
        if self.time_resolution:
            sr = int(1.0 / float(self.time_resolution))
            x_axis = 'time'
        else:
            sr = 1.0
            x_axis = None

        y = self.get_focused()[0]
        locs = frames_to_time(frames=numpy.arange(len(y)), sr=sr, hop_length=1)

        plt.plot(locs, y)
        axes = plt.gca()

        axes.set_xlim([locs.min(), locs.max()])
        if x_axis == 'time':
            axes.xaxis.set_major_formatter(TimeFormatter(lag=False))
            axes.xaxis.set_label_text('Time')
        elif x_axis is None or x_axis in ['off', 'none']:
            axes.set_xticks([])

        # Add filename to first subplot
        if self.filename:
            plt.title(self.filename)

        if plot:
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
            File path
            Default value None

        data : numpy.ndarray, optional
            Data to initialize the container
            Default value None

        stats : dict, optional
            Statistics of the data
            Default value None

        metadata : dict or MetadataContainer, optional
            MetadataContainer
            Default value None

        time_resolution : float, optional
            Time resolution
            Default value None

        processing_chain : ProcessingChain, optional
            Processing chain.
            Default value None

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
            File path
            Default value None

        data : numpy.ndarray, optional
            Data to initialize the container
            Default value None

        stats : dict, optional
            Statistics of the data
            Default value None

        metadata : dict or MetadataContainer, optional
            MetadataContainer
            Default value None

        time_resolution : float, optional
            Time resolution
            Default value None

        processing_chain : ProcessingChain, optional
            Processing chain.
            Default value None

        """

        if data is None:
            # Initialize with 2D-matrix
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

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(DataMatrix2DContainer, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'

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
            Default value None

        vector_ids : list of int, optional
            Data ids of frame's data vector to be included.
            Default value None

        frame_hop : int, optional
            Frame hopping factor, with one every frame is included.
            Default value 1

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

    def change_axis(self, time_axis=None, data_axis=None):
        """Set axis

        Parameters
        ----------
        time_axis : int, optional
            New data axis for time. Current axis and new axis are swapped.
            Default value None

        data_axis : int, optional
            New data axis for data. Current axis and new axis are swapped.
            Default value None

        Returns
        -------
        self

        """

        # Get not None values
        axis_list = [time_axis, data_axis]
        axis_list = [x for x in axis_list if x is not None]

        # Get unique values
        axis_set = set(axis_list)

        if len(axis_list) != len(axis_set):
            message = '{name}: Give unique axis indexes [{axis_list}].'.format(
                name=self.__class__.__name__,
                axis_list=axis_list
            )

            self.logger.exception(message)
            raise ValueError(message)

        if time_axis > 1:
            message = '{name}: Given time_axis too large [{time_axis}].'.format(
                name=self.__class__.__name__,
                time_axis=time_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if data_axis > 1:
            message = '{name}: Given data_axis too large [{data_axis}].'.format(
                name=self.__class__.__name__,
                data_axis=data_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Get axis map
        axis_map = OneToOneMappingContainer({
            'time_axis': self.time_axis,
            'data_axis': self.data_axis
        })

        if time_axis is not None and time_axis != self.time_axis:
            # Modify time axis

            # Get axis names
            target_axis = axis_map.flipped.map(time_axis)
            source_axis = axis_map.flipped.map(self.time_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.time_axis,
                axis2=time_axis
            )

            # Store new axes
            axis_map[target_axis] = self.time_axis
            axis_map[source_axis] = time_axis

            setattr(self, str(target_axis), self.time_axis)
            setattr(self, str(source_axis), time_axis)

        if data_axis is not None and data_axis != self.data_axis:
            # Modify data axis

            # Get axis names
            target_axis = axis_map.flipped.map(data_axis)
            source_axis = axis_map.flipped.map(self.data_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.data_axis,
                axis2=data_axis
            )

            # Store new axes
            axis_map[target_axis] = self.data_axis
            axis_map[source_axis] = data_axis

            setattr(self, str(target_axis), self.data_axis)
            setattr(self, str(source_axis), data_axis)

        return self

    def plot(self, plot=True, show_color_bar=False, figsize=None, xlabel=None, ylabel=None):
        """Visualize data matrix.

        Parameters
        ----------

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        show_color_bar : bool
            Show color bar next to plot.
            Default value False

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        xlabel : str
            Label for X axis
            Default value None

        ylabel : str
            Label for Y axis
            Default value None

        Returns
        -------
        self

        """

        if figsize is None:
            figsize = (10, 5)

        from librosa.display import specshow
        import matplotlib.pyplot as plt

        if plot:
            plt.figure(figsize=figsize)

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

        if show_color_bar:
            # Add color bar
            plt.colorbar()

        # Add filename to first subplot
        if hasattr(self, 'filename') and self.filename:
            plt.title(self.filename)

        if ylabel:
            plt.ylabel(ylabel, fontsize=16)

        if xlabel:
            plt.xlabel(xlabel, fontsize=16)

        if plot:
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
            File path
            Default value None

        data : numpy.ndarray, optional
            Data to initialize the container
            Default value None

        stats : dict, optional
            Statistics of the data
            Default value None

        metadata : dict or MetadataContainer, optional
            MetadataContainer
            Default value None

        time_resolution : float, optional
            Time resolution
            Default value None

        processing_chain : ProcessingChain, optional
            Processing chain.
            Default value None

        """

        if data is None:
            # Initialize with 3D-matrix
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

    def __getstate__(self):
        d = super(DataMatrix3DContainer, self).__getstate__()
        d.update({
            'sequence_axis': self.sequence_axis
        })

        return d

    def __setstate__(self, d):
        super(DataMatrix3DContainer, self).__setstate__(d)
        self.sequence_axis = d['sequence_axis']

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(DataMatrix3DContainer, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'
        output += ui.data(indent=indent + 4, field='sequence_axis', value=self.sequence_axis) + '\n'

        return output

    def change_axis(self, time_axis=None, data_axis=None, sequence_axis=None):
        """Set axis

        Parameters
        ----------
        time_axis : int, optional
            New data axis for time. Current axis and new axis are swapped.
            Default value None

        data_axis : int, optional
            New data axis for data. Current axis and new axis are swapped.
            Default value None

        sequence_axis : int, optional
            New data axis for data sequence. Current axis and new axis are swapped.
            Default value None

        Returns
        -------
        self

        """

        # Get not None values
        axis_list = [time_axis, data_axis, sequence_axis]
        axis_list = [x for x in axis_list if x is not None]

        # Get unique values
        axis_set = set(axis_list)

        if len(axis_list) != len(axis_set):
            message = '{name}: Give unique axis indexes [{axis_list}].'.format(
                name=self.__class__.__name__,
                axis_list=axis_list
            )

            self.logger.exception(message)
            raise ValueError(message)

        if time_axis > 2:
            message = '{name}: Given time_axis too large [{time_axis}].'.format(
                name=self.__class__.__name__,
                time_axis=time_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if data_axis > 2:
            message = '{name}: Given data_axis too large [{data_axis}].'.format(
                name=self.__class__.__name__,
                data_axis=data_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if sequence_axis > 2:
            message = '{name}: Given sequence_axis too large [{sequence_axis}].'.format(
                name=self.__class__.__name__,
                sequence_axis=sequence_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Get axis map
        axis_map = OneToOneMappingContainer({
            'time_axis': self.time_axis,
            'data_axis': self.data_axis,
            'sequence_axis': self.sequence_axis,
        })
        if time_axis is not None and time_axis != self.time_axis:
            # Modify time axis

            # Get axis names
            target_axis = axis_map.flipped.map(time_axis)
            source_axis = axis_map.flipped.map(self.time_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.time_axis,
                axis2=time_axis
            )

            # Store new axes
            axis_map[target_axis] = self.time_axis
            axis_map[source_axis] = time_axis

            setattr(self, str(target_axis), self.time_axis)
            setattr(self, str(source_axis), time_axis)

        if data_axis is not None and data_axis != self.data_axis:
            # Modify data axis

            # Get axis names
            target_axis = axis_map.flipped.map(data_axis)
            source_axis = axis_map.flipped.map(self.data_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.data_axis,
                axis2=data_axis
            )

            # Store new axes
            axis_map[target_axis] = self.data_axis
            axis_map[source_axis] = data_axis

            setattr(self, str(target_axis), self.data_axis)
            setattr(self, str(source_axis), data_axis)

        if sequence_axis is not None and sequence_axis != self.sequence_axis:
            # Modify sequence axis

            # Get axis names
            target_axis = axis_map.flipped.map(sequence_axis)
            source_axis = axis_map.flipped.map(self.sequence_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.sequence_axis,
                axis2=sequence_axis
            )

            # Store new axes
            axis_map[target_axis] = self.sequence_axis
            axis_map[source_axis] = sequence_axis

            setattr(self, str(target_axis), self.sequence_axis)
            setattr(self, str(source_axis), sequence_axis)

        return self

    def plot(self, show_color_bar=False, show_filename=True, plot=True, figsize=None):
        """Plot data

        Parameters
        ----------

        show_color_bar : bool
            Show color bar next to plot.
            Default value False

        show_filename : bool
            Show filename as figure title
            Default value True

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,10) is used.
            Default value None

        Returns
        -------
        self

        """

        if figsize is None:
            figsize = (10, 10)

        data = self.get_focused()

        if data.shape[self.sequence_axis] < 20:
            from librosa.display import specshow
            import matplotlib.pyplot as plt
            if plot:
                plt.figure(figsize=figsize)

            for sequence_id in range(data.shape[self.sequence_axis]):
                ax = plt.subplot(data.shape[self.sequence_axis], 1, sequence_id + 1)
                current_data = data[:, :, sequence_id]
                if self.time_axis == 0:
                    # Make sure time is on x-axis
                    current_data = current_data.T

                # Plot data matrix
                if self.time_resolution:
                    sr = int(1.0 / float(self.time_resolution))
                    x_axis = 'time'

                else:
                    sr = 1.0
                    x_axis = None

                specshow(
                    current_data,
                    x_axis=x_axis,
                    sr=sr,
                    hop_length=1
                )

                plt.ylabel(str(sequence_id))

                if show_color_bar:
                    # Add color bar
                    plt.colorbar()

                if sequence_id < data.shape[self.sequence_axis]-1:
                    ax.axes.get_xaxis().set_visible(False)

                # Add filename to first subplot
                if show_filename and hasattr(self, 'filename') and self.filename:
                    plt.title(self.filename)
                    show_filename = False

            if plot:
                plt.tight_layout()
                plt.show()

        else:
            # TODO find method to visualize deep matrices.
            message = '{name}: Matrix is too deep, plot-method not yet implemented.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise NotImplementedError(message)


class DataMatrix4DContainer(DataMatrix3DContainer):
    """Four-dimensional data matrix container class, inherited from DataMatrix3DContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path
            Default value None

        data : numpy.ndarray, optional
            Data to initialize the container
            Default value None

        stats : dict, optional
            Statistics of the data
            Default value None

        metadata : dict or MetadataContainer, optional
            MetadataContainer
            Default value None

        time_resolution : float, optional
            Time resolution
            Default value None

        processing_chain : ProcessingChain, optional
            Processing chain.
            Default value None

        """

        if data is None:
            # Initialize with 4D-matrix
            data = numpy.ndarray((0, 0, 0, 0))

        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataMatrix3DContainer init
        DataMatrix3DContainer.__init__(self, **kwargs)

        # Run super init
        super(DataMatrix4DContainer, self).__init__(**kwargs)

        # Matrix axis
        self.data_axis = 0
        self.time_axis = 1
        self.sequence_axis = 2
        self.channel_axis = 3

    def __getstate__(self):
        d = super(DataMatrix4DContainer, self).__getstate__()
        d.update({
            'channel_axis': self.channel_axis
        })

        return d

    def __setstate__(self, d):
        super(DataMatrix4DContainer, self).__setstate__(d)
        self.channel_axis = d['channel_axis']

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(DataMatrix4DContainer, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Data', indent=indent) + '\n'

        output += ui.line(indent=indent + 2, field='Dimensions') + '\n'
        output += ui.data(indent=indent + 4, field='time_axis', value=self.time_axis) + '\n'
        output += ui.data(indent=indent + 4, field='data_axis', value=self.data_axis) + '\n'
        output += ui.data(indent=indent + 4, field='sequence_axis', value=self.sequence_axis) + '\n'
        output += ui.data(indent=indent + 4, field='channel_axis', value=self.channel_axis) + '\n'

        return output

    def change_axis(self, time_axis=None, data_axis=None, sequence_axis=None, channel_axis=None):
        """Set axis

        Parameters
        ----------
        time_axis : int, optional
            New data axis for time. Current axis and new axis are swapped.
            Default value None

        data_axis : int, optional
            New data axis for data. Current axis and new axis are swapped.
            Default value None

        sequence_axis : int, optional
            New data axis for data sequence. Current axis and new axis are swapped.
            Default value None

        channel_axis : int, optional
            New data axis for data channel. Current axis and new axis are swapped.
            Default value None

        Returns
        -------
        self

        """

        # Get not None values
        axis_list = [time_axis, data_axis, sequence_axis, channel_axis]
        axis_list = [x for x in axis_list if x is not None]

        # Get unique values
        axis_set = set(axis_list)

        if len(axis_list) != len(axis_set):
            message = '{name}: Give unique axis indexes [{axis_list}].'.format(
                name=self.__class__.__name__,
                axis_list=axis_list
            )

            self.logger.exception(message)
            raise ValueError(message)

        if time_axis > 3:
            message = '{name}: Given time_axis too large [{time_axis}].'.format(
                name=self.__class__.__name__,
                time_axis=time_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if data_axis > 3:
            message = '{name}: Given data_axis too large [{data_axis}].'.format(
                name=self.__class__.__name__,
                data_axis=data_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if sequence_axis > 3:
            message = '{name}: Given sequence_axis too large [{sequence_axis}].'.format(
                name=self.__class__.__name__,
                sequence_axis=sequence_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        if channel_axis > 3:
            message = '{name}: Given channel_axis too large [{channel_axis}].'.format(
                name=self.__class__.__name__,
                channel_axis=channel_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Get axis map
        axis_map = OneToOneMappingContainer({
            'time_axis': self.time_axis,
            'data_axis': self.data_axis,
            'sequence_axis': self.sequence_axis,
            'channel_axis': self.channel_axis,
        })

        if time_axis is not None and time_axis != self.time_axis:
            # Modify time axis

            # Get axis names
            target_axis = axis_map.flipped.map(time_axis)
            source_axis = axis_map.flipped.map(self.time_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.time_axis,
                axis2=time_axis
            )

            # Store new axes
            axis_map[target_axis] = self.time_axis
            axis_map[source_axis] = time_axis

            setattr(self, str(target_axis), self.time_axis)
            setattr(self, str(source_axis), time_axis)

        if data_axis is not None and data_axis != self.data_axis:
            # Modify data axis

            # Get axis names
            target_axis = axis_map.flipped.map(data_axis)
            source_axis = axis_map.flipped.map(self.data_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.data_axis,
                axis2=data_axis
            )

            # Store new axes
            axis_map[target_axis] = self.data_axis
            axis_map[source_axis] = data_axis

            setattr(self, str(target_axis), self.data_axis)
            setattr(self, str(source_axis), data_axis)

        if sequence_axis is not None and sequence_axis != self.sequence_axis:
            # Modify sequence axis

            # Get axis names
            target_axis = axis_map.flipped.map(sequence_axis)
            source_axis = axis_map.flipped.map(self.sequence_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.sequence_axis,
                axis2=sequence_axis
            )

            # Store new axes
            axis_map[target_axis] = self.sequence_axis
            axis_map[source_axis] = sequence_axis

            setattr(self, str(target_axis), self.sequence_axis)
            setattr(self, str(source_axis), sequence_axis)

        if channel_axis is not None and channel_axis != self.channel_axis:
            # Modify channel axis

            # Get axis names
            target_axis = axis_map.flipped.map(channel_axis)
            source_axis = axis_map.flipped.map(self.channel_axis)

            # Modify data
            self.data = numpy.swapaxes(
                a=self.data,
                axis1=self.channel_axis,
                axis2=channel_axis
            )

            # Store new axes
            axis_map[target_axis] = self.channel_axis
            axis_map[source_axis] = channel_axis

            setattr(self, str(target_axis), self.channel_axis)
            setattr(self, str(source_axis), channel_axis)

        return self

    def plot(self, show_color_bar=False, show_filename=True, plot=True, figsize=None):
        """Plot data

        Parameters
        ----------

        show_color_bar : bool
            Show color bar next to plot.
            Default value False

        show_filename : bool
            Show filename as figure title
            Default value True

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        Returns
        -------
        self

        """

        if figsize is None:
            figsize = (10, 5)

        data = self.get_focused()

        if data.shape[self.sequence_axis] <= 10:
            from librosa.display import specshow
            import matplotlib.pyplot as plt

            if plot:
                plt.figure(figsize=figsize)

            rows_count = data.shape[self.channel_axis]
            for sequence_id in range(data.shape[self.sequence_axis]):
                for channel_id in range(data.shape[self.channel_axis]):
                    if rows_count == 1:
                        # Special case when only one stream, transpose presentation
                        index = 1 + sequence_id

                        plt.subplot(
                            data.shape[self.sequence_axis],
                            rows_count,
                            index
                        )

                    else:
                        index = 1 + (sequence_id + channel_id * data.shape[self.sequence_axis])

                        plt.subplot(
                            rows_count,
                            data.shape[self.sequence_axis],
                            index
                        )

                    if self.sequence_axis == 0 and self.channel_axis == 1:
                        current_data = data[sequence_id, channel_id, :, :]

                    elif self.sequence_axis == 0 and self.channel_axis == 2:
                        current_data = data[sequence_id, :, channel_id, :]

                    elif self.sequence_axis == 0 and self.channel_axis == 3:
                        current_data = data[sequence_id, :, :, channel_id]

                    elif self.sequence_axis == 1 and self.channel_axis == 3:
                        current_data = data[:, sequence_id, :, channel_id]

                    elif self.sequence_axis == 2 and self.channel_axis == 3:
                        current_data = data[:, :, sequence_id, channel_id]

                    else:
                        message = '{name}: Unknown data axes'.format(
                            name=self.__class__.__name__
                        )

                        self.logger.exception(message)
                        raise ValueError(message)

                    # Plot feature matrix
                    ax = specshow(
                        data=current_data,
                        x_axis='time',
                        sr=1,
                        hop_length=1
                    )

                    if rows_count == 1:
                        if channel_id != data.shape[self.channel_axis] - 1:
                            ax.tick_params(
                                axis='x',
                                which='both',
                                bottom=False,
                                top=False,
                                labelbottom=False
                            )
                            plt.xlabel('')
                    else:
                        if channel_id+1 != data.shape[self.channel_axis]:
                            ax.tick_params(
                                axis='x',
                                which='both',
                                bottom=False,
                                top=False,
                                labelbottom=False
                            )
                            plt.xlabel('')

                    plt.ylabel('seq['+str(sequence_id)+'] chan['+str(channel_id)+']')

            # Add filename to first subplot
            if show_filename and hasattr(self, 'filename') and self.filename:
                plt.title(self.filename)

            if plot:
                plt.tight_layout()
                plt.show()

        else:
            # TODO find method to visualize deep matrices.
            message = '{name}: Matrix is too deep, plot-method not yet implemented.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise NotImplementedError(message)


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

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(BinaryMatrix2DContainer, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Labels', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='label_list', value=self.label_list) + '\n'

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

    def plot(self, plot=True, binary_matrix=None, data_container=None, figsize=None, panel_title=None,
             binary_panel_title='Binary matrix', data_panel_title='Data', panel_title_position='right',
             color='binary'):
        """Visualize binary matrix, and optionally synced data matrix.

        For example, this can be used to visualize sound event activity along with the acoustic features.

        Parameters
        ----------
        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        binary_matrix : numpy.ndarray
            Binary matrix, if None given internal data used.
            Default value None

        data_container : DataContainer
            Extra data matrix to be shown along with binary matrix.
            Default value None

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        panel_title :  str
            Panel title (ylabel for first subplot)
            Default value None

        binary_panel_title : str
            Binary panel title (ylabel for first subplot)
            Default value "Binary matrix"

        data_panel_title : str
            Data panel title (ylabel for second subplot)
            Default value "Data"

        panel_title_position : str
            Panel title position ['left', 'right']
            Default value "right"

        color : str
            Color scheme used ['binary', 'gray', 'purple', 'blue', 'green', 'orange', 'red']
            Default value 'binary'

        Returns
        -------
        None

        """

        if figsize is None:
            figsize = (10, 5)

        import matplotlib.pyplot as plt
        from librosa.display import specshow

        if binary_matrix is None:
            binary_matrix = self.data

        if self.time_axis == 0:
            binary_matrix = binary_matrix.T

        if color:
            if color == 'binary':
                cmap = plt.cm.binary
            elif color == 'gray':
                cmap = plt.cm.gray_r
            elif color == 'purple':
                cmap = plt.cm.Purples
            elif color == 'blue':
                cmap = plt.cm.Blues
            elif color == 'green':
                cmap = plt.cm.Greens
            elif color == 'orange':
                cmap = plt.cm.Oranges
            elif color == 'red':
                cmap = plt.cm.Reds
            else:
                cmap = plt.cm.binary
        else:
            cmap = plt.cm.binary

        if binary_matrix is not None and data_container is not None:
            fig, axes = plt.subplots(2, 1, figsize=figsize)
            fig.subplots_adjust(top=1.0, bottom=0.0, right=1.0, hspace=0.05, wspace=0.00)

            # Features
            ax1 = plt.subplot(2, 1, 1)
            specshow(
                binary_matrix,
                x_axis='time',
                sr=int(1 / float(self.time_resolution)),
                hop_length=1,
                cmap=cmap
            )

            y_ticks = numpy.arange(0, len(self.label_list)) + 0.5
            ax1.set_yticks(y_ticks)
            ax1.set_yticklabels(self.label_list, fontsize=20)
            ax1.get_xaxis().set_visible(False)
            ax1.yaxis.set_label_position(panel_title_position)
            plt.ylabel(binary_panel_title, fontsize=20)

            # Binary matrix
            ax2 = plt.subplot(2, 1, 2)

            specshow(
                data_container.data,
                x_axis='time',
                sr=int(1 / float(data_container.hop_length_seconds)),
                hop_length=1
            )
            ax2.yaxis.set_label_position(panel_title_position)
            plt.ylabel(data_panel_title, fontsize=20)
            plt.xlabel('Time', fontsize=20)

        elif binary_matrix is not None and data_container is None:
            if plot:
                plt.figure(figsize=figsize)

            # Binary matrix
            if self.time_resolution:
                sr = int(1.0 / float(self.time_resolution))
                x_axis = 'time'
            else:
                sr = 1.0
                x_axis = None

            ax = specshow(
                binary_matrix,
                x_axis=x_axis,
                sr=sr,
                hop_length=1,
                cmap=cmap
            )

            if panel_title:
                ax.yaxis.set_label_position(panel_title_position)
                plt.ylabel(panel_title, fontsize=20)

            if self.time_resolution:
                plt.xlabel('Time', fontsize=20)

            if self.label_list:
                ax.yaxis.set_label_position("right")
                y_ticks = numpy.arange(0, len(self.label_list)) + 0.5
                ax.set_yticks(y_ticks)
                ax.set_yticklabels(self.label_list, fontsize=20)

        if plot:
            plt.show()


class DataRepository(RepositoryContainer):
    """Data repository container class to store multiple DataContainers together.

    Containers are stored in a dict, label is used as dictionary key and value is associated data container.

    """

    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, filename=None, default_stream_id=0, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename: str or dict
            Either one filename (str) or multiple filenames in a dictionary. Dictionary based parameter is used to
            construct the repository from separate FeatureContainers, two formats for the dictionary is supported:
            1) label as key, and filename as value, and 2) two-level dictionary label as key1, stream as
            key2 and filename as value.

        default_stream_id : str or int
            Default stream id used when accessing data
            Default value 0

        processing_chain : ProcessingChain
            Processing chain to be included into repository
            Default value None

        """

        kwargs['filename'] = filename

        super(DataRepository, self).__init__(**kwargs)

        self.default_stream_id = default_stream_id

        from dcase_util.processors import ProcessingChain
        if processing_chain is None:
            processing_chain = ProcessingChain()

        self.processing_chain = processing_chain

        self.item_class = DataMatrix2DContainer

        if data is not None and isinstance(data, dict):
            dict.update(self, data)

    def __getstate__(self):
        d = super(DataRepository, self).__getstate__()
        d.update({
            'default_stream_id': self.default_stream_id,
            'processing_chain': self.processing_chain,
            'item_class': self.item_class
        })

        return d

    def __setstate__(self, d):
        super(DataRepository, self).__setstate__(d)

        self.default_stream_id = d['default_stream_id']
        self.processing_chain = d['processing_chain']
        self.item_class = d['item_class']

        # Remove internal variables from dict
        del d['default_stream_id']
        del d['processing_chain']
        del d['item_class']

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = ''
        output += ui.class_name(self.__class__.__name__, indent=indent) + '\n'

        if hasattr(self, 'filename') and self.filename:
            output += ui.data(
                field='filename',
                value=self.filename,
                indent=indent
            ) + '\n'

        output += ui.line(field='Repository info', indent=indent) + '\n'

        if hasattr(self, 'item_class') and self.item_class:
            output += ui.data(
                indent=indent + 2,
                field='Item class',
                value=self.item_class.__name__
            ) + '\n'

        output += ui.data(
            indent=indent + 2,
            field='Item count',
            value=len(self)
        ) + '\n'

        output += ui.data(
            indent=indent + 2,
            field='Labels',
            value=list(self.keys())
        ) + '\n'

        output += ui.line(field='Content', indent=indent) + '\n'
        for label, label_data in iteritems(self):
            if label_data:
                if isinstance(label_data, dict):
                    for stream_id, stream_data in iteritems(label_data):
                        if hasattr(stream_data, 'to_string'):
                            output += ui.data(
                                indent=indent + 2,
                                field='['+str(label)+']' + '[' + str(stream_id) + ']',
                                value=stream_data.to_string(ui=ui)
                            ) + '\n'

                        else:
                            output += ui.data(
                                indent=indent + 2,
                                field='[' + str(label) + ']' + '[' + str(stream_id) + ']',
                                value=stream_data
                            ) + '\n'

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

    def load(self, filename=None, collect_from_containers=True):
        """Load file list

        Parameters
        ----------
        filename : str or dict
            Either one filename (str) or multiple filenames in a dictionary. Dictionary based parameter is used to
            construct the repository from separate FeatureContainers, two formats for the dictionary is supported: 1)
            label as key, and filename as value, and 2) two-level dictionary label as key1, stream as key2 and
            filename as value. If None given, parameter given to class initializer is used instead.
            Default value None

        collect_from_containers : bool
            Collect data to the repository from separate containers.
            Default value True

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename

        if isinstance(self.filename, basestring):
            # String filename given use load method from parent class
            if os.path.exists(self.filename):
                # If file exist load it
                self.detect_file_format()
                self.validate_format()

                super(DataRepository, self).load(filename=self.filename)

            if collect_from_containers:
                # Collect data to the repository from separate containers
                filename_base, file_extension = os.path.splitext(self.filename)
                containers = glob.glob(filename_base + '.*-*' + file_extension)
                for filename in containers:
                    label, stream_id = os.path.splitext(filename)[0].split('.')[-1].split('-')
                    if label not in self:
                        self[label] = {}

                    self[label][int(stream_id)] = self.item_class().load(filename=filename)

        elif isinstance(self.filename, dict):
            sorted(self.filename)

            # Dictionary based filename given
            if filelist_exists(self.filename):
                dict.clear(self)

                for label, data in iteritems(self.filename):
                    self[label] = {}
                    if not label.startswith('_'):
                        # Skip labels starting with '_', those are just for extra info
                        if isinstance(data, basestring):
                            # filename given directly, only one feature stream per method inputted.
                            self[label][self.default_stream_id] = self.item_class().load(filename=data)

                        elif isinstance(data, dict):
                            for stream, filename in iteritems(data):
                                self[label][stream] = self.item_class().load(filename=filename)

            else:
                # All filenames did not exists, find which ones is missing and raise error.
                for label, data in iteritems(self.filename):
                    if isinstance(data, basestring) and not os.path.isfile(data):
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
            message = '{name}: Repository cannot be loaded, no valid filename set.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise IOError(message)

        return self

    def save(self, filename=None, split_into_containers=False):
        """Save file

        Parameters
        ----------
        filename : str or dict
            File path
            Default value filename given to class constructor

        split_into_containers : bool
            Split data from repository separate containers and save them individually.
            Default value False

        Raises
        ------
        ImportError:
            Error if file format specific module cannot be imported

        IOError:
            File has unknown file format

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename

        if split_into_containers and isinstance(self.filename, basestring):
            # Automatic filename generation for saving data into separate containers
            filename_base, file_extension = os.path.splitext(self.filename)
            filename_dictionary = {}
            for label in self.labels:
                if label not in filename_dictionary:
                    filename_dictionary[label] = {}

                for stream_id in self.stream_ids(label=label):
                    if stream_id not in filename_dictionary[label]:
                        filename_dictionary[label][stream_id] = filename_base + '.' + label + '-' + str(stream_id) + file_extension

            self.filename = filename_dictionary

        if isinstance(self.filename, basestring):
            # Single output file as target
            self.detect_file_format()
            self.validate_format()

            # String filename given use load method from parent class
            super(DataRepository, self).save(filename=self.filename)

        elif isinstance(self.filename, dict):
            # Custom naming and splitting into separate containers
            sorted(self.filename)

            # Dictionary of filenames given, save each data container in the repository separately
            for label in self.labels:
                if label in self.filename:
                    for stream_id in self.stream_ids(label=label):
                        if stream_id in self.filename[label]:
                            current_container = self.get_container(label=label, stream_id=stream_id)
                            current_container.save(filename=self.filename[label][stream_id])

        return self

    def get_container(self, label, stream_id=None):
        """Get container from repository

        Parameters
        ----------
        label : str
            Label

        stream_id : str or int
            Stream id, if None, default_stream is used.
            Default value None

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
            Default value None

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

    def push_processing_chain_item(self, processor_name, init_parameters=None, process_parameters=None,
                                   preprocessing_callbacks=None,
                                   input_type=None, output_type=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict, optional
            Initialization parameters for the processors
            Default value None

        process_parameters : dict, optional
            Parameters for the process method of the Processor
            Default value None

        preprocessing_callbacks : list of dicts
            Callbacks used for preprocessing
            Default value None

        input_type : ProcessingChainItemType
            Input data type
            Default value None

        output_type : ProcessingChainItemType
            Output data type
            Default value None

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters,
            preprocessing_callbacks=preprocessing_callbacks,
            input_type=input_type,
            output_type=output_type
        )

        return self

    def plot(self, plot=True, figsize=None):
        """Visualize data stored in the repository.

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,10) is used.
            Default value None

        Returns
        -------
        self

        """

        if figsize is None:
            figsize = (10, 10)

        from librosa.display import specshow
        import matplotlib.pyplot as plt

        rows_count = 0
        for label_id, label in enumerate(self.labels):
            if rows_count < len(self.stream_ids(label)):
                rows_count = len(self.stream_ids(label))

        labels = list(self.keys())
        labels.sort()

        if plot:
            plt.figure(figsize=figsize)

        for label_id, label in enumerate(self.labels):
            for stream_id in self.stream_ids(label):
                if rows_count == 1:
                    # Special case when only one stream, transpose presentation
                    index = 1 + label_id

                    plt.subplot(
                        len(self.labels),
                        rows_count,
                        index
                    )

                else:
                    index = 1 + (label_id + stream_id * len(self.labels))

                    plt.subplot(
                        rows_count,
                        len(self.labels),
                        index
                    )

                current_container = self.get_container(
                    label=label,
                    stream_id=stream_id
                )

                # Plot feature matrix
                ax = specshow(
                    data=current_container.data,
                    x_axis='time',
                    sr=int(1 / float(current_container.time_resolution)),
                    hop_length=1
                )
                if rows_count == 1:
                    if label_id != len(self.labels) - 1:
                        ax.tick_params(
                            axis='x',
                            which='both',
                            bottom='off',
                            top='off',
                            labelbottom='off'
                        )
                        plt.xlabel('')
                else:
                    if stream_id+1 != len(self.stream_ids(label)):
                        ax.tick_params(
                            axis='x',
                            which='both',
                            bottom='off',
                            top='off',
                            labelbottom='off'
                        )
                        plt.xlabel('')

                plt.ylabel('['+str(label)+']['+str(stream_id)+']')

        if plot:
            plt.show()

        return self
