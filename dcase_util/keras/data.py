# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import numpy
import copy

from dcase_util.ui import FancyStringifier, FancyLogger
from dcase_util.containers import ContainerMixin
from dcase_util.data import DataBuffer


def get_keras_data_sequence_class():
    # Use getter method to avoid importing Keras when importing dcase_util. This allows user to decide when import
    # Keras, so that user can set random seeds before Keras import.

    from keras.utils import Sequence

    class KerasDataSequence(Sequence, ContainerMixin):
        def __init__(self, item_list=None, batch_size=64,
                     buffer_size=None,
                     data_processing_chain=None, meta_processing_chain=None,
                     data_processing_chain_callback_on_epoch_end=None, meta_processing_chain_callback_on_epoch_end=None,
                     transformer_callbacks=None,
                     refresh_buffer_on_epoch=False,
                     data_format='channels_last',
                     target_format='single_target_per_sequence',
                     **kwargs):
            """Constructor

            Parameters
            ----------
            item_list : list or dict
                Items in the data sequence. List containing multi-level dictionary with first level key
                'data' and 'meta'. Second level should contain parameters for process method in the processing chain.
                Default value None

            batch_size : int
                Batch size (item count).
                Default value 64

            buffer_size : int
                Internal buffer size (item count). By setting this sufficiently high, data sequence generator can
                possibly fit all sequence items into internal buffer and can fetch without loading from disk.
                Set to None, if no internal buffer used.
                Default value None

            data_processing_chain : ProcessingChain
                Data processing chain.
                Default value None

            meta_processing_chain : ProcessingChain
                Meta processing chain.
                Default value None

            data_processing_chain_callback_on_epoch_end : list of dict
                Can be used to call methods with parameters for processing chain at the end of epoch. This can be
                used to control processing chain's internal status (e.g. roll the data).
                Default value None

            meta_processing_chain_callback_on_epoch_end : list of dict
                Can be used to call methods with parameters for processing chain at the end of epoch. This can be
                used to control processing chain's internal status (e.g. roll the data).
                Default value None

            transformer_callbacks : list of func
                Transformer callbacks to jointly process data and meta. This can be used for local data modification and
                data augmentation.
                Default value None

            refresh_buffer_on_epoch : bool
                In case internal data buffer is used, force data and meta refresh at the end of each epoch. Use this if
                data is modified/augmented differently for each epoch.
                In case data_processing_chain_callback_on_epoch_end or meta_processing_chain_callback_on_epoch_end is
                used, this parameter is automatically set to True.
                Default value False

            data_format : str
                Keras like data format, controls where channel should be added.
                Possible values ['channels_first', 'channels_last']
                Default value 'channels_last'

            target_format : str
                Meta data interpretation in the relation to the data items.
                Default value 'single_target_per_segment'

            """

            # Run ContainerMixin init
            ContainerMixin.__init__(self, **kwargs)

            self._data_shape = None
            self._data_axis = None

            self.item_list = copy.copy(item_list)

            self.batch_size = batch_size

            self.buffer_size = buffer_size
            self.data_refresh_on_epoch = refresh_buffer_on_epoch

            if data_format is None:
                data_format = 'channels_last'

            self.data_format = data_format
            if self.data_format not in ['channels_first', 'channels_last']:
                message = '{name}: Unknown data_format [{data_format}].'.format(
                    name=self.__class__.__name__,
                    data_format=self.data_format
                )
                self.logger.exception(message)
                raise NotImplementedError(message)

            if target_format is None:
                target_format = 'single_target_per_sequence'

            self.target_format = target_format
            if self.target_format not in ['same', 'single_target_per_sequence']:
                message = '{name}: Unknown target_format [{target_format}].'.format(
                    name=self.__class__.__name__,
                    target_format=self.target_format
                )
                self.logger.exception(message)
                raise NotImplementedError(message)

            if data_processing_chain_callback_on_epoch_end is None:
                data_processing_chain_callback_on_epoch_end = []

            self.data_processing_chain_callback_on_epoch_end = data_processing_chain_callback_on_epoch_end

            if self.data_processing_chain_callback_on_epoch_end:
                self.data_refresh_on_epoch = True

            if meta_processing_chain_callback_on_epoch_end is None:
                meta_processing_chain_callback_on_epoch_end = []

            self.meta_processing_chain_callback_on_epoch_end = meta_processing_chain_callback_on_epoch_end

            if transformer_callbacks is None:
                transformer_callbacks = []

            self.transformer_callbacks = transformer_callbacks

            # Processing chains
            self.data_processing_chain = data_processing_chain
            self.meta_processing_chain = meta_processing_chain

            if self.buffer_size is not None:
                # Initialize data buffer
                self.data_buffer = DataBuffer(
                    size=self.buffer_size
                )

            else:
                self.data_buffer = None

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

            output = ''
            output += ui.class_name(self.__class__.__name__, indent=indent) + '\n'

            output += ui.data(
                indent=indent,
                field='Batch size',
                value=self.batch_size
            ) + '\n'

            output += ui.data(
                indent=indent,
                field='Epoch size',
                value=len(self), unit='batches'
            ) + '\n'

            shape = self.data_shape
            axis = self.data_axis

            output += ui.data(field='Data item shape', value=shape, indent=indent) + '\n'

            output += ui.data(
                indent=indent + 2,
                field='Time',
                value=shape[axis['time_axis']]
            ) + '\n'

            output += ui.data(
                indent=indent + 2,
                field='Data',
                value=shape[axis['data_axis']]
            ) + '\n'

            if 'sequence_axis' in axis:
                output += ui.data(
                    indent=indent + 2,
                    field='Sequence',
                    value=shape[axis['sequence_axis']]
                ) + '\n'

            output += ui.data(
                indent=indent + 2,
                field='Axis',
                value=axis
            ) + '\n'

            if self.buffer_size is not None:
                output += ui.line(field='Buffer', indent=indent) + '\n'
                output += ui.data(
                    indent=indent + 2,
                    field='buffer_size',
                    value=self.buffer_size,
                    unit='items'
                ) + '\n'
                output += ui.data(
                    indent=indent + 2,
                    field='buffer usage',
                    value=self.data_buffer.count,
                    unit='items'
                ) + '\n'
                output += ui.data(
                    indent=indent + 2,
                    field='buffer usage',
                    value=(self.data_buffer.count / float(self.buffer_size)) * 100,
                    unit='%'
                ) + '\n'

            return output

        def __getitem__(self, index):
            start_index = index * self.batch_size
            stop_index = (index + 1) * self.batch_size

            batch_buffer_data = []
            batch_buffer_meta = []

            for item_index in range(start_index, stop_index):
                if item_index < len(self.item_list):
                    item = self.item_list[item_index]

                    # Load item data
                    data, meta = self.process_item(item=item)

                    if self.transformer_callbacks:
                        # Apply transformer callbacks
                        for callback in self.transformer_callbacks:
                            data, meta = callback(
                                data=data,
                                meta=meta
                            )

                    # Collect data
                    batch_buffer_data.append(data.data)

                    # Collect meta
                    if self.target_format == 'single_target_per_sequence':
                        # Collect single target per sequence
                        for i in range(0, data.shape[data.sequence_axis]):
                            batch_buffer_meta.append(meta.data[:, 0])

                    elif self.target_format == 'same':
                        # Collect single target per sequence
                        batch_buffer_meta.append(
                            numpy.repeat(
                                a=meta.data,
                                repeats=data.length,
                                axis=1
                            )
                        )

            if len(data.shape) == 2:
                # Prepare 2D data, stack along time_axis
                if data.time_axis == 0:
                    batch_buffer_data = numpy.vstack(batch_buffer_data)

                elif data.time_axis == 1:
                    batch_buffer_data = numpy.hstack(batch_buffer_data)

            elif len(data.shape) == 3:
                # Prepare 3D data, stack along sequence_axis
                if data.sequence_axis == 0:
                    batch_buffer_data = numpy.vstack(batch_buffer_data)

                elif data.sequence_axis == 1:
                    batch_buffer_data = numpy.hstack(batch_buffer_data)

                elif data.sequence_axis == 2:
                    batch_buffer_data = numpy.dstack(batch_buffer_data)

                # Add channel dimension to the data
                if self.data_format == 'channels_first':
                    batch_buffer_data = numpy.expand_dims(
                        batch_buffer_data,
                        axis=0
                    )

                elif self.data_format == 'channels_last':
                    batch_buffer_data = numpy.expand_dims(
                        batch_buffer_data,
                        axis=3
                    )

            # Prepare meta
            if self.target_format == 'single_target_per_sequence':
                batch_buffer_meta = numpy.vstack(batch_buffer_meta)

            elif self.target_format == 'same':
                batch_buffer_meta = numpy.hstack(batch_buffer_meta).T

            return batch_buffer_data, batch_buffer_meta

        def __len__(self):
            num_batches = int(numpy.ceil(len(self.item_list) / float(self.batch_size)))

            if num_batches > 0:
                return num_batches
            else:
                return 1

        @property
        def data_shape(self):
            if self._data_shape is None:
                # Load first item and get data length
                data = self.process_item(
                    item=self.item_list[0]
                )[0]

                self._data_shape = data.shape

                self._data_axis = {
                    'time_axis': data.time_axis,
                    'data_axis': data.data_axis
                }

                if hasattr(data,'sequence_axis'):
                    self._data_axis['sequence_axis']= data.sequence_axis

            return self._data_shape

        @property
        def data_axis(self):
            if self._data_axis is None:
                # Load first item and get data length
                data = self.process_item(
                    item=self.item_list[0]
                )[0]

                self._data_shape = data.shape
                self._data_axis = {
                    'time_axis': data.time_axis,
                    'data_axis': data.data_axis
                }

                if hasattr(data, 'sequence_axis'):
                    self._data_axis['sequence_axis'] = data.sequence_axis

            return self._data_axis

        @property
        def data_size(self):
            shape = self.data_shape
            axis = self.data_axis
            size = {
                'time': shape[axis['time_axis']],
                'data': shape[axis['data_axis']],
            }

            if 'sequence_axis' in axis:
                size['sequence'] = shape[axis['sequence_axis']]

            return size

        def process_item(self, item):
            if self.data_buffer is not None:
                # Fetch data and meta through internal buffer
                if not self.data_buffer.key_exists(key=item):
                    data = self.data_processing_chain.process(**item['data'])
                    meta = self.meta_processing_chain.process(**item['meta'])

                    self.data_buffer.set(
                        key=item,
                        data=data,
                        meta=meta
                    )

                else:
                    data, meta = self.data_buffer.get(key=item)

            else:
                # Fetch data and meta directly.
                data = self.data_processing_chain.process(**item['data'])
                meta = self.meta_processing_chain.process(**item['meta'])

            return data, meta

        def on_epoch_end(self):
            if self.data_processing_chain_callback_on_epoch_end:
                for callback_parameters in self.data_processing_chain_callback_on_epoch_end:
                    if 'method_name' in callback_parameters:
                        self.data_processing_chain.call_method(
                            method_name=callback_parameters['method_name'],
                            parameters=callback_parameters.get('parameters', {})
                        )

            if self.meta_processing_chain_callback_on_epoch_end:
                for callback_parameters in self.meta_processing_chain_callback_on_epoch_end:
                    if 'method_name' in callback_parameters:
                        self.data_processing_chain.call_method(
                            method_name=callback_parameters['method_name'],
                            parameters=callback_parameters.get('parameters', {})
                        )

            if self.data_buffer is not None and self.data_refresh_on_epoch:
                # Force reload of data
                self.data_buffer.clear()

    return KerasDataSequence


def data_collector(item_list=None,
                   data_processing_chain=None, meta_processing_chain=None,
                   target_format='single_target_per_sequence',
                   channel_dimension='channels_last',
                   verbose=True,
                   print_indent=2
                   ):
    """Data collector

    Collects data and meta into matrices while processing them through processing chains.

    Parameters
    ----------
    item_list : list or dict
        Items in the data sequence. List containing multi-level dictionary with first level key
        'data' and 'meta'. Second level should contain parameters for process method in the processing chain.
        Default value None

    data_processing_chain : ProcessingChain
        Data processing chain.
        Default value None

    meta_processing_chain : ProcessingChain
        Meta processing chain.
        Default value None

    channel_dimension : str
        Controls where channel dimension should be added. Similar to Keras data format parameter.
        If None given, no channel dimension is added.
        Possible values [None, 'channels_first', 'channels_last']
        Default value None

    target_format : str
        Meta data interpretation in the relation to the data items.
        Possible values ['same', 'single_target_per_segment']
        Default value 'single_target_per_segment'

    verbose : bool
        Print information about the data
        Default value True

    print_indent : int
        Default value 2

    Returns
    -------
    numpy.ndarray
        data

    numpy.ndarray
        meta

    dict
        data size information

    """

    if item_list:
        # Collect all data and meta
        X = []
        Y = []

        for item in item_list:
            data = data_processing_chain.process(**item['data'])
            meta = meta_processing_chain.process(**item['meta'])

            X.append(data.data)

            # Collect meta
            if target_format == 'single_target_per_sequence':
                # Collect single target per sequence
                for i in range(0, data.shape[data.sequence_axis]):
                    Y.append(meta.data[:, 0])

            elif target_format == 'same':
                # Collect same target per each element (frame)
                if data.time_axis != meta.time_axis:
                    Y.append(
                        numpy.repeat(
                            a=meta.data,
                            repeats=data.length,
                            axis=meta.time_axis
                        ).T
                    )

                else:
                    Y.append(
                        numpy.repeat(
                            a=meta.data,
                            repeats=data.length,
                            axis=meta.time_axis
                        )
                    )

        data_size = {}

        if len(data.shape) == 2:
            # Stack collected data and meta correct way
            if data.time_axis == 0:
                X = numpy.vstack(X)
                Y = numpy.vstack(Y)

            else:
                X = numpy.hstack(X)
                Y = numpy.hstack(Y)

            # Get data item size
            data_size = {
                'data': X.shape[data.data_axis],
                'time': X.shape[data.time_axis],
            }
            data_axis = [None] * 2
            data_axis[data.data_axis] = 'data'
            data_axis[data.time_axis] = 'time'

        elif len(data.shape) == 3:
            # Stack collected data and meta correct way
            if data.sequence_axis == 0:
                X = numpy.vstack(X)
                Y = numpy.vstack(Y)

            elif data.sequence_axis == 1:
                X = numpy.hstack(X)
                Y = numpy.hstack(Y)

            elif data.sequence_axis == 2:
                X = numpy.dstack(X)
                Y = numpy.dstack(Y)

            # Get data item size
            data_size = {
                'data': X.shape[data.data_axis],
                'time': X.shape[data.time_axis],
                'sequence': X.shape[data.sequence_axis],
            }
            data_axis = [None] * 3
            data_axis[data.data_axis] = 'data'
            data_axis[data.time_axis] = 'time'
            data_axis[data.sequence_axis] = 'sequence'

            if channel_dimension:
                # Add channel dimension to the data
                if channel_dimension == 'channels_first':
                    X = numpy.expand_dims(X, axis=1)
                    data_axis.insert(1, 'channel')
                elif channel_dimension == 'channels_last':
                    X = numpy.expand_dims(X, axis=3)
                    data_axis.insert(3, 'channel')

        if verbose:
            data_shape = data.shape
            data_axis_ = {
                'time_axis': data.time_axis,
                'data_axis': data.data_axis
            }

            if hasattr(data, 'sequence_axis'):
                data_axis_['sequence_axis'] = data.sequence_axis

            meta_shape = meta.shape
            meta_axis = {
                'time_axis': meta.time_axis,
                'data_axis': meta.data_axis
            }

            if hasattr(meta, 'sequence_axis'):
                meta_axis['sequence_axis'] = meta.sequence_axis

            logger = FancyLogger()

            # Data information
            logger.line('Data', indent=print_indent)

            # Matrix
            logger.data(
                field='Matrix shape',
                value=X.shape,
                indent=print_indent + 2
            )

            # Item
            logger.data(
                field='Item shape',
                value=data_shape,
                indent=print_indent + 2
            )

            logger.data(
                field='Time',
                value=data_shape[data_axis_['time_axis']],
                indent=print_indent + 4
            )

            logger.data(
                field='Data',
                value=data_shape[data_axis_['data_axis']],
                indent=print_indent + 4
            )

            if 'sequence_axis' in data_axis_:
                logger.data(
                    field='Sequence',
                    value=data_shape[data_axis_['sequence_axis']],
                    indent=print_indent + 4
                )

            # Meta information
            logger.line('Meta', indent=print_indent)

            # Matrix
            logger.data(
                field='Matrix shape',
                value=Y.shape,
                indent=print_indent + 2
            )

            # Item
            logger.data(
                field='Item shape',
                value=meta_shape,
                indent=print_indent + 2
            )
            logger.data(
                field='Time',
                value=meta_shape[meta_axis['time_axis']],
                indent=print_indent + 4
            )

            logger.data(
                field='Data',
                value=meta_shape[meta_axis['data_axis']],
                indent=print_indent + 4
            )

            if 'sequence_axis' in meta_axis:
                logger.data(
                    field='Sequence',
                    value=meta_shape[meta_axis['sequence_axis']],
                    indent=print_indent + 4
                )

        return X, Y, data_size
