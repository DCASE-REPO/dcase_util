#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import logging
from dcase_util.containers import ObjectContainer
from dcase_util.utils import setup_logging
from dcase_util.processors import ProcessingChainItem


class Processor(ObjectContainer):
    """Data processing chain unit mixin"""
    def __init__(self, *args, **kwargs):

        self.init_parameters = kwargs

        if not hasattr(self, 'input_type'):
            self.input_type = None

        if not hasattr(self, 'output_type'):
            self.output_type = None

        # Run super init to call init of mixins too
        super(Processor, self).__init__(**kwargs)

    def __getstate__(self):
        d = super(Processor, self).__getstate__()
        d.update({
            'input_type': self.input_type,
            'output_type': self.output_type,
        })

        return d

    def __setstate__(self, d):
        super(Processor, self).__setstate__(d)

        self.input_type = d['input_type']
        self.output_type = d['output_type']

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)

    @property
    def logger(self):
        """Logger instance"""

        logger = logging.getLogger(__name__)

        if not logger.handlers:
            setup_logging()

        return logger

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Process data

        Parameters
        ----------
        data :
            Data to be processed.

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        """

        return data

    def get_processing_chain_item(self):
        """Get processing chain item with current Processor data.

        Returns
        -------
        ProcessingChainItem

        """

        init_parameters = self.init_parameters

        return ProcessingChainItem({
            'processor_name': 'dcase_util.processors.'+self.__class__.__name__,
            'init_parameters': init_parameters,
            'input_type': self.input_type,
            'output_type': self.output_type,
        })
