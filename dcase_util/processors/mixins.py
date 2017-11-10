#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import logging
from dcase_util.utils import setup_logging
from dcase_util.processors import ProcessingChain, ProcessingChainItem


class ProcessorMixin(object):
    """Data processing chain unit mixin"""
    def __init__(self, *args, **kwargs):
        self.processing_chain = kwargs.get('processing_chain', ProcessingChain())
        if not hasattr(self, 'input_type'):
            self.input_type = None

        if not hasattr(self, 'output_type'):
            self.output_type = None

    def __getstate__(self):
        d = super(ProcessorMixin, self).__getstate__()
        d.update({
            'processing_chain': self.processing_chain,
            'input_type': self.input_type,
            'output_type': self.output_type,
        })

        return d

    def __setstate__(self, d):
        super(ProcessorMixin, self).__setstate__(d)

        self.processing_chain = d['processing_chain']
        self.input_type = d['input_type']
        self.output_type = d['output_type']

    @property
    def logger(self):
        """Logger instance"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def process(self, data=None, **kwargs):
        """Process data

        Parameters
        ----------
        data :
            Data to be processed.

        """
        pass

    def get_processing_chain_item(self):
        """Get processing chain item with current Processor data.

        Returns
        -------
        ProcessingChainItem

        """

        init_parameters = self.__getstate__()

        # Remove some fields
        if 'processing_chain' in init_parameters:
            del init_parameters['processing_chain']
        if '_data' in init_parameters:
            del init_parameters['_data']

        if 'input_type' in init_parameters:
            del init_parameters['input_type']

        if 'output_type' in init_parameters:
            del init_parameters['output_type']

        return ProcessingChainItem({
            'processor_name': 'dcase_util.processors.'+self.__class__.__name__,
            'init_parameters': init_parameters,
            'input_type': self.input_type,
            'output_type': self.output_type,
        })

    def push_processing_chain_item(self,
                                   processor_name, init_parameters=None, process_parameters=None,
                                   input_type=None, output_type=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict
            Initialization parameters for the processors

        process_parameters : dict
            Parameters for the process method of the Processor

        input_type : ProcessingChainItemType
            Input data type

        output_type : ProcessingChainItemType
            Output data type

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters,
            input_type=input_type,
            output_type=output_type
        )

        return self
