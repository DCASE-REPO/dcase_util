#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
from six import iteritems

from dcase_util.containers import DataMatrix2DContainer, DataRepository
from dcase_util.utils import FileFormat


class FeatureContainer(DataMatrix2DContainer):
    """Feature container class for a single feature matrix, inherited from DataContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataMatrix2DContainer init
        DataMatrix2DContainer.__init__(self, **kwargs)

        # Run super init
        super(FeatureContainer, self).__init__(**kwargs)

    @property
    def hop_length_seconds(self):
        return self.time_resolution

    @hop_length_seconds.setter
    def hop_length_seconds(self, value):
        self.time_resolution = value


class FeatureRepository(DataRepository):
    """Feature repository container class to store multiple FeatureContainers together.

    Feature containers for each method are stored in a dict. Method label is used as dictionary key.

    """

    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, filename_dict=None, default_stream_id=0, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename_dict: dict
            Dict of file paths, feature extraction method label as key, and filename as value.
            If given, features are loaded in the initialization stage.

        default_stream_id : int

        processing_chain : ProcessingChain


        """
        kwargs.update({
            'filename_dict': filename_dict,
            'default_stream_id': default_stream_id,
            'processing_chain': processing_chain
        })

        super(FeatureRepository, self).__init__(**kwargs)

        self.item_class = FeatureContainer
