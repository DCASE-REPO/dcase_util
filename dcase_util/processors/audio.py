#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import copy
from dcase_util.containers import AudioContainer
from dcase_util.processors import Processor, ProcessingChainItemType, ProcessingChain


class AudioReadingProcessor(Processor):
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

        # Inject initialization parameters back to kwargs
        kwargs.update(
            {
                'data': data,
                'fs': fs,
                'focus_start_samples': focus_start_samples,
                'focus_stop_samples': focus_stop_samples,
                'focus_channel': focus_channel,
                'mono': mono
            }
        )

        # Run super init to call init of mixins too
        super(AudioReadingProcessor, self).__init__(**kwargs)

    def process(self, data=None, filename=None,
                focus_start_samples=None, focus_stop_samples=None, focus_duration_samples=None,
                focus_start_seconds=None, focus_stop_seconds=None, focus_duration_seconds=None,
                focus_channel=None,
                store_processing_chain=False,
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

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        AudioContainer

        """

        if data is None and self.input_type == ProcessingChainItemType.NONE:
            audio_container = AudioContainer(**self.init_parameters)

            if filename:
                audio_container.load(
                    filename=filename,
                    mono=self.init_parameters.get('mono')
                )

            # Set focus segment and channel
            audio_container.set_focus(
                start=focus_start_samples,
                stop=focus_stop_samples,
                duration=focus_duration_samples,
                start_seconds=focus_start_seconds,
                stop_seconds=focus_stop_seconds,
                duration_seconds=focus_duration_seconds,
                channel=focus_channel
            )

            if store_processing_chain:
                processing_chain_item = self.get_processing_chain_item()

                if 'process_parameters' not in processing_chain_item:
                    processing_chain_item['process_parameters'] = {}

                processing_chain_item['process_parameters']['filename'] = filename

                processing_chain_item['process_parameters']['focus_start_samples'] = focus_start_samples
                processing_chain_item['process_parameters']['focus_stop_samples'] = focus_stop_samples
                processing_chain_item['process_parameters']['focus_duration_samples'] = focus_duration_samples

                processing_chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
                processing_chain_item['process_parameters']['focus_stop_seconds'] = focus_stop_seconds
                processing_chain_item['process_parameters']['focus_duration_seconds'] = focus_duration_seconds

                processing_chain_item['process_parameters']['focus_channel'] = focus_channel

                # Push chain item into processing chain stored in the container

                # Create processing chain to be stored in the container, and push chain item into it
                if hasattr(audio_container, 'processing_chain'):
                    audio_container.processing_chain.push_processor(**processing_chain_item)

                else:
                    audio_container.processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            return audio_container

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

        kwargs.update(
            {
                'data': data,
                'fs': fs,
                'focus_start_samples': focus_start_samples,
                'focus_stop_samples': focus_stop_samples,
                'focus_channel': focus_channel,
                'mono': True
            }
        )

        # Run AudioReadingProcessor init
        AudioReadingProcessor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MonoAudioReadingProcessor, self).__init__(**kwargs)


class AudioWritingProcessor(Processor):
    input_type = ProcessingChainItemType.AUDIO  #: Input data type
    output_type = ProcessingChainItemType.NONE  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(AudioWritingProcessor, self).__init__(*args, **kwargs)

    def process(self, data=None, output_filename=None,
                bit_depth=16, bit_rate=None,
                **kwargs):
        """Audio writing

        Parameters
        ----------
        data :

        output_filename : str
            Filename

        bit_depth : int, optional
            Bit depth for audio.
            Default value 16

        bit_rate : int, optional
            Bit rate for compressed audio formats.
            Default value None

        Returns
        -------
        AudioContainer

        """

        if data and isinstance(data, AudioContainer):
            audio_container = copy.deepcopy(data)

            if output_filename:
                audio_container.save(
                    filename=output_filename,
                    bit_depth=bit_depth,
                    bit_rate=bit_rate
                )

            return audio_container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type
            )

            self.logger.exception(message)
            raise ValueError(message)


class MonoAudioWritingProcessor(Processor):
    input_type = ProcessingChainItemType.AUDIO  #: Input data type
    output_type = ProcessingChainItemType.NONE  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(MonoAudioWritingProcessor, self).__init__(*args, **kwargs)

    def process(self, data=None, output_filename=None,
                bit_depth=16, bit_rate=None,
                **kwargs):
        """Audio writing

        Parameters
        ----------
        data :

        output_filename : str
            Filename

        bit_depth : int, optional
            Bit depth for audio.
            Default value 16

        bit_rate : int, optional
            Bit rate for compressed audio formats.
            Default value None

        Returns
        -------
        AudioContainer

        """

        if data and isinstance(data, AudioContainer):
            audio_container = copy.deepcopy(data)

            audio_container.mixdown()

            if output_filename:
                audio_container.save(
                    filename=output_filename,
                    bit_depth=bit_depth,
                    bit_rate=bit_rate
                )

            return audio_container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type
            )

            self.logger.exception(message)
            raise ValueError(message)

