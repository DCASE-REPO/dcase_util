#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import numpy

from dcase_util.containers import RepositoryContainer
from dcase_util.processors import Processor, ProcessingChainItemType, ProcessingChain
from dcase_util.data import Normalizer, RepositoryNormalizer, Aggregator, Sequencer, Stacker, Masker


class AggregationProcessor(Processor):
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

        if recipe is None and kwargs.get('aggregation_recipe', None) is not None:
            recipe = kwargs.get('aggregation_recipe', None)

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'win_length_frames': win_length_frames,
                'hop_length_frames': hop_length_frames,
                'recipe': recipe
            }
        )

        # Run super init to call init of mixins too
        super(AggregationProcessor, self).__init__(**kwargs)

        self.aggregator = Aggregator(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process

        Parameters
        ----------
        data : DataContainer
            Data to be aggregated

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            # Do processing
            container = self.aggregator.aggregate(
                data=data,
                **kwargs
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Push chain item into processing chain stored in the container
                container.processing_chain.push_processor(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryAggregationProcessor(Processor):
    """Data aggregation processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

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

        if recipe is None and kwargs.get('aggregation_recipe', None) is not None:
            recipe = kwargs.get('aggregation_recipe', None)

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'win_length_frames': win_length_frames,
                'hop_length_frames': hop_length_frames,
                'recipe': recipe
            }
        )

        # Run super init to call init of mixins too
        super(RepositoryAggregationProcessor, self).__init__(**kwargs)

        self.aggregator = Aggregator(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process

        Parameters
        ----------
        data : DataRepository
            Data

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataMatrix3DContainer

        """

        if isinstance(data, RepositoryContainer):
            # Label exists in data repository
            for label in data:
                for stream_id in data[label]:
                    # Do processing
                    data.set_container(
                        label=label,
                        stream_id=stream_id,
                        container=self.aggregator.aggregate(
                            data=data.get_container(
                                label=label,
                                stream_id=stream_id
                            ),
                            **kwargs
                        )
                    )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Push chain item into processing chain stored in the container
                data.processing_chain.push_processor(**processing_chain_item)

            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class SequencingProcessor(Processor):
    """Data sequencing processor"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'sequence_length': sequence_length,
                'hop_length': hop_length,
                'padding': padding,
                'shift': shift,
                'shift_border': shift_border,
                'required_data_amount_per_segment': required_data_amount_per_segment
            }
        )

        # Run super init to call init of mixins too
        super(SequencingProcessor, self).__init__(**kwargs)

        self.sequencer = Sequencer(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process

        Parameters
        ----------
        data : DataContainer
            Data

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataMatrix3DContainer

        """
        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            # Do processing
            container = self.sequencer.sequence(
                data=data,
                **kwargs
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Push chain item into processing chain stored in the container
                container.processing_chain.push_processor(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositorySequencingProcessor(Processor):
    """Data sequencing processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

    def __init__(self, sequence_length=10, hop_length=None, padding=None, shift=0,
                 shift_border='roll', required_data_amount_per_segment=0.9, **kwargs):
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'sequence_length': sequence_length,
                'hop_length': hop_length,
                'padding': padding,
                'shift': shift,
                'shift_border': shift_border,
                'required_data_amount_per_segment': required_data_amount_per_segment
            }
        )

        # Run super init to call init of mixins too
        super(RepositorySequencingProcessor, self).__init__(**kwargs)

        self.sequencer = Sequencer(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process

        Parameters
        ----------
        data : DataRepository
            Data

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataMatrix3DContainer

        """

        if isinstance(data, RepositoryContainer):
            # Label exists in data repository
            for label in data:
                for stream_id in data[label]:
                    # Do processing
                    data.set_container(
                        label=label,
                        stream_id=stream_id,
                        container=self.sequencer.sequence(
                            data=data.get_container(
                                label=label,
                                stream_id=stream_id
                            ),
                            **kwargs
                        )
                    )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Push chain item into processing chain stored in the container
                data.processing_chain.push_processor(**processing_chain_item)

            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class NormalizationProcessor(Processor):
    """Data normalizer to accumulate data statistics"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, n=None, s1=None, s2=None, mean=None, std=None, normalizer=None, filename=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        n : int
            Item count used to calculate statistics
            Default value None

        s1 : numpy.array [shape=(vector_length,)]
            Vector-wise sum of the data seen by the Normalizer
            Default value None

        s2 : numpy.array [shape=(vector_length,)]
            Vector-wise sum^2 of the data seen by the Normalizer
            Default value None

        mean : numpy.ndarray() [shape=(vector_length, 1)]
            Mean of the data
            Default value None

        std : numpy.ndarray() [shape=(vector_length, 1)]
            Standard deviation of the data
            Default value None

        normalizer : Normalizer
            Normalizer object to initialize the processor
            Default value None

        filename : str
            Filename to saved normalizer object to initialize the processor
            Default value None

        """

        if filename is not None:
            normalizer = Normalizer().load(filename=filename)

        # Inject initialization parameters back to kwargs
        if isinstance(normalizer, Normalizer):
            # Valid Normalizer class given
            kwargs.update(
                {
                    'n': normalizer.n,
                    's1': normalizer.s1,
                    's2': normalizer.s2,
                    'mean': normalizer._mean,
                    'std': normalizer._std
                }
            )

        else:
            kwargs.update(
                {
                    'n': n,
                    's1': s1,
                    's2': s2,
                    'mean': mean,
                    'std': std
                }
            )

        # Run super init to call init of mixins too
        super(NormalizationProcessor, self).__init__(**kwargs)

        self.normalizer = Normalizer(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Normalize feature matrix with internal statistics of the class

        Parameters
        ----------
        data : DataContainer or numpy.ndarray
            DataContainer or numpy.ndarray to be normalized

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataContainer or numpy.ndarray [shape=(frames, number of feature values)]
            Normalized data matrix

        """

        from dcase_util.containers import ContainerMixin

        if isinstance(data, ContainerMixin):
            # Do processing
            container = self.normalizer.normalize(
                data=data,
                **kwargs
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Push chain item into processing chain stored in the container
                container.processing_chain.push_processor(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryNormalizationProcessor(Processor):
    """Data normalizer to accumulate data statistics inside repository"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY
    output_type = ProcessingChainItemType.DATA_REPOSITORY

    def __init__(self, parameters=None, normalizers=None, filename=None, **kwargs):
        """__init__ method.

        Parameters
        ----------
        parameters : dict
            Pre-calculated statistics in dict to initialize internal state, label as key
            Default value None

        normalizer : Normalizer
            Normalizer object to initialize the processor, label as key
            Default value None

        filename : str
            Filename to saved normalizer object to initialize the processor
            Default value None

        """

        if parameters is None:
            parameters = {}

        if filename is not None:
            normalizers = RepositoryNormalizer().load(filename=filename)

        if not parameters and isinstance(normalizers, RepositoryNormalizer):

            for label in normalizers.normalizers:
                if label not in parameters:
                    parameters[label] = {}

                parameters[label] = {
                    'mean': normalizers.normalizers[label].mean,
                    'std': normalizers.normalizers[label].std
                }

        self.parameters = parameters

        # Run super init to call init of mixins too
        super(RepositoryNormalizationProcessor, self).__init__(**kwargs)

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

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Normalize data repository with internal statistics

        Parameters
        ----------
        data : DataRepository
            DataRepository
            Default value None

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataRepository

        """

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

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Push chain item into processing chain stored in the container
                data.processing_chain.push_processor(**processing_chain_item)

            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class StackingProcessor(Processor):
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'recipe': recipe,
                'hop': hop
            }
        )

        # Run super init to call init of mixins too
        super(StackingProcessor, self).__init__(**kwargs)

        self.stacker = Stacker(**self.init_parameters)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Vector creation based on recipe

        Parameters
        ----------
        data : RepositoryContainer
            Repository with needed data

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import RepositoryContainer

        if isinstance(data, RepositoryContainer):
            # Do processing
            container = self.stacker.stack(
                repository=data,
                **kwargs
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Push chain item into processing chain stored in the container
                container.processing_chain.push_processor(
                    **processing_chain_item
                )

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryMaskingProcessor(Processor):
    """Data masking processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

    def __init__(self, **kwargs):
        """Constructor
        """

        # Run super init to call init of mixins too
        super(RepositoryMaskingProcessor, self).__init__(**kwargs)

        self.masker = Masker()

    def process(self, data, mask_events=None, store_processing_chain=False, **kwargs):
        """Vector creation based on recipe

        Parameters
        ----------
        data : RepositoryContainer
            Repository with needed data

        mask_events : MetaDaaContainer
            Masking events
            Default value None

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import RepositoryContainer

        if isinstance(data, RepositoryContainer):
            # Do processing
            container = self.masker.mask(
                data=data,
                mask_events=mask_events
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Push chain item into processing chain stored in the container
                container.processing_chain.push_processor(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class DataShapingProcessor(Processor):
    """Data shaping processor"""
    input_type = ProcessingChainItemType.DATA_CONTAINER  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, axis_list=None, time_axis=None, data_axis=None, sequence_axis=None, channel_axis=None, **kwargs):
        """Constructor

        Parameters
        ----------
        axis_list : list
            List of axis names in order. Use this parameter or set by time_axis, data_axis, and sequence_axis.
            Default value None

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

        """

        # Initialize axis ids
        self.time_axis = None
        self.data_axis = None
        self.sequence_axis = None
        self.channel_axis = None

        if axis_list is not None:
            if isinstance(axis_list, list):
                for axis_id, item in enumerate(axis_list):
                    if 'time' in item:
                        self.time_axis = axis_id

                    elif 'data' in item:
                        self.data_axis = axis_id

                    elif 'sequence' in item:
                        self.sequence_axis = axis_id

                    elif 'channel' in item:
                        self.channel_axis = axis_id

            else:
                message = '{name}: Wrong type for axis_list, list required.'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise ValueError(message)

        else:
            self.time_axis = time_axis
            self.data_axis = data_axis
            self.sequence_axis = sequence_axis
            self.channel_axis = channel_axis

        # Run super init to call init of mixins too
        super(DataShapingProcessor, self).__init__(**kwargs)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process data

        Parameters
        ----------
        data : DataContainer
            Data to be reshaped

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataContainer

        """

        from dcase_util.containers import DataContainer, DataMatrix2DContainer, DataMatrix3DContainer, DataMatrix4DContainer

        if isinstance(data, DataContainer):
            # Do processing

            if isinstance(data, DataMatrix4DContainer):
                data.change_axis(
                    time_axis=self.time_axis,
                    data_axis=self.data_axis,
                    sequence_axis=self.sequence_axis,
                    channel_axis=self.channel_axis
                )

            elif isinstance(data, DataMatrix3DContainer):
                data.change_axis(
                    time_axis=self.time_axis,
                    data_axis=self.data_axis,
                    sequence_axis=self.sequence_axis
                )

            elif isinstance(data, DataMatrix2DContainer):
                data.change_axis(
                    time_axis=self.time_axis,
                    data_axis=self.data_axis
                )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Push chain item into processing chain stored in the container
                data.processing_chain.push_processor(**processing_chain_item)

            return data

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type
            )

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryToMatrixProcessor(Processor):
    """Repository converting processor"""
    input_type = ProcessingChainItemType.DATA_REPOSITORY  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label=None, expanded_dimension='last', **kwargs):
        """Constructor

        Parameters
        ----------
        label : str
            Default value None

        data_format : str
            Default value 'channel_last'

        expanded_dimension : str
            Controls where stream information should be added.
            Possible values ['first', 'last']
            Default value 'last'

        """

        # Run super init to call init of mixins too
        super(RepositoryToMatrixProcessor, self).__init__(**kwargs)

        self.label = label
        self.expanded_dimension = expanded_dimension

    def process(self, data=None, label=None, store_processing_chain=False, **kwargs):
        """Process data

        Parameters
        ----------
        data : DataRepository
            Data to be reshaped

        Returns
        -------
        DataContainer

        """

        if label is None:
            label = self.label

        from dcase_util.containers import DataRepository, DataMatrix3DContainer,  DataMatrix4DContainer

        if isinstance(data, DataRepository):
            # Do processing
            if label in data:
                data_list = []
                for stream_id in data.stream_ids(label=label):
                    current_container = data.get_container(
                        label=label,
                        stream_id=stream_id
                    )

                    data_list.append(current_container.data)

                if len(current_container.shape) == 3:
                    # Set expanded axis
                    if self.expanded_dimension == 'first':
                        stack_axis = 0

                    elif self.expanded_dimension == 'last':
                        stack_axis = 3

                    # Create a new container
                    container = DataMatrix4DContainer(
                        data=numpy.stack(data_list, axis=stack_axis),
                        processing_chain=data.processing_chain
                    )

                    # Set axis correctly
                    if self.expanded_dimension == 'first':
                        container.time_axis = current_container.time_axis + 1
                        container.data_axis = current_container.data_axis + 1
                        container.sequence_axis = current_container.sequence_axis + 1
                        container.channel_axis = 0

                    elif self.expanded_dimension == 'last':
                        container.time_axis = current_container.time_axis
                        container.data_axis = current_container.data_axis
                        container.sequence_axis = current_container.sequence_axis
                        container.channel_axis = 3

                elif len(current_container.shape) == 2:
                    # Set expanded axis
                    if self.expanded_dimension == 'first':
                        stack_axis = 0

                    elif self.expanded_dimension == 'last':
                        stack_axis = 2

                    # Create a new container
                    container = DataMatrix3DContainer(
                        data=numpy.stack(data_list, axis=stack_axis),
                        processing_chain=data.processing_chain
                    )

                    # Set axis correctly
                    if self.expanded_dimension == 'first':
                        container.time_axis = current_container.time_axis + 1
                        container.data_axis = current_container.data_axis + 1
                        container.sequence_axis = 0

                    elif self.expanded_dimension == 'last':
                        container.time_axis = current_container.time_axis
                        container.data_axis = current_container.data_axis
                        container.sequence_axis = 2

                if store_processing_chain:
                    # Get processing chain item
                    processing_chain_item = self.get_processing_chain_item()

                    # Update current processing parameters into chain item
                    processing_chain_item.update({
                        'process_parameters': kwargs
                    })

                    # Push chain item into processing chain stored in the container
                    container.processing_chain.push_processor(**processing_chain_item)

                return container
            else:
                message = '{name}: Label not found from repository [{label}].'.format(
                    name=self.__class__.__name__,
                    label=label
                )

                self.logger.exception(message)
                raise ValueError(message)

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type
            )

            self.logger.exception(message)
            raise ValueError(message)

