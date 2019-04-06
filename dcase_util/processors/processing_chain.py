#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import importlib
from dcase_util.containers import DictContainer, ListDictContainer
from dcase_util.ui import FancyLogger, FancyStringifier
from dcase_util.utils import FileFormat


class ProcessingChainItemType(object):
    AUDIO = 'AUDIO'
    DATA_CONTAINER = 'DATA_CONTAINER'
    DATA_REPOSITORY = 'DATA_REPOSITORY'
    METADATA = 'METADATA'
    MATRIX = 'MATRIX'
    NONE = 'NONE'
    UNKNOWN = 'UNKNOWN'


class ProcessingChainItem(DictContainer):
    def __init__(self, *args, **kwargs):
        super(ProcessingChainItem, self).__init__(*args, **kwargs)

        self.processor_class = None
        # Initialize processor class
        self.init_processor_class()

    def __getstate__(self):
        d = super(ProcessingChainItem, self).__getstate__()
        return d

    def __setstate__(self, d):
        super(ProcessingChainItem, self).__setstate__(d)
        self.init_processor_class()

    def init_processor_class(self):
        """Initialize processor class

        Returns
        -------
        self

        """
        processor_name = self.get('processor_name')
        processor_init_parameters = self.get('init_parameters', {})
        if processor_name:
            try:
                # Get module
                if len(processor_name.split('.')) == 1:
                    processor_name = 'dcase_util.processors.' + processor_name

                processor_module = importlib.import_module('.'.join(processor_name.split('.')[:-1]))
                self.processor_class = eval('processor_module.' + processor_name.split('.')[-1])(**processor_init_parameters)

            except NameError:
                message = '{name}: Processor class was not found [{processor_name}]'.format(
                    name=self.__class__.__name__,
                    processor_name=processor_name
                )

                self.logger.exception(message)
                raise ValueError(message)

        return self


class ProcessingChain(ListDictContainer):
    valid_formats = [FileFormat.CPICKLE, FileFormat.YAML]  #: Valid formats
    valid_input_types = [
        ProcessingChainItemType.AUDIO,
        ProcessingChainItemType.DATA_CONTAINER,
        ProcessingChainItemType.DATA_REPOSITORY,
        ProcessingChainItemType.METADATA,
        ProcessingChainItemType.MATRIX,
        ProcessingChainItemType.NONE
    ]  #: Valid input data types
    valid_output_types = [
        ProcessingChainItemType.AUDIO,
        ProcessingChainItemType.DATA_CONTAINER,
        ProcessingChainItemType.DATA_REPOSITORY,
        ProcessingChainItemType.METADATA,
        ProcessingChainItemType.MATRIX,
        ProcessingChainItemType.NONE
    ]  #: Valid output data types

    def __init__(self, *args, **kwargs):
        """__init__ method.

        """

        if len(args) > 0 and args[0] and (not isinstance(args[0], list) or not isinstance(args[0][0], dict)):
            message = '{name}: ProcessingChain should be initialized with list of dicts.'.format(
                name=self.__class__.__name__,
            )
            self.logger.exception(message)
            raise ValueError(message)

        super(ProcessingChain, self).__init__(*args, **kwargs)

        # Make sure items are ProcessingChainItems and that their parameters are valid.
        if len(self):
            for item_id, item in enumerate(self):
                if not isinstance(item, ProcessingChainItem):
                    current_processor = self.processor_class_reference(
                        processor_name=item['processor_name']
                    )

                    from dcase_util.processors.processor import Processor
                    if not issubclass(current_processor, Processor):
                        message = '{name}: ProcessingChain items should be Processor classes, please check item [{item}].'.format(
                            name=self.__class__.__name__,
                            item=item['processor_name']
                        )
                        self.logger.exception(message)
                        raise ValueError(message)

                    item.update(
                        {
                            'input_type': current_processor.input_type,
                            'output_type': current_processor.output_type,
                        }
                    )
                    self._check_item(item)

                    if item_id > 0:
                        # Check connection from second item in the chain,
                        # check connecting data type to between current and previous item.
                        self._check_connection(
                            item1=self[item_id-1],
                            item2=item
                        )

                    # Store processing chain item
                    self[item_id] = ProcessingChainItem(item)

    def chain_string(self):
        """Basic info about the items in the chain.

        Returns
        -------
        str

        """

        output = ''

        ui = FancyStringifier()
        output += ui.row('ID', 'Processor', 'Input', 'Output', 'Init parameters set', widths=[5, 30, 18, 18, 50]) + '\n'
        output += ui.row('-', '-', '-', '-', '-') + '\n'
        if len(self):
            for item_id, item in enumerate(self):
                if isinstance(item, ProcessingChainItem):
                    current_processor = self.processor_class_reference(
                        processor_name=item['processor_name']
                    )
                    processor_name = item['processor_name'].split('.')[-1]

                    output += ui.row(
                        item_id,
                        processor_name,
                        current_processor.input_type,
                        current_processor.output_type,
                        ','.join(item.get('init_parameters', {}).keys())
                    ) + '\n'

        else:
            output += ui.row('Empty', widths=[95])

        return output

    def show_chain(self):
        """Show chain information."""
        print(self.chain_string())

    def log_chain(self, level='info'):
        """Log chain information

        Parameters
        ----------
        level : str
            Logging level, possible values [info, debug, warn, warning, error, critical]

        Returns
        -------
        Nothing

        """

        ui = FancyLogger()
        ui.line(data=self.chain_string(), level=level)

    def _check_item(self, item):
        """Check validity of processing chain item.

        Parameters
        ----------
        item : ProcessingChainItem
            processing chain item

        Returns
        -------
        ProcessingChainItem
            processing chain item
        """

        if 'init_parameters' in item and item['init_parameters'] is None:
            item['init_parameters'] = {}

        if 'process_parameters' in item and item['process_parameters'] is None:
            item['process_parameters'] = {}

        if 'input_type' in item:
            if set(item['input_type']) > set(self.valid_input_types):
                message = '{name}: Unknown process input type [{input_type}] for processor [{processor_name}]'.format(
                    name=self.__class__.__name__,
                    input_type=item['input_type'],
                    processor_name=item['processor_name'],
                )
                self.logger.exception(message)
                raise ValueError(message)

        if 'output_type' in item:
            if set(item['output_type']) > set(self.valid_output_types):
                message = '{name}: Unknown process output type [{output_type}] for processor [{processor_name}]'.format(
                    name=self.__class__.__name__,
                    output_type=item['output_type'],
                    processor_name=item['processor_name'],
                )
                self.logger.exception(message)
                raise ValueError(message)

        return item

    def _check_connection(self, item1, item2):
        """Check processing chain connection validity.

        Check that output type of item1 is an input type of item2.

        Parameters
        ----------
        item1 : ProcessingChainItem
            processing chain item

        item2 : ProcessingChainItem
            processing chain item

        Returns
        -------

        """

        # Get processor class reference to item1
        item1_processor = self.processor_class_reference(
            processor_name=item1['processor_name']
        )

        # Get processor class reference to item2
        item2_processor = self.processor_class_reference(
            processor_name=item2['processor_name']
        )

        # Make sure connecting types are same.
        if item1_processor.output_type != item2_processor.input_type:
            message = '{name}: Chain connection invalid between items [{item1}][{output_type}] -> [{item2}][{input_type}]'.format(
                name=self.__class__.__name__,
                item1=item1['processor_name'],
                item2=item1['processor_name'],
                output_type=item1_processor.output_type,
                input_type=item2_processor.input_type
            )

            self.logger.exception(message)
            raise ValueError(message)

    def processor_exists(self, processor_name):
        """Checks that processor exists in the chain.

        Parameters
        ----------
        processor_name : str
            processor name

        Returns
        -------
        bool

        """

        for processor in self:
            if processor.get('processor_name') == processor_name:
                return True

        return False

    def push_processor(self, processor_name,
                       init_parameters=None, process_parameters=None, preprocessing_callbacks=None,
                       input_type=None, output_type=None):
        """Push processor item to the chain, if item already exists in the processing chain update only parameters.
        Processor name is considered unique in the processing chain.

        Parameters
        ----------
        processor_name : str
            processor name

        init_parameters : dict
            Processor initialization parameters
            Default value None

        process_parameters : dict
            Parameters for the process method
            Default value None

        preprocessing_callbacks : list of dicts
            Default value None

        input_type : ProcessingChainItemType
            Input data type of the processor
            Default value None

        output_type : ProcessingChainItemType
            Output data type of the processor
            Default value None

        Returns
        -------
        self

        """

        if init_parameters is None:
            init_parameters = {}

        if process_parameters is None:
            process_parameters = {}

        if preprocessing_callbacks is None:
            preprocessing_callbacks = []

        if not self.chain_item_exists(processor_name=processor_name):
            if input_type is None:
                input_type = self.processor_class_reference(
                    processor_name=processor_name
                ).input_type

            if output_type is None:
                output_type = self.processor_class_reference(
                    processor_name=processor_name
                ).output_type

            # Create item
            item = ProcessingChainItem({
                'processor_name': processor_name,
                'init_parameters': init_parameters,
                'process_parameters': process_parameters,
                'preprocessing_callbacks': preprocessing_callbacks,
                'input_type': input_type,
                'output_type': output_type,
            })

            # Check item
            self._check_item(item=item)

            # If there is other items in the chain check connection to previous item.
            if len(self) > 0:
                self._check_connection(item1=self[-1], item2=item)

            self.append(item)

        else:
            # Update existing processing chain item
            item = self.chain_item(processor_name=processor_name)
            if init_parameters:
                item['init_parameters'].update(init_parameters)

            if process_parameters:
                item['process_parameters'].update(process_parameters)

            if preprocessing_callbacks:
                item['preprocessing_callbacks'] = preprocessing_callbacks

            if input_type:
                item['input_type'] = input_type

            if output_type:
                item['output_type'] = output_type

            # Check item
            self._check_item(item=item)

        return self

    def processor_class_reference(self, processor_name):
        """Processor class reference.

        Parameters
        ----------
        processor_name : str
            processor name

        Returns
        -------
        class reference

        """

        try:
            if len(processor_name.split('.')) == 1:
                processor_name = 'dcase_util.processors.' + processor_name

            processor_module = importlib.import_module('.'.join(processor_name.split('.')[:-1]))

            return eval('processor_module.' + processor_name.split('.')[-1])

        except NameError:
            message = '{name}: Processor class was not found [{processor_name}]'.format(
                name=self.__class__.__name__,
                processor_name=processor_name
            )

            self.logger.exception(message)
            raise ValueError(message)

    def processor_class(self, processor_name, **kwargs):
        """Processor class initialized.

        Parameters
        ----------
        processor_name : str
            processor name

        Returns
        -------
        class

        """

        try:
            # Get module
            if len(processor_name.split('.')) == 1:
                processor_name = 'dcase_util.processors.' + processor_name

            processor_module = importlib.import_module('.'.join(processor_name.split('.')[:-1]))

            return eval('processor_module.' + processor_name.split('.')[-1])(**kwargs)

        except NameError:
            message = '{name}: Processor class was not found [{processor_name}]'.format(
                name=self.__class__.__name__,
                processor_name=processor_name
            )

            self.logger.exception(message)
            raise ValueError(message)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process the data with processing chain

        Parameters
        ----------
        data : DataContainer
            Data

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        data : DataContainer
            Processed data

        """

        for step_id, step in enumerate(self):
            # Loop through steps in the processing chain

            if isinstance(step, ProcessingChainItem):

                if step_id == 0 and data is None:
                    # Inject data for the first item in the chain

                    if step.processor_class.input_type == ProcessingChainItemType.DATA_CONTAINER:
                        from dcase_util.containers import DataMatrix2DContainer
                        data = DataMatrix2DContainer(**kwargs).load()

                    elif step.processor_class.input_type == ProcessingChainItemType.DATA_REPOSITORY:
                        from dcase_util.containers import DataRepository
                        data = DataRepository(**kwargs).load()

                if 'preprocessing_callbacks' in step and isinstance(step['preprocessing_callbacks'], list):
                    # Handle pre-processing callbacks assigned to current processor

                    for method in step['preprocessing_callbacks']:
                        if isinstance(method, dict):
                            method_name = method.get('method_name')
                            method_parameters = method.get('parameters')
                            if hasattr(step.processor_class, method_name):
                                getattr(step.processor_class, method_name)(**method_parameters)

                if hasattr(step.processor_class, 'process'):
                    # Call process method of the processor if it exists

                    # Get process parameters from step
                    process_parameters = step.get('process_parameters', {})

                    # Update parameters with current parameters given
                    process_parameters.update(kwargs)

                    # Do actual processing
                    data = step.processor_class.process(
                        data=data,
                        store_processing_chain=store_processing_chain,
                        **process_parameters
                    )

        return data

    def call_method(self, method_name, parameters=None):
        """Call class method in the processing chain items

        Processing chain is gone through and given method is
        called to processing items having such method.

        Parameters
        ----------
        method_name : str
            Method name to call

        parameters : dict
            Parameters for the method

        Returns
        -------
        self

        """

        parameters = parameters or {}

        for step in self:
            if hasattr(step.processor_class, method_name):
                getattr(step.processor_class, method_name)(**parameters)

        return self

    def chain_item_exists(self, processor_name):
        """Check if item exists already in the chain

        Parameters
        ----------
        processor_name : str
            processor name

        Returns
        -------
        bool

        """

        for step_id, step in enumerate(self):
            if step.get('processor_name') == processor_name:
                return True

        return False

    def chain_item(self, processor_name):
        """Get item based processor_name from the processing chain. If processor is not found, None returned.

        Parameters
        ----------
        processor_name : str
            processor name

        Returns
        -------
        ProcessingChainItem

        """

        for step_id, step in enumerate(self):
            if step.get('processor_name') == processor_name:
                return step

        return None
