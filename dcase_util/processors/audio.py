#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from dcase_util.containers import AudioContainer
from dcase_util.processors import ProcessorMixin, ProcessingChainItemType


class AudioReadingProcessor(ProcessorMixin, AudioContainer):
    input_type = ProcessingChainItemType.NONE  #: Input data type
    output_type = ProcessingChainItemType.AUDIO  #: Output data type

    def __init__(self, data=None, fs=44100,
                 focus_start_samples=None, focus_stop_samples=None, focus_channel=None, mono=False,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        data : DataContainer
            Data to initialize the container

        fs : int
            Target sampling rate when reading audio

        focus_start_samples : int
            Sample id of the focus segment start

        focus_stop_samples : int
            Sample id of the focus segment stop

        focus_channel : int or str
            Focus segment channel

        mono : bool
            Mixdown multi-channel audio in during the reading stage.

        """

        kwargs.update({
            'data': data,
            'fs': fs,
            'focus_start_samples': focus_start_samples,
            'focus_stop_samples': focus_stop_samples,
            'focus_channel': focus_channel,
            'mono': mono
        })

        # Run ProcessorMixin init
        ProcessorMixin.__init__(self, **kwargs)

        # Run AudioContainer init
        AudioContainer.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(AudioReadingProcessor, self).__init__(**kwargs)

        self.mono = kwargs.get('mono', False)

    def __getstate__(self):
        d = super(AudioReadingProcessor, self).__getstate__()
        d.update({
            'fs': self.fs,
            'mono': self.mono,
            'filename': self.filename,
        })

        return d

    def __setstate__(self, d):
        super(AudioReadingProcessor, self).__setstate__(d)

        self.fs = d['fs']
        self.mono = d['mono']
        self.filename = d['filename']

    def process(self, data=None, filename=None,
                focus_start_samples=None, focus_stop_samples=None, focus_duration_samples=None,
                focus_start_seconds=None, focus_stop_seconds=None, focus_duration_seconds=None,
                focus_channel=None,
                **kwargs):
        """Audio reading

        Parameters
        ----------
        data :

        filename : str
            Filename

        focus_start_samples : int
            Sample index of focus segment start

        focus_stop_samples : int
            Sample index of focus segment stop

        focus_duration_samples : int
            Sample count of focus segment

        focus_start_seconds : float
            Time stamp (in seconds) of focus segment start

        focus_stop_seconds : float
            Time stamp (in seconds) of focus segment stop

        focus_duration_seconds : float
            Duration (in seconds) of focus segment

        focus_channel : int or str
            Audio channel id or name to focus. In case of stereo signal, valid channel labels to select
            single channel are 'L', 'R', 'left', and 'right' or 0, 1, and to get mixed down version
            of all channels 'mixdown'.

        Returns
        -------
        AudioContainer

        """

        if data is None and self.input_type == ProcessingChainItemType.NONE:
            chain_item = self.get_processing_chain_item()

            if filename:
                self.load(filename=filename, mono=self.mono, fs=self.fs)

                if 'process_parameters' not in chain_item:
                    chain_item['process_parameters'] = {}

                chain_item['process_parameters']['filename'] = filename

            # Set focus segment and channel
            self.set_focus(
                start=focus_start_samples,
                stop=focus_stop_samples,
                duration=focus_duration_samples,
                start_seconds=focus_start_seconds,
                stop_seconds=focus_stop_seconds,
                duration_seconds=focus_duration_seconds,
                channel=focus_channel
            )
            chain_item['process_parameters']['focus_start_samples'] = focus_start_samples
            chain_item['process_parameters']['focus_stop_samples'] = focus_stop_samples
            chain_item['process_parameters']['focus_duration_samples'] = focus_duration_samples

            chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
            chain_item['process_parameters']['focus_stop_seconds'] = focus_stop_seconds
            chain_item['process_parameters']['focus_duration_seconds'] = focus_duration_seconds

            chain_item['process_parameters']['focus_channel'] = focus_channel

            self.push_processing_chain_item(**chain_item)

            return self

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class MonoAudioReadingProcessor(AudioReadingProcessor):
    input_type = ProcessingChainItemType.NONE  #: Input data type
    output_type = ProcessingChainItemType.AUDIO  #: Output data type

    def __init__(self,
                 data=None, fs=44100,
                 focus_start_samples=None, focus_stop_samples=None, focus_channel=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        data : DataContainer
            Data to initialize the container

        fs : int
            Target sampling rate when reading audio

        focus_start_samples : int
            Sample id of the focus segment start

        focus_stop_samples : int
            Sample id of the focus segment stop

        focus_channel : int or str
            Focus segment channel

        mono : bool
            Mixdown multi-channel audio in during the reading stage.

        """

        kwargs.update({
            'data': data,
            'fs': fs,
            'focus_start_samples': focus_start_samples,
            'focus_stop_samples': focus_stop_samples,
            'focus_channel': focus_channel,
            'mono': True
        })

        # Run AudioReadingProcessor init
        AudioReadingProcessor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MonoAudioReadingProcessor, self).__init__(**kwargs)
