#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import six
from six import iteritems
import numpy
import scipy
import copy
import os
import glob
from past.builtins import basestring

from dcase_util.containers import ObjectContainer
from dcase_util.ui import FancyStringifier
from dcase_util.utils import VectorRecipeParser, filelist_exists


class Normalizer(ObjectContainer):
    """Data normalizer to accumulate data statistics"""

    def __init__(self, n=None, s1=None, s2=None, mean=None, std=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        n : int
            Item count used to calculate statistics
            Default value None

        s1 : np.array [shape=(vector_length,)]
            Vector-wise sum of the data seen by the Normalizer
            Default value None

        s2 : np.array [shape=(vector_length,)]
            Vector-wise sum^2 of the data seen by the Normalizer
            Default value None

        mean : np.ndarray() [shape=(vector_length, 1)]
            Mean of the data
            Default value None

        std : np.ndarray() [shape=(vector_length, 1)]
            Standard deviation of the data
            Default value None

        """

        # Run super init to call init of mixins too
        super(Normalizer, self).__init__(**kwargs)

        self.n = n
        self.s1 = s1
        self.s2 = s2
        self._mean = mean
        self._std = std

        # Make sure mean and std are numpy.array
        if isinstance(self._mean, list):
            self._mean = numpy.array(self._mean)
        if isinstance(self._std, list):
            self._std = numpy.array(self._std)

        # Make sure mean and std has correct shape
        if isinstance(self._mean, numpy.ndarray) and len(self._mean.shape) == 1:
            self._mean = self._mean.reshape((-1, 1))
        if isinstance(self._std, numpy.ndarray) and len(self._std.shape) == 1:
            self._std = self._std.reshape((-1, 1))

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

        output = super(Normalizer, self).to_string(ui=ui, indent=indent)

        output += ui.data(field='Mean', value=self.mean, indent=indent) + '\n'
        output += ui.data(field='Std', value=self.std, indent=indent) + '\n'

        output += ui.data(field='n', value=self.n, indent=indent) + '\n'

        return output

    def __getstate__(self):
        d = super(ObjectContainer, self).__getstate__()
        d.update(
            {
                'n': self.n,
                's1': self.s1,
                's2': self.s2,
                '_mean': self._mean,
                '_std': self._std,
            }
        )
        return d

    def __setstate__(self, d):
        super(ObjectContainer, self).__setstate__(d)
        self.n = d['n']
        self.s1 = d['s1']
        self.s2 = d['s2']
        self._mean = d['_mean']
        self._std = d['_std']

    @property
    def mean(self):
        """Mean vector

        Returns
        -------
        numpy.array(vector_length, 1)

        """

        if self._mean is None:
            if self.s1 is not None and self.n is not None:
                self._mean = (self.s1 / self.n).reshape(-1, 1)
            else:
                self._mean = None

        return self._mean

    @mean.setter
    def mean(self, value):
        self._mean = value

    @property
    def std(self):
        """Standard deviation vector

        Returns
        -------
        numpy.array(vector_length, 1)

        """

        if self._std is None:
            if self.s1 is not None and self.s2 is not None and self.n is not None:
                self._std = numpy.sqrt((self.n * self.s2 - (self.s1 * self.s1)) / (self.n * (self.n - 1))).reshape(-1, 1)
            else:
                self._std = None

        return self._std

    @std.setter
    def std(self, value):
        self._std = value

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, type, value, traceback):
        # Finalize accumulated calculation
        self.finalize()

    def __call__(self, *args, **kwargs):
        return self.normalize(*args, **kwargs)

    def reset(self):
        """Reset internal variables.
        """

        self.n = None
        self.s1 = None
        self.s2 = None
        self.mean = None
        self.std = None

    def accumulate(self, data, time_axis=1):
        """Accumulate statistics

        Parameters
        ----------
        data : FeatureContainer or np.ndarray
            Data in FeatureContainer or in np.ndarray

        time_axis : int
            If data contains np.ndarray axis for the time
            Default value 1

        Returns
        -------
        self

        """

        from dcase_util.containers import FeatureContainer

        stats = None

        if isinstance(data, FeatureContainer):
            stats = data.stats

        elif isinstance(data, numpy.ndarray):
            stats = {
                'mean': numpy.mean(data, axis=time_axis),
                'std': numpy.std(data, axis=time_axis),
                'n': data.shape[time_axis],
                's1': numpy.sum(data, axis=time_axis),
                's2': numpy.sum(data ** 2, axis=time_axis),
            }

        if stats:
            if self.n is None:
                self.n = stats['n']
            else:
                self.n += stats['n']

            if self.s1 is None:
                self.s1 = stats['s1']
            else:
                self.s1 += stats['s1']

            if self.s2 is None:
                self.s2 = stats['s2']
            else:
                self.s2 += stats['s2']

        return self

    def finalize(self):
        """Finalize statistics calculation

        Accumulated values are used to get mean and std for the seen data.

        Parameters
        ----------

        Returns
        -------
        self

        """

        self._mean = (self.s1 / self.n).reshape(-1, 1)
        self._std = numpy.sqrt((self.n * self.s2 - (self.s1 * self.s1)) / (self.n * (self.n - 1))).reshape(-1, 1)

        return self

    def normalize(self, data, **kwargs):
        """Normalize data matrix with internal statistics of the class.

        Parameters
        ----------
        data : DataContainer or np.ndarray
            DataContainer or np.ndarray to be normalized

        Returns
        -------
        DataContainer or numpy.ndarray [shape=(frames, number of data values)]
            Normalized data matrix

        """
        from dcase_util.containers import DataContainer

        # Make copy of data to prevent data contamination
        data = copy.deepcopy(data)

        if isinstance(data, DataContainer):
            data.data = (data.data - self.mean) / self.std

            return data

        elif isinstance(data, numpy.ndarray):
            return (data - self.mean) / self.std

    def plot(self, plot=True, figsize=None):
        """Visualize normalization factors.

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

        if plot:
            plt.figure(figsize=figsize)

        # Add filename to first subplot
        if hasattr(self, 'filename') and self.filename:
            plt.title(self.filename)

        upper = (self.mean + self.std).reshape(-1)
        lower = (self.mean - self.std).reshape(-1)

        plt.fill_between(range(self.mean.shape[0]), lower, upper, facecolor='grey', alpha=0.1, step='mid')

        plt.errorbar(
            x=range(self.mean.shape[0]),
            y=self.mean.reshape(-1),
            yerr=self.std.reshape(-1),
            linestyle='None',
            marker='s',
            elinewidth=0.5,
            capsize=4,
            capthick=1,
            color='black',
        )
        plt.ylabel('Value')
        plt.xlabel('Index')
        plt.tight_layout()

        if plot:
            plt.show()


class RepositoryNormalizer(ObjectContainer):
    """Data repository normalizer"""
    def __init__(self, normalizers=None, filename=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        normalizers : dict
            Normalizers in a dict to initialize the repository, key in the dictionary should be the label
            Default value None

        filename : str or dict
            Either one filename (str) or multiple filenames in a dictionary. Dictionary based parameter is used to
            construct the repository from separate Normalizer, format:
            label as key, and filename as value.
            Default value None

        """

        # Run super init to call init of mixins too
        super(RepositoryNormalizer, self).__init__(**kwargs)

        self.normalizers = {}

        if normalizers:
            if isinstance(normalizers, dict):
                self.normalizers = normalizers

            else:
                message = '{name}: Invalid type for normalizer_dict'.format(
                    name=self.__class__.__name__
                )
                self.logger.exception(message)
                raise ValueError(message)

        self.filename = filename

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, type, value, traceback):
        # Finalize accumulated calculation
        self.finalize()

    def __getitem__(self, label):
        return self.normalizers[label]

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

        output = super(RepositoryNormalizer, self).to_string(ui=ui, indent=indent)

        output += ui.data(
            indent=indent + 2,
            field='Labels',
            value=list(self.normalizers.keys())
        ) + '\n'

        output += ui.line(field='Content') + '\n'
        for label, label_data in iteritems(self.normalizers):
            if label_data:
                output += ui.data(
                    indent=indent + 2,
                    field='['+str(label)+']',
                    value=label_data
                ) + '\n'

        output += '\n'
        return output

    def __call__(self, *args, **kwargs):
        return self.normalize(*args, **kwargs)

    def reset(self):
        """Reset normalizers.
        """

        for label in self.normalizers:
            self.normalizers[label].reset()

    def load(self, filename, collect_from_containers=True):
        """Load normalizers from disk.


        Parameters
        ----------
        filename : str or dict
            Either one filename (str) or multiple filenames in a dictionary. Dictionary based parameter is used to
            construct the repository from separate Normalizer, format:
            label as key, and filename as value. If None given, parameter given to class initializer is used instead.
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

                super(RepositoryNormalizer, self).load(
                    filename=self.filename
                )

            if collect_from_containers:
                # Collect data to the repository from separate normalizer containers
                filename_base, file_extension = os.path.splitext(self.filename)
                normalizers = glob.glob(filename_base + '.*' + file_extension)
                for filename in normalizers:
                    label = os.path.splitext(filename)[0].split('.')[-1]
                    self.normalizers[label] = Normalizer().load(
                        filename=filename
                    )

        elif isinstance(self.filename, dict):
            sorted(self.filename)

            # Dictionary based filename given
            if filelist_exists(self.filename):
                self.normalizers = {}

                for label, data in iteritems(self.filename):
                    if not label.startswith('_'):
                        # Skip labels starting with '_', those are just for extra info
                        if isinstance(data, basestring):
                            # filename given directly, only one data stream per method inputted.
                            self.normalizers[label] = Normalizer().load(
                                filename=data
                            )
            else:
                # All filenames did not exists, find which ones is missing and raise error.
                for label, data in iteritems(self.filename):
                    if isinstance(data, basestring) and not os.path.isfile(data):
                        message = '{name}: RepositoryNormalizer cannot be loaded, file does not exists for method [{method}], file [{filename}]'.format(
                            name=self.__class__.__name__,
                            method=label,
                            filename=data
                        )
                        self.logger.exception(message)
                        raise IOError(message)

        else:
            message = '{name}: RepositoryNormalizer cannot be loaded, no valid filename set.'.format(
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
            Split data from repository separate normalizer containers and save them individually.
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
            for label in self.normalizers:
                if label not in filename_dictionary:
                    filename_dictionary[label] = {}

                filename_dictionary[label] = filename_base + '.' + label  + file_extension

            self.filename = filename_dictionary

        if isinstance(self.filename, basestring):
            # Single output file as target
            self.detect_file_format()
            self.validate_format()

            # String filename given use load method from parent class
            super(RepositoryNormalizer, self).save(
                filename=self.filename
            )

        elif isinstance(self.filename, dict):
            # Custom naming and splitting into separate normalizer containers
            sorted(self.filename)

            # Dictionary of filenames given, save each data normalizer in the repository separately
            for label in self.normalizers:
                if label in self.filename:
                    current_normalizer = self.normalizers[label]
                    current_normalizer.save(
                        filename=self.filename[label]
                    )

        return self

    def accumulate(self, data):
        """Accumulate statistics

        Parameters
        ----------
        data : DataRepository
            Data in DataRepository

        Returns
        -------
        self

        """

        for label_id, label in enumerate(data.labels):
            if label not in self.normalizers:
                # Label not yet encountered, initialize new normalizer for it
                self.normalizers[label] = Normalizer()

            # Loop through streams
            for stream_id in data.stream_ids(label=label):
                self.normalizers[label].accumulate(
                    data=data.get_container(
                        label=label,
                        stream_id=stream_id
                    )
                )

        return self

    def finalize(self):
        """Finalize statistics calculation

        Accumulated values are used to get mean and std for the seen data.

        Parameters
        ----------

        Returns
        -------
        self

        """

        for label in self.normalizers:
            self.normalizers[label].finalize()

        return self

    def normalize(self, data, **kwargs):
        """Normalize data repository

        Parameters
        ----------
        data : DataRepository
            DataRepository to be normalized

        Returns
        -------
        DataRepository

        """

        from dcase_util.containers import DataRepository

        # Make copy of data to prevent data contamination
        data = copy.deepcopy(data)

        if isinstance(data, DataRepository):
            for label_id, label in enumerate(data.labels):
                if label in self.normalizers:
                    for stream_id in data.stream_ids(label=label):
                        data.set_container(
                            label=label,
                            stream_id=stream_id,
                            container=self.normalizers[label].normalize(
                                data=data.get_container(
                                    label=label,
                                    stream_id=stream_id
                                )
                            )
                        )

        return data


class Aggregator(ObjectContainer):
    """Data aggregator"""
    valid_method = ['mean', 'std', 'cov', 'kurtosis', 'skew', 'flatten']

    def __init__(self, win_length_frames=10, hop_length_frames=1, recipe=None, center=True, padding=True, **kwargs):
        """Constructor

        Parameters
        ----------
        recipe : list of dict or list of str
            Aggregation recipe, supported methods [mean, std, cov, kurtosis, skew, flatten].
            Default value None

        win_length_frames : int
            Window length in data frames
            Default value 10

        hop_length_frames : int
            Hop length in data frames
            Default value 1

        center : bool
            Centering of the window
            Default value True

        padding : bool
            Padding of the first window with the first frame and last window with last frame to have equal
            length data in the windows.
            Default value True

        """

        # Run super init to call init of mixins too
        super(Aggregator, self).__init__(**kwargs)

        self.win_length_frames = win_length_frames
        self.hop_length_frames = hop_length_frames
        self.center = center
        self.padding = padding

        if recipe is None and kwargs.get('aggregation_recipe', None) is not None:
            recipe = kwargs.get('aggregation_recipe', None)

        if isinstance(recipe, dict):
            self.recipe = [d['label'] for d in recipe]

        elif isinstance(recipe, list):
            recipe = recipe

            if isinstance(recipe[0], dict):
                self.recipe = [d['label'] for d in recipe]

            else:
                self.recipe = recipe

        elif isinstance(recipe, six.string_types):
            recipe = VectorRecipeParser().parse(recipe=recipe)
            self.recipe = [d['label'] for d in recipe]

        else:
            message = '{name}: No valid recipe set'.format(
                name=self.__class__.__name__
            )
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

        output = super(Aggregator, self).to_string(ui=ui, indent=indent)

        output += ui.data(field='win_length_frames', value=self.win_length_frames, indent=indent) + '\n'
        output += ui.data(field='hop_length_frames', value=self.hop_length_frames, indent=indent) + '\n'
        output += ui.data(field='recipe', value=self.recipe, indent=indent) + '\n'

        return output

    def __getstate__(self):
        # Return only needed data for pickle
        return {
            'recipe': self.recipe,
            'win_length_frames': self.win_length_frames,
            'hop_length_frames': self.hop_length_frames,
        }

    def __setstate__(self, d):
        self.recipe = d['recipe']
        self.win_length_frames = d['win_length_frames']
        self.hop_length_frames = d['hop_length_frames']

    def __call__(self, *args, **kwargs):
        return self.aggregate(*args, **kwargs)

    def aggregate(self, data=None, **kwargs):
        """Aggregate data

        Parameters
        ----------
        data : DataContainer
            Features to be aggregated
            Default value None

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import DataContainer
        # Make copy of the data to prevent modifications to the original data
        data = copy.deepcopy(data)

        if isinstance(data, DataContainer):
            aggregated_data = []

            # Not the most efficient way as numpy stride_tricks would produce
            # faster code, however, opted for cleaner presentation this time.
            for frame in range(0, data.data.shape[data.time_axis], self.hop_length_frames):
                # Get start and end of the window
                if self.center:
                    # Keep frame at the middle (approximately)
                    start_frame = int(frame - numpy.floor(self.win_length_frames / 2.0))
                    end_frame = int(frame + numpy.ceil(self.win_length_frames / 2.0))
                else:
                    start_frame = frame
                    end_frame = frame + self.win_length_frames

                frame_ids = numpy.array(range(start_frame, end_frame))

                valid_frame = True
                if self.padding:
                    # If start of data matrix, pad with first frame
                    frame_ids[frame_ids < 0] = 0

                    # If end of the data matrix, pad with last frame
                    frame_ids[frame_ids > data.data.shape[data.time_axis] - 1] = data.data.shape[data.time_axis] - 1

                else:
                    # Mark non-full windows invalid
                    if numpy.any(frame_ids < 0) or numpy.any( frame_ids > data.data.shape[data.time_axis] - 1):
                        valid_frame = False

                if valid_frame:
                    current_frame = data.get_frames(frame_ids=frame_ids)

                    aggregated_frame = []

                    if 'mean' in self.recipe:
                        aggregated_frame.append(current_frame.mean(axis=data.time_axis))

                    if 'std' in self.recipe:
                        aggregated_frame.append(current_frame.std(axis=data.time_axis))

                    if 'cov' in self.recipe:
                        aggregated_frame.append(numpy.cov(current_frame).flatten())

                    if 'kurtosis' in self.recipe:
                        aggregated_frame.append(scipy.stats.kurtosis(current_frame, axis=data.time_axis))

                    if 'skew' in self.recipe:
                        aggregated_frame.append(scipy.stats.skew(current_frame, axis=data.time_axis))

                    if 'flatten' in self.recipe:
                        if data.time_axis == 0:
                            aggregated_frame.append(current_frame.flatten())
                        elif data.time_axis == 1:
                            aggregated_frame.append(current_frame.T.flatten().T)

                    if aggregated_frame:
                        aggregated_data.append(numpy.concatenate(aggregated_frame))

            if aggregated_data:
                # Update data
                data.data = numpy.vstack(aggregated_data).T

            else:
                message = '{name}: No aggregated data, check your aggregation recipe.'.format(
                    name=self.__class__.__name__,
                )
                self.logger.exception(message)
                raise ValueError(message)

            # Update meta data
            if hasattr(data, 'hop_length_seconds') and data.hop_length_seconds is not None:
                data.hop_length_seconds = self.hop_length_frames * data.hop_length_seconds

            return data

        else:
            message = '{name}: Unknown data container type.'.format(
                name=self.__class__.__name__,
            )
            self.logger.exception(message)
            raise ValueError(message)


class Sequencer(ObjectContainer):
    """Data sequencer"""

    def __init__(self, sequence_length=10, hop_length=None,
                 padding=None,
                 shift_border='roll', shift=0,
                 required_data_amount_per_segment=0.9,
                 **kwargs):
        """__init__ method.

        Parameters
        ----------
        sequence_length : int
            Sequence length
            Default value 10

        hop_length : int
            Hop value of when forming the sequence, if None then hop length equals to sequence_length (non-overlapping sequences).
            Default value None

        padding: str
            How data is treated at the boundaries [None, 'zero', 'repeat']
            Default value None

        shift_border : string, ['roll', 'shift']
            Sequence border handling when doing temporal shifting.
            Default value roll

        shift : int
            Sequencing grid shift.
            Default value 0

        required_data_amount_per_segment : float [0,1]
            Percentage of valid data items per segment there need to be for valid segment. Use this parameter to
            filter out part of the non-full segments.
            Default value 0.9

        """

        # Run super init to call init of mixins too
        super(Sequencer, self).__init__(**kwargs)

        self.sequence_length = sequence_length

        if hop_length is None:
            self.hop_length = self.sequence_length

        else:
            self.hop_length = hop_length

        # Padding
        if padding in [None, False, 'zero', 'repeat']:
            self.padding = padding

        else:
            message = '{name}: Unknown padding mode [{padding_mode}]'.format(
                name=self.__class__.__name__,
                padding_mode=padding
            )
            self.logger.exception(message)
            raise ValueError(message)

        # Shifting
        self.shift = shift

        if shift_border in ['roll', 'shift']:
            self.shift_border = shift_border

        else:
            message = '{name}: Unknown temporal shifting border handling [{border_mode}]'.format(
                name=self.__class__.__name__,
                border_mode=self.shift_border
            )
            self.logger.exception(message)
            raise ValueError(message)

        self.required_data_amount_per_segment = required_data_amount_per_segment

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

        output = super(Sequencer, self).to_string(ui=ui, indent=indent)

        output += ui.data(field='frames', value=self.sequence_length, indent=indent) + '\n'
        output += ui.data(field='hop_length_frames', value=self.hop_length, indent=indent) + '\n'
        output += ui.data(field='padding', value=self.padding, indent=indent) + '\n'
        output += ui.data(field='required_data_amount_per_segment', value=self.required_data_amount_per_segment, indent=indent) + '\n'
        output += ui.line(field='Shifting', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='shift', value=self.shift) + '\n'
        output += ui.data(indent=indent + 2, field='shift_border', value=self.shift_border) + '\n'

        return output

    def __getstate__(self):
        # Return only needed data for pickle
        return {
            'frames': self.sequence_length,
            'hop_length_frames': self.hop_length,
            'padding': self.padding,
            'shift': self.shift,
            'shift_border': self.shift_border,
            'required_data_amount_per_segment': self.required_data_amount_per_segment,
        }

    def __setstate__(self, d):
        self.sequence_length = d['frames']
        self.hop_length = d['hop_length_frames']
        self.padding = d['padding']
        self.shift = d['shift']
        self.shift_border = d['shift_border']
        self.required_data_amount_per_segment = d['required_data_amount_per_segment']

    def __call__(self, *args, **kwargs):
        return self.sequence(*args, **kwargs)

    def sequence(self, data, shift=None, **kwargs):
        """Convert 2D data matrix into sequence of specified length 2D matrices

        Parameters
        ----------
        data : DataContainer or numpy.ndarray
            Data

        shift : int
            Sequencing grid shift in frames. If none given, one given for class initializer is used.
            Value is kept inside data size. Parameter value is stored as new class stored value.
            Default value None

        Returns
        -------
        DataMatrix3DContainer

        """

        if shift:
            self.shift = shift

        from dcase_util.containers import DataContainer, DataMatrix2DContainer, DataMatrix3DContainer
        # Make copy of the data to prevent modifications to the original data
        data = copy.deepcopy(data)

        if isinstance(data, numpy.ndarray):
            if len(data.shape) == 2:
                data = DataMatrix2DContainer(data)

        if isinstance(data, DataContainer):
            # Make sure shift index is withing data
            self.shift = self.shift % data.length

            # Not the most efficient way as numpy stride_tricks would produce
            # faster code, however, opted for cleaner presentation this time.
            processed_data = []

            if self.shift_border == 'shift':
                segment_indexes = numpy.arange(self.shift, data.length, self.hop_length)

            elif self.shift_border == 'roll':
                segment_indexes = numpy.arange(0, data.length, self.hop_length)

                if self.shift != 0:
                    # Roll data
                    data.data = numpy.roll(
                        data.data,
                        shift=-self.shift,
                        axis=data.time_axis
                    )

            else:
                message = '{name}: Unknown type for sequence border handling when doing temporal shifting ' \
                          '[{shift_border}].'.format(
                    name=self.__class__.__name__,
                    shift_border=self.shift_border
                )

                self.logger.exception(message)
                raise ValueError(message)

            if self.padding:
                if len(segment_indexes) == 0:
                    # Have at least one segment
                    segment_indexes = numpy.array([0])

            else:
                # Remove segments which are not full
                segment_indexes = segment_indexes[(segment_indexes + self.sequence_length - 1) < data.length]

            for segment_start_frame in segment_indexes:
                segment_end_frame = segment_start_frame + self.sequence_length

                frame_ids = numpy.array(range(segment_start_frame, segment_end_frame))

                valid_frames = numpy.where(numpy.logical_and(frame_ids >= 0, frame_ids < data.length))[0]

                if len(valid_frames) / float(self.sequence_length) > self.required_data_amount_per_segment:
                    # Process segment only if it has minimum about of valid frames

                    if self.padding == 'repeat':
                        # Handle boundaries with repeated boundary vectors

                        # If start of matrix, pad with first frame
                        frame_ids[frame_ids < 0] = 0

                        # If end of the matrix, pad with last frame
                        frame_ids[frame_ids > data.length - 1] = data.length - 1

                        # Append the segment
                        processed_data.append(
                            data.get_frames(
                                frame_ids=frame_ids
                            )
                        )

                    elif self.padding == 'zero':
                        # Handle boundaries with zero padding

                        # Initialize current segment with zero content
                        current_segment = numpy.zeros((data.vector_length, self.sequence_length))

                        # Copy data into correct position within the segment
                        current_segment[:, valid_frames] = data.get_frames(
                            frame_ids=frame_ids[valid_frames]
                        )

                        # Append the segment
                        processed_data.append(current_segment)

                    else:
                        # Append the segment
                        processed_data.append(data.get_frames(frame_ids=frame_ids))

            if len(processed_data) == 0:
                message = '{name}: Cannot create valid segment, adjust segment length and hop size, or use ' \
                          'padding flag.'.format(name=self.__class__.__name__)

                self.logger.exception(message)
                raise IOError(message)

            return DataMatrix3DContainer(
                data=numpy.moveaxis(numpy.array(processed_data), 0, 2),
                time_resolution=None,
                processing_chain=data.processing_chain
            )

        else:
            message = '{name}: Unknown data container type.'.format(
                name=self.__class__.__name__,
            )
            self.logger.exception(message)
            raise ValueError(message)

    def increase_shifting(self, shift_step=1):
        """Increase temporal shifting

        Parameters
        ----------
        shift_step : int
            Amount to be added to the sequencing grid
            Default value 1

        Returns
        -------
        self

        """

        if shift_step:
            self.shift += shift_step

        return self


class Stacker(ObjectContainer):
    """Data stacker"""

    def __init__(self, recipe=None, hop=1, **kwargs):
        """Constructor

        Parameters
        ----------
        recipe : dict or str
            Stacking recipe
            Default value None

        hop : int, optional
            Data item hopping
            Default value 1

        """

        # Run super init to call init of mixins too
        super(Stacker, self).__init__(**kwargs)

        if isinstance(recipe, str):
            from dcase_util.utils import VectorRecipeParser
            self.recipe = VectorRecipeParser().parse(recipe=recipe)

        elif isinstance(recipe, list):
            self.recipe = recipe

        else:
            message = '{name}: No recipe set'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        self.hop = hop

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

        output = super(Stacker, self).to_string(ui=ui, indent=indent)

        output += ui.data(field='recipe', value=self.recipe, indent=indent) + '\n'
        output += ui.data(field='hop', value=self.hop, indent=indent) + '\n'

        return output

    def __getstate__(self):
        return {
            'recipe': self.recipe,
            'hop': self.hop,
        }

    def __setstate__(self, d):
        self.recipe = d['recipe']
        self.hop = d['hop']

    def __call__(self, *args, **kwargs):
        return self.stack(*args, **kwargs)

    def stack(self, repository, **kwargs):
        """Vector creation based on recipe

        Parameters
        ----------
        repository : RepositoryContainer
            Repository with needed data

        Returns
        -------
        FeatureContainer

        """

        # Check that all data matrices have same amount of frames
        frame_count = []
        time_resolution = []
        for recipe_part in self.recipe:
            label = recipe_part['label']
            stream_id = 0  # Default value
            if 'vector-index' in recipe_part:
                stream_id = recipe_part['vector-index']['stream']

            if repository.get_container(label=label, stream_id=stream_id).time_resolution:
                time_resolution.append(
                    repository.get_container(
                        label=label,
                        stream_id=stream_id
                    ).time_resolution
                )

            frame_count.append(
                repository.get_container(
                    label=label,
                    stream_id=stream_id
                ).length
            )

        if len(set(frame_count)) != 1:
            message = '{name}: Data matrices should have same number of frames {frame_count}'.format(
                name=self.__class__.__name__,
                frame_count=frame_count,
            )

            self.logger.exception(message)
            raise AssertionError(message)

        if len(set(time_resolution)) != 1:
            message = '{name}: Data matrices should have same time resolution {time_resolution}'.format(
                name=self.__class__.__name__,
                time_resolution=time_resolution,
            )

            self.logger.exception(message)
            raise AssertionError(message)

        # Stack data
        data_matrix = []
        for recipe_part in self.recipe:
            label = recipe_part['label']

            # Default values
            stream_id = 0
            if 'vector-index' in recipe_part:
                stream_id = recipe_part['vector-index']['stream']

            if ('vector-index' not in recipe_part or
               ('vector-index' in recipe_part and 'full' in recipe_part['vector-index'] and recipe_part['vector-index']['full'])):

                # Full matrix
                data_matrix.append(
                    repository.get_container(
                        label=label,
                        stream_id=stream_id
                    ).get_frames(
                        frame_hop=self.hop
                    )
                )

            elif ('vector-index' in recipe_part and
                  'vector' in recipe_part['vector-index'] and
                  'selection' in recipe_part['vector-index'] and recipe_part['vector-index']['selection']):

                index = numpy.array(recipe_part['vector-index']['vector'])

                # Selector vector
                data_matrix.append(
                    repository.get_container(
                        label=label,
                        stream_id=stream_id
                    ).get_frames(
                        vector_ids=index,
                        frame_hop=self.hop
                    )
                )

            elif ('vector-index' in recipe_part and
                  'start' in recipe_part['vector-index'] and
                  'stop' in recipe_part['vector-index']):

                index = numpy.arange(recipe_part['vector-index']['start'], recipe_part['vector-index']['stop'])

                # Start and end index
                data_matrix.append(
                    repository.get_container(
                        label=label,
                        stream_id=stream_id
                    ).get_frames(
                        vector_ids=index,
                        frame_hop=self.hop
                    )
                )

        from dcase_util.containers import FeatureContainer

        return FeatureContainer(
            data=numpy.vstack(data_matrix),
            time_resolution=time_resolution[0],
            processing_chain=repository.processing_chain
        )


class Selector(ObjectContainer):
    """Data selector"""

    def __init__(self, **kwargs):
        """Constructor

        Parameters
        ----------
        time_resolution : float
            Hop length in seconds

        """

        super(Selector, self).__init__(**kwargs)

        # Initialize selection mask events
        from dcase_util.containers import MetaDataContainer
        self.selection_events = MetaDataContainer()

    def __getstate__(self):
        # Return only needed data for pickle
        return {}

    def __setstate__(self, d):
        from dcase_util.containers import MetaDataContainer
        self.selection_events = MetaDataContainer()

    def __call__(self, *args, **kwargs):
        return self.select(*args, **kwargs)

    def set_mask(self, mask_events):
        """Set masking events

        Parameters
        ----------
        mask_events : list of MetaItems or MetaDataContainer
            Event list used for selecting

        """

        self.selection_events = mask_events
        return self

    def select(self, data, selection_events=None):
        """Selecting data repository with given events

        Parameters
        ----------
        data : DataRepository
            Data repository to be masked.

        selection_events : list of MetaItems or MetaDataContainer
            Event list used for selecting
            Default value None

        Returns
        -------
        DataRepository

        """

        if selection_events is None:
            selection_events = self.selection_events

        for label in data.labels:
            for stream_id in data.stream_ids(label):
                current_container = data.get_container(label=label, stream_id=stream_id)

                selection_mask = numpy.zeros((current_container.length), dtype=bool)
                for select_event in selection_events:
                    onset_frame = current_container._time_to_frame(select_event.onset, rounding_direction='floor')
                    offset_frame = current_container._time_to_frame(select_event.offset, rounding_direction='ceil')

                    if offset_frame > current_container.length:
                        offset_frame = current_container.length

                    selection_mask[onset_frame:offset_frame] = True

                current_container.data = current_container.get_frames(frame_ids=numpy.where(selection_mask == True)[0])

        return data


class Masker(ObjectContainer):
    """Data masker"""

    def __init__(self, **kwargs):
        """Constructor

        Parameters
        ----------
        time_resolution : float
            Hop length in seconds

        """

        super(Masker, self).__init__(**kwargs)

        # Initialize mask events
        from dcase_util.containers import MetaDataContainer
        self.mask_events = MetaDataContainer()

    def __getstate__(self):
        # Return only needed data for pickle
        return {}

    def __setstate__(self, d):
        from dcase_util.containers import MetaDataContainer
        self.mask_events = MetaDataContainer()

    def __call__(self, *args, **kwargs):
        return self.mask(*args, **kwargs)

    def set_mask(self, mask_events):
        """Set masking events

        Parameters
        ----------
        mask_events : list of MetaItems or MetaDataContainer
            Event list used for masking

        """

        self.mask_events = mask_events
        return self

    def mask(self, data, mask_events=None):
        """Masking data repository with given events

        Parameters
        ----------
        data : DataRepository
            Data repository to be masked.

        mask_events : list of MetaItems or MetaDataContainer
            Event list used for masking
            Default value None

        Returns
        -------
        DataRepository

        """

        if mask_events is None:
            mask_events = self.mask_events

        for label in data.labels:
            for stream_id in data.stream_ids(label):
                current_container = data.get_container(label=label, stream_id=stream_id)

                removal_mask = numpy.ones((current_container.length), dtype=bool)
                for mask_event in mask_events:
                    onset_frame = current_container._time_to_frame(mask_event.onset, rounding_direction='floor')
                    offset_frame = current_container._time_to_frame(mask_event.offset, rounding_direction='ceil')

                    if offset_frame > current_container.length:
                        offset_frame = current_container.length

                    removal_mask[onset_frame:offset_frame] = False

                current_container.data = current_container.get_frames(frame_ids=numpy.where(removal_mask == True)[0])

        return data
