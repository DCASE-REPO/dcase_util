#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import importlib
from dcase_util.containers import DictContainer, ListDictContainer
from dcase_util.ui import FancyLogger, FancyStringifier


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


class ProcessingChain(ListDictContainer):
    valid_formats = ['cpickle', 'yaml']  #: Valid formats
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
        super(ProcessingChain, self).__init__(*args, **kwargs)

        # Make sure items are ProcessingChainItems and that their parameters are valid.
        if len(self):
            for item_id, item in enumerate(self):
                if not isinstance(item, ProcessingChainItem):
                    current_processor = self.processor_class_reference(processor_name=item['processor_name'])
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
                        self._check_connection(item1=self[item_id-1], item2=item)

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
        output += ui.row('ID', 'Processor', 'INPUT', 'OUTPUT', 'INIT', widths=[5, 55, 10, 10, 15]) + '\n'
        output += ui.row('-', '-', '-', '-', '-') + '\n'
        if len(self):
            for item_id, item in enumerate(self):
                if isinstance(item, ProcessingChainItem):
                    current_processor = self.processor_class_reference(processor_name=item['processor_name'])
                    output += ui.row(
                        item_id,
                        item['processor_name'],
                        current_processor.input_type,
                        current_processor.output_type,
                        item.get('init_parameters')
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
        ui.line(self.chain_string(), level=level)

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
        item1_processor = self.processor_class_reference(processor_name=item1['processor_name'])

        # Get processor class reference to item2
        item2_processor = self.processor_class_reference(processor_name=item2['processor_name'])

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

    def push_processor(self, processor_name, init_parameters=None, process_parameters=None,
                       input_type=None, output_type=None):
        """Push processor item to the chain.

        Parameters
        ----------
        processor_name : str
            processor name

        init_parameters : dict
            Processor initialization parameters

        process_parameters : dict
            Parameters for the process method

        input_type : ProcessingChainItemType
            Input data type of the processor

        output_type : ProcessingChainItemType
            Output data type of the processor

        Returns
        -------
        self

        """

        if input_type is None:
            input_type = self.processor_class_reference(processor_name=processor_name).input_type

        if output_type is None:
            output_type = self.processor_class_reference(processor_name=processor_name).output_type

        # Create item
        item = ProcessingChainItem({
            'processor_name': processor_name,
            'init_parameters': init_parameters,
            'process_parameters': process_parameters,
            'input_type': input_type,
            'output_type': output_type,
        })

        # Check item
        self._check_item(item=item)

        # If there is other items in the chain check connection to previous item.
        if len(self) > 0:
            self._check_connection(item1=self[-1], item2=item)

        self.append(item)
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
            processor_module = importlib.import_module('.'.join(processor_name.split('.')[:-1]))
            return eval('processor_module.' + processor_name.split('.')[-1])(**kwargs)

        except NameError:
            message = '{name}: Processor class was not found [{processor_name}]'.format(
                name=self.__class__.__name__,
                processor_name=processor_name
            )

            self.logger.exception(message)
            raise ValueError(message)

    def process(self, data=None, **kwargs):
        """Process the data with processing chain

        Parameters
        ----------
        data : FeatureContainer
            Data

        Returns
        -------
        data : FeatureContainer
            Processed data

        """

        for step_id, step in enumerate(self):
            if step is not None and 'processor_name' in step:
                processor = self.processor_class(processor_name=step['processor_name'], **step['init_parameters'])

                if step_id == 0 and data is None:
                    # Inject data for the first item in the chain

                    if processor.input_type == ProcessingChainItemType.DATA_CONTAINER:
                        from dcase_util.containers import DataMatrix2DContainer
                        data = DataMatrix2DContainer(**kwargs).load()

                    elif processor.input_type == ProcessingChainItemType.DATA_REPOSITORY:
                        from dcase_util.containers import DataRepository
                        data = DataRepository(**kwargs).load()

                if hasattr(processor, 'process'):
                    process_parameters = step.get('process_parameters', {})
                    process_parameters.update(kwargs)
                    data = processor.process(data=data, **process_parameters)

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

        """

        parameters = parameters or {}

        for item in self:
            if hasattr(item, method_name):
                getattr(item, method_name)(**parameters)

        return self
