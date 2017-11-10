#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import numpy

from dcase_util.containers import DataContainer
from dcase_util.processors import ProcessorMixin, ProcessingChainItemType, ProcessingChain
from dcase_util.data import Normalizer, Aggregator, Sequencer, Stacker, OneHotEncoder, ManyHotEncoder, \
    EventRollEncoder, Masker


class AggregationProcessor(Aggregator, ProcessorMixin):
    """Data aggregation processor"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

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

        kwargs.update(
            {
                'win_length_frames': win_length_frames,
                'hop_length_frames': hop_length_frames,
                'recipe': recipe
            }
        )
        
        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(AggregationProcessor, self).__init__(**kwargs)

    def process(self, data=None, **kwargs):
        """Process features

        Parameters
        ----------
        data : DataContainer
            Data to be aggregated

        Returns
        -------
        DataContainer

        """
        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            data = self.aggregate(data=data, **kwargs)

            # Update processing chain
            if hasattr(data, 'processing_chain') and hasattr(data.processing_chain, 'push_processor'):
                data.processing_chain.push_processor(**self.get_processing_chain_item())

            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class SequencingProcessor(Sequencer, ProcessorMixin):
    """Data sequencing processor"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, frames=10, hop_length_frames=None, padding=False, shift_step=0,
                 shift_border='roll', shift_max=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        frames : int
            Sequence length

        hop_length_frames : int
            Hop value of when forming the sequence

        padding: bool
            Replicate data when sequence is not full

        shift_step : int
            Sequence start temporal shifting amount, is added once method increase_shifting is called

        shift_border : string, {'roll', 'shift'}
            Sequence border handling when doing temporal shifting.

        shift_max : int
            Maximum value for temporal shift

        """

        kwargs.update(
            {
                'frames': frames,
                'hop_length_frames': hop_length_frames,
                'padding': padding,
                'shift_step': shift_step,
                'shift_border': shift_border,
                'shift_max': shift_max
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(SequencingProcessor, self).__init__(**kwargs)

    def process(self, data=None, **kwargs):
        """Process

        Parameters
        ----------
        data : DataContainer
            Data

        Returns
        -------
        DataMatrix3DContainer

        """
        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            container = self.sequence(data=data, **kwargs)
            container.processing_chain.push_processor(**self.get_processing_chain_item())

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class NormalizationProcessor(Normalizer, ProcessorMixin):
    """Data normalizer to accumulate data statistics"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, n=None, s1=None, s2=None, mean=None, std=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        n : int
            Item count used to calculate statistics

        s1 : numpy.array [shape=(vector_length,)]
            Vector-wise sum of the data seen by the Normalizer

        s2 : numpy.array [shape=(vector_length,)]
            Vector-wise sum^2 of the data seen by the Normalizer

        mean : numpy.ndarray() [shape=(vector_length, 1)]
            Mean of the data

        std : numpy.ndarray() [shape=(vector_length, 1)]
            Standard deviation of the data

        """

        kwargs.update(
            {
                'n': n,
                's1': s1,
                's2': s2,
                'mean': mean,
                'std': std
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(NormalizationProcessor, self).__init__(**kwargs)

    def process(self, data=None, **kwargs):
        """Normalize feature matrix with internal statistics of the class

        Parameters
        ----------
        data : DataContainer or numpy.ndarray
            DataContainer or numpy.ndarray to be normalized

        Returns
        -------
        DataContainer or numpy.ndarray [shape=(frames, number of feature values)]
            Normalized data matrix

        """

        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            return self.normalize(data=data)

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryNormalizationProcessor(DataContainer, ProcessorMixin):
    """Data normalizer to accumulate data statistics inside repository"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY
    output_type = ProcessingChainItemType.DATA_REPOSITORY

    def __init__(self, parameters=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        parameters : dict
            Pre-calculated statistics in dict to initialize internal state

        """

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(RepositoryNormalizationProcessor, self).__init__(**kwargs)

        if parameters is None:
            parameters = {}

        self.parameters = parameters

    def __getstate__(self):
        d = super(RepositoryNormalizationProcessor, self).__getstate__()
        d.update(
            {
                'parameters': self.parameters,
            }
        )
        return d

    def __setstate__(self, d):
        super(RepositoryNormalizationProcessor, self).__setstate__(d)
        self.parameters = d['parameters']

    def process(self, data=None, **kwargs):
        """Normalize data repository with internal statistics

        Parameters
        ----------
        data : DataRepository
            DataRepository

        Returns
        -------
        DataRepository

        """

        from dcase_util.containers import RepositoryContainer

        if isinstance(data, RepositoryContainer):
            for label, parameters in iteritems(self.parameters):
                if label in data:
                    # Label exists in data repository

                    if 'mean' in parameters and 'std' in parameters:
                        # Normalization statistics are present, use same statistics for all streams
                        for stream, stream_data in iteritems(data[label]):
                            # Normalize

                            # Make sure mean and std are numpy.array
                            if isinstance(parameters['mean'], list):
                                parameters['mean'] = numpy.array(parameters['mean'])
                            if isinstance(parameters['std'], list):
                                parameters['std'] = numpy.array(parameters['std'])

                            # Make sure mean and std has correct shape
                            if isinstance(parameters['mean'], numpy.ndarray) and len(parameters['mean'].shape) == 1:
                                parameters['mean'] = parameters['mean'].reshape((-1, 1))

                            if isinstance(parameters['std'], numpy.ndarray) and len(parameters['std'].shape) == 1:
                                parameters['std'] = parameters['std'].reshape((-1, 1))

                            stream_data.data = (stream_data.data - parameters['mean']) / parameters['std']

                    elif isinstance(parameters, dict):
                        # Most likely we have normalization statistics per stream
                        pass

            data.processing_chain.push_processor(**self.get_processing_chain_item())
            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class StackingProcessor(Stacker, ProcessorMixin):
    """Data stacking processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, recipe=None, hop=1, **kwargs):
        """Constructor

        Parameters
        ----------
        recipe : dict or str
            Stacking recipe

        hop : int, optional
            Feature hopping

        """

        kwargs.update(
            {
                'recipe': recipe,
                'hop': hop
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(StackingProcessor, self).__init__(**kwargs)

    def process(self, data=None, **kwargs):
        """Vector creation based on recipe

        Parameters
        ----------
        data : RepositoryContainer
            Repository with needed data

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import RepositoryContainer

        if isinstance(data, RepositoryContainer):
            container = self.stack(repository=data)

            container.processing_chain.push_processor(
                **self.get_processing_chain_item()
            )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryMaskingProcessor(Masker, ProcessorMixin):
    """Data masking processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

    def __init__(self, **kwargs):
        """Constructor
        """

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(RepositoryMaskingProcessor, self).__init__(**kwargs)

    def process(self, data, mask_events=None, **kwargs):
        """Vector creation based on recipe

        Parameters
        ----------
        data : RepositoryContainer
            Repository with needed data

        mask_events : MetaDaaContainer
            Masking events

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import RepositoryContainer

        if isinstance(data, RepositoryContainer):
            container = self.mask(
                data=data,
                mask_events=mask_events
            )

            container.processing_chain.push_processor(
                **self.get_processing_chain_item()
            )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class OneHotEncodingProcessor(OneHotEncoder, ProcessorMixin):
    """Event roll encoding processor"""
    input_type = ProcessingChainItemType.METADATA  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label_list=None, focus_field='scene_label', time_resolution=None,
                 length_frames=None, length_seconds=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list
            List of labels in correct order

        focus_field : str
            Field from the meta data item to be used in encoding

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.

        length_frames : int
            Length of encoded segment in frames

        length_seconds : float > 0.0
            Length of encoded segment in seconds

        """

        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'length_frames': length_frames,
                'length_seconds': length_seconds
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(OneHotEncodingProcessor, self).__init__(**kwargs)

        self.focus_field = focus_field

    def process(self, data=None, focus_field=None, length_frames=None, length_seconds=None, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode.

        focus_field : str
            Field from the meta data item to be used in encoding. If None, one given as parameter for class
            constructor is used.

        length_frames : int
            Length of encoded segment in frames. If None, one given as parameter for class constructor is used.

        length_seconds : float > 0.0
            Length of encoded segment in seconds. If None, one given as parameter for class constructor is used.

        Returns
        -------
        BinaryMatrixContainer

        """

        from dcase_util.containers import MetaDataContainer

        if focus_field is None:
            focus_field = self.focus_field

        if isinstance(data, MetaDataContainer):
            chain_item = self.get_processing_chain_item()

            if length_frames is None and length_seconds is not None:
                length_frames = self._length_to_frames(length_seconds)

            if length_frames is None:
                length_frames = self.length_frames

            if 'process_parameters' not in chain_item:
                chain_item['process_parameters'] = {}

            chain_item['process_parameters']['focus_field'] = focus_field
            chain_item['process_parameters']['length_frames'] = length_frames

            if len(data) > 0:
                label = data[0].get(focus_field)

            self.encode(
                label=label,
                length_frames=length_frames
            )

            processing_chain_item = self.get_processing_chain_item()

            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain
            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            from dcase_util.containers import BinaryMatrix2DContainer
            container = BinaryMatrix2DContainer(
                data=self.data,
                label_list=self.label_list,
                time_resolution=self.time_resolution,
                processing_chain=processing_chain
            )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class ManyHotEncodingProcessor(ManyHotEncoder, ProcessorMixin):
    """Event roll encoding processor"""
    input_type = ProcessingChainItemType.METADATA  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label_list=None, focus_field='tags', time_resolution=None,
                 length_frames=None, length_seconds=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list
            List of labels in correct order

        focus_field : str
            Field from the meta data item to be used in encoding

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.

        length_frames : int
            Length of encoded segment in frames

        length_seconds : float > 0.0
            Length of encoded segment in seconds

        """

        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'length_frames': length_frames,
                'length_seconds': length_seconds,
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(ManyHotEncodingProcessor, self).__init__(**kwargs)

        self.focus_field = focus_field

    def process(self, data=None, focus_field=None, length_frames=None, length_seconds=None, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode.

        focus_field : str
            Field from the meta data item to be used in encoding. If None, one given as parameter for
            class constructor is used.

        length_frames : int
            Length of encoded segment in frames. If None, one given as parameter for class constructor is used.

        length_seconds : float > 0.0
            Length of encoded segment in seconds. If None, one given as parameter for class constructor is used.

        Returns
        -------
        BinaryMatrixContainer

        """

        from dcase_util.containers import MetaDataContainer

        if focus_field is None:
            focus_field = self.focus_field

        if isinstance(data, MetaDataContainer):
            chain_item = self.get_processing_chain_item()

            if length_frames is None and length_seconds is not None:
                length_frames = self._length_to_frames(length_seconds)

            if length_frames is None:
                length_frames = self.length_frames

            if len(data) > 0:
                label_list = data[0].get(focus_field)
                if isinstance(label_list, str):
                    label_list = [label_list]

            if 'process_parameters' not in chain_item:
                chain_item['process_parameters'] = {}

            chain_item['process_parameters']['focus_field'] = focus_field
            chain_item['process_parameters']['length_frames'] = length_frames

            self.encode(
                label_list=label_list,
                length_frames=length_frames
            )

            processing_chain_item = self.get_processing_chain_item()

            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain
            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            from dcase_util.containers import BinaryMatrix2DContainer
            container = BinaryMatrix2DContainer(
                data=self.data,
                label_list=self.label_list,
                time_resolution=self.time_resolution,
                processing_chain=processing_chain
            )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class EventRollEncodingProcessor(EventRollEncoder, ProcessorMixin):
    """Event roll encoding processor"""
    input_type = ProcessingChainItemType.METADATA  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label_list=None, time_resolution=None, focus_field='event_label', **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list
            List of labels in correct order

        focus_field : str
            Field from the meta data item to be used in encoding

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.

        """

        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'label': focus_field
            }
        )

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(EventRollEncodingProcessor, self).__init__(**kwargs)

    def process(self, data=None, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode.

        Returns
        -------
        BinaryMatrixContainer

        """

        from dcase_util.containers import MetaDataContainer

        if isinstance(data, MetaDataContainer):
            self.encode(metadata_container=data)

            processing_chain_item = self.get_processing_chain_item()

            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain
            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            from dcase_util.containers import BinaryMatrix2DContainer
            container = BinaryMatrix2DContainer(
                data=self.data,
                label_list=self.label_list,
                time_resolution=self.time_resolution,
                processing_chain=processing_chain
            )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)

