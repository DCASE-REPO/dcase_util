#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import numpy
import scipy

from dcase_util.containers import DataContainer, ObjectContainer
from dcase_util.ui import FancyStringifier


class Normalizer(ObjectContainer):
    """Data normalizer to accumulate data statistics"""

    def __init__(self, n=None, s1=None, s2=None, mean=None, std=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        n : int
            Item count used to calculate statistics

        s1 : np.array [shape=(vector_length,)]
            Vector-wise sum of the data seen by the Normalizer

        s2 : np.array [shape=(vector_length,)]
            Vector-wise sum^2 of the data seen by the Normalizer

        mean : np.ndarray() [shape=(vector_length, 1)]
            Mean of the data

        std : np.ndarray() [shape=(vector_length, 1)]
            Standard deviation of the data

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

    def __str__(self):
        ui = FancyStringifier()

        output = super(Normalizer, self).__str__()

        output += ui.data(field='Mean', value=self.mean) + '\n'
        output += ui.data(field='Std', value=self.std) + '\n'

        output += ui.data(field='n', value=self.n) + '\n'

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

        Returns
        -------
        nothing

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

        Accumulated values are used to get mean and std for the seen feature data.

        Parameters
        ----------

        Returns
        -------
        None

        """

        self._mean = (self.s1 / self.n).reshape(-1, 1)
        self._std = numpy.sqrt((self.n * self.s2 - (self.s1 * self.s1)) / (self.n * (self.n - 1))).reshape(-1, 1)

        return self

    def normalize(self, data):
        """Normalize feature matrix with internal statistics of the class

        Parameters
        ----------
        data : DataContainer or np.ndarray
            DataContainer or np.ndarray to be normalized

        Returns
        -------
        DataContainer or numpy.ndarray [shape=(frames, number of feature values)]
            Normalized data matrix

        """
        from dcase_util.containers import DataContainer

        if isinstance(data, DataContainer):
            data.data = (data.data - self.mean) / self.std

            if hasattr(self, 'get_processing_chain_item'):
                data.processing_chain.push_processor(**self.get_processing_chain_item())

            return data

        elif isinstance(data, numpy.ndarray):
            return (data - self.mean) / self.std


class RepositoryNormalizer(ObjectContainer):
    """Data repository normalizer"""
    def __init__(self, normalizer_dict=None, filename_dict=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        normalizer_dict : dict
            Normalizers in a dict, key should be the label used in the repository.

        filename_dict : dict
            Filenames of Normalizers, key should be the label used in the repository.

        """

        # Run super init to call init of mixins too
        super(RepositoryNormalizer, self).__init__(**kwargs)

        self.normalizer_dict = {}

        if normalizer_dict:
            self.normalizer_dict = normalizer_dict

        if filename_dict:
            self.load(filename_dict=filename_dict)

    def load(self, filename_dict):
        """Load normalizers from disk.

        Parameters
        ----------
        filename_dict : dict
            Filenames of Normalizers, key should be the label used in the repository.

        Returns
        -------
        self

        """

        self.normalizer_dict = {}
        for label, filename in iteritems(filename_dict):
            self.normalizer_dict[label] = Normalizer().load(filename=filename)

        return self

    def normalize(self, data_repository):
        """Normalize data repository

        Parameters
        ----------
        data_repository : DataRepository
            DataRepository to be normalized

        Returns
        -------
        DataRepository
            Normalized data

        """
        from dcase_util.containers import DataRepository

        if isinstance(data_repository, DataRepository):
            for label_id, label in enumerate(data_repository.labels):
                if label in self.normalizer_dict:
                    for stream_id in data_repository.stream_ids(label=label):
                        self.normalizer_dict[label].normalize(
                            data=data_repository.get_container(label=label, stream_id=stream_id)
                        )

        return data_repository


class Aggregator(ObjectContainer):
    """Data aggregator"""
    valid_method = ['mean', 'std', 'cov', 'kurtosis', 'skew', 'flatten']

    def __init__(self, win_length_frames=10, hop_length_frames=1, recipe=None, **kwargs):
        """Constructor

        Parameters
        ----------
        recipe : list of dict or list of str
            Aggregation recipe, supported methods [mean, std, cov, kurtosis, skew, flatten].

        win_length_frames : int
            Window length in feature frames

        hop_length_frames : int
            Hop length in feature frames

        """

        # Run super init to call init of mixins too
        super(Aggregator, self).__init__(**kwargs)

        self.win_length_frames = win_length_frames
        self.hop_length_frames = hop_length_frames

        if isinstance(recipe, dict):
            self.recipe = [d['label'] for d in recipe]

        elif isinstance(recipe, list):
            recipe = recipe

            if isinstance(recipe[0], dict):
                self.recipe = [d['label'] for d in recipe]

            else:
                self.recipe = recipe

        else:
            self.recipe = None

    def __str__(self):
        ui = FancyStringifier()
        output = super(Aggregator, self).__str__()
        output += ui.data(field='win_length_frames', value=self.win_length_frames) + '\n'
        output += ui.data(field='hop_length_frames', value=self.hop_length_frames) + '\n'
        output += ui.data(field='recipe', value=self.recipe) + '\n'

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

    def aggregate(self, data=None, **kwargs):
        """Aggregate data

        Parameters
        ----------
        data : DataContainer
            Features to be aggregated

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import DataContainer

        if isinstance(data, DataContainer):
            aggregated_features = []

            # Not the most efficient way as numpy stride_tricks would produce
            # faster code, however, opted for cleaner presentation this time.
            for frame in range(0, data.data.shape[data.time_axis], self.hop_length_frames):
                # Get start and end of the window, keep frame at the middle (approximately)
                start_frame = int(frame - numpy.floor(self.win_length_frames/2.0))
                end_frame = int(frame + numpy.ceil(self.win_length_frames / 2.0))

                frame_ids = numpy.array(range(start_frame, end_frame))
                # If start of feature matrix, pad with first frame
                frame_ids[frame_ids < 0] = 0

                # If end of the feature matrix, pad with last frame
                frame_ids[frame_ids > data.data.shape[data.time_axis] - 1] = data.data.shape[data.time_axis] - 1

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
                    aggregated_features.append(numpy.concatenate(aggregated_frame))

            # Update data
            data.data = numpy.vstack(aggregated_features).T

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

    def __init__(self, frames=10, hop_length_frames=None, padding=False, shift_step=0,
                 shift_border='roll', shift_max=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        frames : int
            Sequence length

        hop_length_frames : int
            Hop value of when forming the sequence, if None then hop length equals to frames (non-overlapping hopping).

        padding: bool
            Replicate data when sequence is not full

        shift_step : int
            Sequence start temporal shifting amount, is added once method increase_shifting is called

        shift_border : string, {'roll', 'shift'}
            Sequence border handling when doing temporal shifting.

        shift_max : int
            Maximum value for temporal shift

        """

        # Run super init to call init of mixins too
        super(Sequencer, self).__init__(**kwargs)

        self.frames = frames

        if hop_length_frames is None:
            self.hop_length_frames = self.frames

        else:
            self.hop_length_frames = hop_length_frames

        self.padding = padding
        self.shift = 0

        self.shift_step = shift_step

        if shift_border in ['roll', 'shift']:
            self.shift_border = shift_border

        else:
            message = '{name}: Unknown temporal shifting border handling [{border_mode}]'.format(
                name=self.__class__.__name__,
                border_mode=self.shift_border
            )
            self.logger.exception(message)
            raise ValueError(message)

        self.shift_max = shift_max

    def __str__(self):
        ui = FancyStringifier()

        output = super(Sequencer, self).__str__()
        output += ui.data(field='frames', value=self.frames) + '\n'
        output += ui.data(field='hop_length_frames', value=self.hop_length_frames) + '\n'
        output += ui.data(field='padding', value=self.padding) + '\n'

        output += ui.line(field='Shifting') + '\n'
        output += ui.data(indent=4, field='shift', value=self.shift) + '\n'
        output += ui.data(indent=4, field='shift_step', value=self.shift_step) + '\n'
        output += ui.data(indent=4, field='shift_border', value=self.shift_border) + '\n'
        output += ui.data(indent=4, field='shift_max', value=self.shift_max) + '\n'

        return output

    def __getstate__(self):
        # Return only needed data for pickle
        return {
            'frames': self.frames,
            'hop_length_frames': self.hop_length_frames,
            'padding': self.padding,
            'shift': self.shift,
            'shift_step': self.shift_step,
            'shift_border': self.shift_border,
            'shift_max': self.shift_max,
        }

    def __setstate__(self, d):
        self.frames = d['frames']
        self.hop_length_frames = d['hop_length_frames']
        self.padding = d['padding']
        self.shift = d['shift']
        self.shift_step = d['shift_step']
        self.shift_border = d['shift_border']
        self.shift_max = d['shift_max']

    def sequence(self, data=None, **kwargs):
        """Make sequences

        Parameters
        ----------
        data : DataContainer
            Data

        Returns
        -------
        DataMatrix3DContainer

        """

        from dcase_util.containers import DataContainer, DataMatrix3DContainer

        if isinstance(data, DataContainer):

            # Not the most efficient way as numpy stride_tricks would produce
            # faster code, however, opted for cleaner presentation this time.
            data_length = data.length
            processed_data = []

            if self.shift_border == 'shift':
                segment_indexes = numpy.arange(self.shift, data.length, self.hop_length_frames)

            elif self.shift_border == 'roll':
                segment_indexes = numpy.arange(0, data.length, self.hop_length_frames)

                if self.shift:
                    # Roll data
                    data.data = numpy.roll(
                        data.data,
                        shift=self.shift,
                        axis=data.time_axis
                    )

            else:
                message = '{name}: Unknown type for sequence border handling when doing temporal shifting [{shift_border}].'.format(
                    name=self.__class__.__name__,
                    shift_border=self.shift_border,
                )

                self.logger.exception(message)
                raise IOError(message)

            if self.padding:
                if len(segment_indexes) == 0:
                    # Have at least one segment
                    segment_indexes = numpy.array([0])
            else:
                # Remove segments which are not full
                segment_indexes = segment_indexes[(segment_indexes+self.hop_length_frames-1) < data.length]

            for segment_start_frame in segment_indexes:
                segment_end_frame = segment_start_frame + self.hop_length_frames

                frame_ids = numpy.array(range(segment_start_frame, segment_end_frame))

                if self.padding:
                    # If start of matrix, pad with first frame
                    frame_ids[frame_ids < 0] = 0

                    # If end of the matrix, pad with last frame
                    frame_ids[frame_ids > data.length - 1] = data.length - 1

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

    def increase_shifting(self, shift_step=None):
        """Increase temporal shifting

        Parameters
        ----------
        shift_step : int
            Optional value, if none given shift_step parameter given for init is used.

        Returns
        -------
        self

        """

        if shift_step is None:
            shift_step = self.shift_step
        self.shift += shift_step

        if self.shift_max and self.shift > self.shift_max:
            self.shift = 0

        return self


class Stacker(ObjectContainer):
    """Data stacker"""

    def __init__(self, recipe=None, hop=1, **kwargs):
        """Constructor

        Parameters
        ----------
        recipe : dict or str
            Stacking recipe

        hop : int, optional
            Data item hopping

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

    def __str__(self):
        ui = FancyStringifier()

        output = super(Stacker, self).__str__()
        output += ui.data(field='recipe', value=self.recipe) + '\n'
        output += ui.data(field='hop', value=self.hop) + '\n'

        return output

    def __getstate__(self):
        return {
            'recipe': self.recipe,
            'hop': self.hop,
        }

    def __setstate__(self, d):
        self.recipe = d['recipe']
        self.hop = d['hop']

    def stack(self, repository):
        """Vector creation based on recipe

        Parameters
        ----------
        repository : RepositoryContainer
            Repository with needed data

        Returns
        -------
        FeatureContainer

        """

        # Check that all feature matrices have same amount of frames
        frame_count = []
        time_resolution = []
        for recipe_part in self.recipe:
            label = recipe_part['label']
            stream_id = 0  # Default value
            if 'vector-index' in recipe_part:
                stream_id = recipe_part['vector-index']['stream']

            if repository.get_container(label=label, stream_id=stream_id).time_resolution:
                time_resolution.append(repository.get_container(label=label, stream_id=stream_id).time_resolution)

            frame_count.append(repository.get_container(label=label, stream_id=stream_id).length)

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
                    repository.get_container(label=label, stream_id=stream_id).get_frames(frame_hop=self.hop)
                )

            elif ('vector-index' in recipe_part and
                  'vector' in recipe_part['vector-index'] and
                  'selection' in recipe_part['vector-index'] and recipe_part['vector-index']['selection']):

                index = numpy.array(recipe_part['vector-index']['vector'])

                # Selector vector
                data_matrix.append(
                    repository.get_container(label=label, stream_id=stream_id).get_frames(vector_ids=index, frame_hop=self.hop)
                )

            elif ('vector-index' in recipe_part and
                  'start' in recipe_part['vector-index'] and
                  'stop' in recipe_part['vector-index']):

                index = numpy.arange(recipe_part['vector-index']['start'], recipe_part['vector-index']['stop'])

                # Start and end index
                data_matrix.append(
                    repository.get_container(label=label, stream_id=stream_id).get_frames(vector_ids=index, frame_hop=self.hop)
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
        """Selecting feature repository with given events 

        Parameters
        ----------
        data : DataRepository
            Data repository to be masked.

        selection_events : list of MetaItems or MetaDataContainer
            Event list used for selecting

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
        """Masking feature repository with given events

        Parameters
        ----------
        data : DataRepository
            Data repository to be masked.

        mask_events : list of MetaItems or MetaDataContainer
            Event list used for masking

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
