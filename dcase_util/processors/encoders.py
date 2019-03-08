#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import numpy

from dcase_util.processors import Processor, ProcessingChainItemType, ProcessingChain
from dcase_util.data import OneHotEncoder, ManyHotEncoder, EventRollEncoder, OneHotLabelEncoder


class OneHotEncodingProcessor(Processor):
    """One hot encoding processor"""
    input_type = ProcessingChainItemType.METADATA  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label_list=None, focus_field='scene_label', time_resolution=1.0,
                 length_frames=1, length_seconds=None, allow_unknown_labels=False,
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

        allow_unknown_labels : bool
            Allow unknown labels in the decoding. If False, labels not in the given label_list will produce an error.
            Default value False

        """

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'length_frames': length_frames,
                'length_seconds': length_seconds,
                'allow_unknown_labels': allow_unknown_labels
            }
        )

        # Run super init to call init of mixins too
        super(OneHotEncodingProcessor, self).__init__(**kwargs)

        self.encoder = OneHotEncoder(**self.init_parameters)
        self.focus_field = focus_field

    def process(self, data=None, label=None, focus_field=None, length_frames=None, length_seconds=None, store_processing_chain=False, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode. Give data in either through meta data container or directly with label parameter.

        label : str
            Class label to be hot

        focus_field : str
            Field from the meta data item to be used in encoding. If None, one given as parameter for class
            constructor is used.

        length_frames : int
            Length of encoded segment in frames. If None, one given as parameter for class constructor is used.

        length_seconds : float > 0.0
            Length of encoded segment in seconds. If None, one given as parameter for class constructor is used.

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        BinaryMatrixContainer

        """

        if data is None and label is None:
            message = '{name}: Give data or label parameter.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

        from dcase_util.containers import MetaDataContainer

        if data is not None and not isinstance(data, MetaDataContainer):
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)

        if focus_field is None:
            focus_field = self.focus_field

        if data is not None and len(data) > 0 and label is None:
            label = data[0].get(focus_field)

        # Do processing
        self.encoder.encode(
            label=label,
            length_frames=length_frames,
            length_seconds=length_seconds
        )

        if store_processing_chain:
            # Get processing chain item
            processing_chain_item = self.get_processing_chain_item()

            if 'process_parameters' not in processing_chain_item:
                processing_chain_item['process_parameters'] = {}

            processing_chain_item['process_parameters']['focus_field'] = focus_field
            processing_chain_item['process_parameters']['length_frames'] = length_frames

            # Create processing chain to be stored in the container, and push chain item into it
            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain

            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)
        else:
            processing_chain = None

        from dcase_util.containers import BinaryMatrix2DContainer
        container = BinaryMatrix2DContainer(
            data=self.encoder.data,
            label_list=self.encoder.label_list,
            time_resolution=self.encoder.time_resolution,
            processing_chain=processing_chain
        )

        return container


class ManyHotEncodingProcessor(Processor):
    """Many hot encoding processor"""
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'length_frames': length_frames,
                'length_seconds': length_seconds,
            }
        )

        # Run super init to call init of mixins too
        super(ManyHotEncodingProcessor, self).__init__(**kwargs)

        self.focus_field = focus_field
        self.encoder = ManyHotEncoder(**self.init_parameters)

    def process(self, data=None, label_list=None, focus_field=None, length_frames=None, length_seconds=None, store_processing_chain=False, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode.
            Default value None

        label_list : list of str
            Class labels to be hot
            Default value None

        focus_field : str
            Field from the meta data item to be used in encoding. If None, one given as parameter for
            class constructor is used.
            Default value None

        length_frames : int
            Length of encoded segment in frames. If None, one given as parameter for class constructor is used.
            Default value None

        length_seconds : float > 0.0
            Length of encoded segment in seconds. If None, one given as parameter for class constructor is used.
            Default value None

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        BinaryMatrixContainer

        """

        if data is None and label_list is None:
            message = '{name}: Give data or label_list parameter.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

        from dcase_util.containers import MetaDataContainer

        if data is not None and not isinstance(data, MetaDataContainer):
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)

        if focus_field is None:
            focus_field = self.focus_field

        if data is not None and len(data) > 0 and label_list is None:
            label_list = data[0].get(focus_field)
            if isinstance(label_list, str):
                label_list = [label_list]

        # Do processing
        self.encoder.encode(
            label_list=label_list,
            length_frames=length_frames,
            length_seconds=length_seconds
        )

        if store_processing_chain:
            # Get processing chain item
            processing_chain_item = self.get_processing_chain_item()

            if 'process_parameters' not in processing_chain_item:
                processing_chain_item['process_parameters'] = {}

            processing_chain_item['process_parameters']['focus_field'] = focus_field
            processing_chain_item['process_parameters']['length_frames'] = length_frames

            # Create processing chain to be stored in the container, and push chain item into it
            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain

            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)

        else:
            processing_chain = None

        from dcase_util.containers import BinaryMatrix2DContainer
        container = BinaryMatrix2DContainer(
            data=self.encoder.data,
            label_list=self.encoder.label_list,
            time_resolution=self.encoder.time_resolution,
            processing_chain=processing_chain
        )

        return container


class EventRollEncodingProcessor(Processor):
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'label': focus_field
            }
        )

        # Run super init to call init of mixins too
        super(EventRollEncodingProcessor, self).__init__(**kwargs)

        self.encoder = EventRollEncoder(**self.init_parameters)

    def process(self, data=None, pad_length=None, store_processing_chain=False, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode.

        pad_length : int
            Length to be padded

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        BinaryMatrixContainer

        """

        from dcase_util.containers import MetaDataContainer

        if isinstance(data, MetaDataContainer):
            # Do processing
            self.encoder.encode(
                metadata_container=data
            )

            if store_processing_chain:
                # Get processing chain item
                processing_chain_item = self.get_processing_chain_item()

                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                # Create processing chain to be stored in the container, and push chain item into it
                if hasattr(data, 'processing_chain'):
                    data.processing_chain.push_processor(**processing_chain_item)
                    processing_chain = data.processing_chain

                else:
                    processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            else:
                processing_chain = None

            from dcase_util.containers import BinaryMatrix2DContainer
            container = BinaryMatrix2DContainer(
                data=self.encoder.data,
                label_list=self.encoder.label_list,
                time_resolution=self.encoder.time_resolution,
                processing_chain=processing_chain
            )

            if pad_length:
                container.pad(length=pad_length)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class OneHotLabelEncodingProcessor(Processor):
    """One hot label encoding processor"""
    input_type = ProcessingChainItemType.METADATA  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, label_list=None, focus_field='scene_label', time_resolution=1.0,
                 length_frames=1, length_seconds=None,
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'label_list': label_list,
                'time_resolution': time_resolution,
                'length_frames': length_frames,
                'length_seconds': length_seconds
            }
        )

        # Run super init to call init of mixins too
        super(OneHotLabelEncodingProcessor, self).__init__(**kwargs)

        self.encoder = OneHotLabelEncoder(**self.init_parameters)
        self.focus_field = focus_field

    def process(self, data=None, label=None, focus_field=None, length_frames=None, length_seconds=None, store_processing_chain=False, **kwargs):
        """Encode metadata

        Parameters
        ----------
        data : MetaDataContainer
            Meta data to encode. Give data in either through meta data container or directly with label parameter.

        label : str
            Class label to be hot

        focus_field : str
            Field from the meta data item to be used in encoding. If None, one given as parameter for class
            constructor is used.

        length_frames : int
            Length of encoded segment in frames. If None, one given as parameter for class constructor is used.

        length_seconds : float > 0.0
            Length of encoded segment in seconds. If None, one given as parameter for class constructor is used.

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        DataMatrix2DContainer

        """

        if data is None and label is None:
            message = '{name}: Give data or label parameter.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

        from dcase_util.containers import MetaDataContainer

        if data is not None and not isinstance(data, MetaDataContainer):
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)

        if focus_field is None:
            focus_field = self.focus_field

        if data is not None and len(data) > 0 and label is None:
            label = data[0].get(focus_field)

        # Do processing
        self.encoder.encode(
            label=label,
            length_frames=length_frames,
            length_seconds=length_seconds
        )

        if store_processing_chain:
            # Get processing chain item
            processing_chain_item = self.get_processing_chain_item()

            if 'process_parameters' not in processing_chain_item:
                processing_chain_item['process_parameters'] = {}

            processing_chain_item['process_parameters']['focus_field'] = focus_field
            processing_chain_item['process_parameters']['length_frames'] = length_frames

            # Create processing chain to be stored in the container, and push chain item into it
            if hasattr(data, 'processing_chain'):
                data.processing_chain.push_processor(**processing_chain_item)
                processing_chain = data.processing_chain

            else:
                processing_chain = ProcessingChain().push_processor(**processing_chain_item)
        else:
            processing_chain = None

        from dcase_util.containers import DataMatrix2DContainer
        container = DataMatrix2DContainer(
            data=self.encoder.data,
            label_list=self.encoder.label_list,
            time_resolution=self.encoder.time_resolution,
            processing_chain=processing_chain
        )

        return container

