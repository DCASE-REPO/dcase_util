#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

from dcase_util.containers import MetaDataContainer
from dcase_util.processors import Processor, ProcessingChainItemType


class MetadataReadingProcessor(Processor):
    input_type = ProcessingChainItemType.NONE  #: Input data type
    output_type = ProcessingChainItemType.METADATA  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(MetadataReadingProcessor, self).__init__(*args, **kwargs)

    def process(self,
                data=None, filename=None,
                focus_filename=None, focus_start_seconds=None, focus_stop_seconds=None, focus_duration_seconds=None,
                zero_time=None, trim=None,
                store_processing_chain=False,
                **kwargs):
        """Meta data reading.

        Parameters
        ----------
        data : MetaDataContainer
            Input meta data

        filename : str
            Filename of the meta data container to load.

        focus_start_seconds : float > 0.0
            Segment start, seconds

        focus_stop_seconds : float > 0.0
            Segment end, seconds

        focus_duration_seconds : float
            Segment duration, seconds

        focus_filename : str
            Filename to filter

        zero_time : bool
            Convert timestamps in respect to the segment start

        trim : bool
            Trim event onsets and offset according to segment start and stop times.

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        """

        if data is None and self.input_type == ProcessingChainItemType.NONE:
            container = MetaDataContainer()
            if filename:
                container.load(filename=filename)

            if focus_filename is not None:
                filtered = container.filter(filename=focus_filename)
                container.update(filtered)

            if focus_start_seconds is not None and focus_duration_seconds is not None:
                filtered = container.filter_time_segment(
                    start=focus_start_seconds,
                    duration=focus_duration_seconds,
                    zero_time=zero_time,
                    trim=trim
                )
                container.update(filtered)

            elif focus_start_seconds is not None and focus_stop_seconds is not None:
                filtered = container.filter_time_segment(
                    start=focus_start_seconds,
                    stop=focus_stop_seconds,
                    zero_time=zero_time,
                    trim=trim
                )
                container.update(filtered)

            if store_processing_chain:
                processing_chain_item = self.get_processing_chain_item()

                if 'process_parameters' not in processing_chain_item:
                    processing_chain_item['process_parameters'] = {}

                processing_chain_item['process_parameters']['filename'] = filename
                processing_chain_item['process_parameters']['focus_filename'] = focus_filename
                processing_chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
                processing_chain_item['process_parameters']['focus_duration_seconds'] = focus_duration_seconds
                processing_chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
                processing_chain_item['process_parameters']['focus_stop_seconds'] = focus_stop_seconds

                # Push chain item into processing chain stored in the container
                container.push_processing_chain_item(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)
