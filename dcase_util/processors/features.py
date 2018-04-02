#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import copy
from dcase_util.containers import FeatureContainer, FeatureRepository
from dcase_util.features import MelExtractor, MfccStaticExtractor, MfccDeltaExtractor, \
    MfccAccelerationExtractor, ZeroCrossingRateExtractor, RMSEnergyExtractor, SpectralCentroidExtractor
from dcase_util.processors import Processor, ProcessingChainItemType, ProcessingChain
from dcase_util.utils import get_class_inheritors


class FeatureReadingProcessor(Processor):
    input_type = ProcessingChainItemType.NONE  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(FeatureReadingProcessor, self).__init__(*args, **kwargs)

    def process(self,
                data=None, filename=None,
                focus_start=None, focus_stop=None, focus_duration=None,
                focus_start_seconds=None, focus_stop_seconds=None, focus_duration_seconds=None,
                store_processing_chain=False,
                **kwargs):
        """Meta data reading.

        Parameters
        ----------
        data : FeatureContainer
            Input feature data

        filename : str
            Filename of the feature container to load.

        focus_start : int, optional
            Segment start, frame index of focus segment start

        focus_stop : int, optional
            Segment end, Frame index of focus segment stop

        focus_duration : int, optional
            Segment duration, Frame count of focus segment

        focus_start_seconds : float > 0.0
            Segment start, seconds

        focus_stop_seconds : float > 0.0
            Segment end, seconds

        focus_duration_seconds : float
            Segment duration, seconds

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        self

        """

        if data is None and self.input_type == ProcessingChainItemType.NONE:
            container = FeatureContainer()

            if filename:
                # Load features from disk
                container.load(
                    filename=filename
                )

            if focus_start is not None and focus_duration is not None:
                # Set focus segment and channel
                container.set_focus(
                    start=focus_start,
                    duration=focus_duration
                )

            elif focus_start is not None and focus_stop is not None:
                # Set focus segment and channel
                container.set_focus(
                    start=focus_start,
                    stop=focus_stop
                )

            elif focus_start_seconds is not None and focus_duration_seconds is not None:
                # Set focus segment and channel
                container.set_focus(
                    start_seconds=focus_start_seconds,
                    duration_seconds=focus_duration_seconds
                )

            elif focus_start_seconds is not None and focus_stop_seconds is not None:
                # Set focus segment and channel
                container.set_focus(
                    start_seconds=focus_start_seconds,
                    stop_seconds=focus_stop_seconds
                )

            if store_processing_chain and not container.processing_chain:
                # Insert Reader processor only if processing chain is empty
                processing_chain_item = self.get_processing_chain_item()

                if 'process_parameters' not in processing_chain_item:
                    processing_chain_item['process_parameters'] = {}

                processing_chain_item['process_parameters']['filename'] = filename
                processing_chain_item['process_parameters']['focus_start'] = focus_start
                processing_chain_item['process_parameters']['focus_duration'] = focus_duration
                processing_chain_item['process_parameters']['focus_start'] = focus_start
                processing_chain_item['process_parameters']['focus_stop'] = focus_stop
                processing_chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
                processing_chain_item['process_parameters']['focus_duration_seconds'] = focus_duration_seconds
                processing_chain_item['process_parameters']['focus_start_seconds'] = focus_start_seconds
                processing_chain_item['process_parameters']['focus_stop_seconds'] = focus_stop_seconds

                container.push_processing_chain_item(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryFeatureReadingProcessor(Processor):
    input_type = ProcessingChainItemType.NONE  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(RepositoryFeatureReadingProcessor, self).__init__(*args, **kwargs)

    def process(self,
                data=None, filename=None,
                store_processing_chain=False,
                **kwargs):
        """Meta data reading.

        Parameters
        ----------
        data : FeatureContainer
            Input feature data
            Default value None

        filename : str
            Filename of the feature container to load.
            Default value None

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        self

        """

        if data is None and self.input_type == ProcessingChainItemType.NONE:
            container = FeatureRepository()
            if filename:
                container.load(
                    filename=filename
                )

            if store_processing_chain:
                processing_chain_item = self.get_processing_chain_item()

                if 'process_parameters' not in processing_chain_item:
                    processing_chain_item['process_parameters'] = {}

                processing_chain_item['process_parameters']['filename'] = filename

                container.push_processing_chain_item(**processing_chain_item)

            return container

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class FeatureExtractorProcessor(Processor):
    input_type = ProcessingChainItemType.AUDIO  #: Input data type
    output_type = ProcessingChainItemType.DATA_CONTAINER  #: Output data type

    def __init__(self, *args, **kwargs):
        """Constructor"""

        # Run super init to call init of mixins too
        super(FeatureExtractorProcessor, self).__init__(*args, **kwargs)

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Extract features

        Parameters
        ----------
        data : AudioContainer
            Audio data to extract features

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        FeatureContainer

        """

        from dcase_util.containers import FeatureContainer, AudioContainer

        if isinstance(data, AudioContainer):
            if store_processing_chain:
                if hasattr(data, 'processing_chain') and data.processing_chain.chain_item_exists(
                        processor_name='dcase_util.processors.' + self.__class__.__name__):
                    # Current processor is already in the processing chain, get that
                    processing_chain_item = data.processing_chain.chain_item(
                        processor_name='dcase_util.processors.' + self.__class__.__name__
                    )

                else:
                    # Create a new processing chain item
                    processing_chain_item = self.get_processing_chain_item()

                processing_chain_item.update({
                    'process_parameters': kwargs
                })

                if hasattr(data, 'processing_chain'):
                    data.processing_chain.push_processor(**processing_chain_item)
                    processing_chain = data.processing_chain

                else:
                    processing_chain = ProcessingChain().push_processor(**processing_chain_item)

            else:
                processing_chain = None

            return FeatureContainer(
                data=self.extract(y=data.get_focused()),
                time_resolution=self.hop_length_seconds,
                processing_chain=processing_chain
            )

        else:
            message = '{name}: Wrong input data type, type required [{input_type}].'.format(
                name=self.__class__.__name__,
                input_type=self.input_type)

            self.logger.exception(message)
            raise ValueError(message)


class RepositoryFeatureExtractorProcessor(Processor):
    input_type = ProcessingChainItemType.AUDIO  #: Input data type
    output_type = ProcessingChainItemType.DATA_REPOSITORY  #: Output data type

    def __init__(self, parameters=None, **kwargs):
        """Constructor

        Parameters
        ----------
        parameters : dict
            Extraction parameters, extractor label as key and parameters as value.

        """

        if parameters is None:
            parameters = {}

        kwargs.update(
            {
                'parameters': parameters
            }
        )

        # Run super init to call init of mixins too
        super(RepositoryFeatureExtractorProcessor, self).__init__(**kwargs)

        self.parameters = kwargs.get('parameters', {})

        self.label_to_class = {}
        for processor in get_class_inheritors(FeatureExtractorProcessor):
            self.label_to_class[processor.label] = processor

    def __getstate__(self):
        return {
            'parameters': self.parameters
        }

    def __setstate__(self, d):
        self.parameters = d['parameters']

        self.label_to_class = {}
        for processor in get_class_inheritors(FeatureExtractorProcessor):
            self.label_to_class[processor.label] = processor

    def process(self, data=None, store_processing_chain=False, **kwargs):
        """Extract features

        Parameters
        ----------
        data : AudioContainer
            Audio data to extract features

        store_processing_chain : bool
            Store processing chain to data container returned
            Default value False

        Returns
        -------
        FeatureRepository

        """

        from dcase_util.containers import FeatureRepository, AudioContainer

        if isinstance(data, AudioContainer):
            if store_processing_chain:
                if hasattr(data, 'processing_chain') and data.processing_chain.chain_item_exists(
                        processor_name='dcase_util.processors.' + self.__class__.__name__):
                    # Current processor is already in the processing chain, get that
                    processing_chain_item = data.processing_chain.chain_item(
                        processor_name='dcase_util.processors.' + self.__class__.__name__
                    )

                else:
                    # Create a new processing chain item
                    processing_chain_item = self.get_processing_chain_item()

                # Update current processing parameters into chain item
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

            # Create repository container
            repository = FeatureRepository(
                processing_chain=processing_chain
            )

            # Make local copy of data
            current_data = copy.deepcopy(data)

            if data.streams == 1:
                # We have single channel audio input
                for label, parameters in iteritems(self.parameters):
                    if label in self.label_to_class:
                        # Get processor
                        processor = self.label_to_class[label](**parameters)

                        # Reset processing chain
                        current_data.processing_chain = ProcessingChain()

                        # Extract features
                        extracted = processor.process(data=current_data)

                        repository.set_container(
                            container=extracted,
                            label=label
                        )

                    else:
                        message = '{name}: Unknown label [{label}], no corresponding class found.'.format(
                            name=self.__class__.__name__,
                            label=label)

                        self.logger.exception(message)
                        raise AssertionError(message)

            elif data.streams > 1:
                # We have multi-channel audio input
                for stream_id in range(0, data.streams):
                    for label, parameters in iteritems(self.parameters):
                        if label in self.label_to_class:
                            # Get processor
                            processor = self.label_to_class[label](**parameters)

                            # Reset processing chain
                            current_data.processing_chain = ProcessingChain()

                            # Set focus to the current stream
                            current_data.focus_channel = stream_id

                            # Extract features
                            extracted = processor.process(data=current_data)

                            # Add extracted features to the repository
                            repository.set_container(
                                container=extracted,
                                label=label,
                                stream_id=stream_id
                            )

                        else:
                            message = '{name}: Unknown label [{label}], no corresponding class found.'.format(
                                name=self.__class__.__name__,
                                label=label)

                            self.logger.exception(message)
                            raise AssertionError(message)

            return repository


class MelExtractorProcessor(FeatureExtractorProcessor, MelExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False, logarithmic=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.

        n_fft : int
            Length of the FFT window.

        window_type : str
            Window function type.

        n_mels : int
            Number of mel bands to generate

        fmin : int
            Lowest frequency in mel bands (in Hz)

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0

        htk : bool
            Use HTK formula for mel band creation instead of Slaney

        logarithmic : bool
            Switch for log mel-band energies

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'n_mels': n_mels,
            'fmin': fmin,
            'fmax': fmax,
            'normalize_mel_bands': normalize_mel_bands,
            'htk': htk,
            'logarithmic': logarithmic
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run MelExtractor init
        MelExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MelExtractorProcessor, self).__init__(**kwargs)


class MfccStaticExtractorProcessor(FeatureExtractorProcessor, MfccStaticExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mfcc=20, n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.

        n_fft : int
            Length of the FFT window.

        window_type : str
            Window function type.

        n_mels : int
            Number of mel bands to generate

        fmin : int
            Lowest frequency in mel bands (in Hz)

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0

        htk : bool
            Use HTK formula for mel band creation instead of Slaney

        n_mfcc : int
            Number of MFCC coefficients

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'n_mfcc': n_mfcc,
            'n_mels': n_mels,
            'fmin': fmin,
            'fmax': fmax,
            'normalize_mel_bands': normalize_mel_bands,
            'htk': htk
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run MfccStaticExtractor init
        MfccStaticExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MfccStaticExtractorProcessor, self).__init__(**kwargs)


class MfccDeltaExtractorProcessor(FeatureExtractorProcessor, MfccDeltaExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mfcc=20, n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 width=9,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.

        n_fft : int
            Length of the FFT window.

        window_type : str
            Window function type.

        n_mels : int
            Number of mel bands to generate.

        fmin : int
            Lowest frequency in mel bands (in Hz).

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0.

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0.

        htk : bool
            Use HTK formula for mel band creation instead of Slaney.

        n_mfcc : int
            Number of MFCC coefficients.

        width : int
            Width of the delta window.

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'n_mfcc': n_mfcc,
            'n_mels': n_mels,
            'fmin': fmin,
            'fmax': fmax,
            'normalize_mel_bands': normalize_mel_bands,
            'htk': htk,
            'width': width
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run MfccDeltaExtractor init
        MfccDeltaExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MfccDeltaExtractorProcessor, self).__init__(**kwargs)


class MfccAccelerationExtractorProcessor(FeatureExtractorProcessor, MfccAccelerationExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mfcc=20, n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 width=9,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.

        n_fft : int
            Length of the FFT window.

        window_type : str
            Window function type.

        n_mels : int
            Number of mel bands to generate.

        fmin : int
            Lowest frequency in mel bands (in Hz).

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0.

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0.

        htk : bool
            Use HTK formula for mel band creation instead of Slaney.

        n_mfcc : int
            Number of MFCC coefficients.

        width : int
            Width of the delta window.

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'n_mfcc': n_mfcc,
            'n_mels': n_mels,
            'fmin': fmin,
            'fmax': fmax,
            'normalize_mel_bands': normalize_mel_bands,
            'htk': htk,
            'width': width
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run MfccAccelerationExtractor init
        MfccAccelerationExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(MfccAccelerationExtractorProcessor, self).__init__(**kwargs)


class ZeroCrossingRateExtractorProcessor(FeatureExtractorProcessor, ZeroCrossingRateExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 center=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        center : bool
            If True, frames are centered by padding the edges of signal.

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'center': center
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run ZeroCrossingRateExtractor init
        ZeroCrossingRateExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(ZeroCrossingRateExtractorProcessor, self).__init__(**kwargs)


class RMSEnergyExtractorProcessor(FeatureExtractorProcessor, RMSEnergyExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 center=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        center : bool
            If True, frames are centered by padding the edges of signal.

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'center': center
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run RMSEnergyExtractor init
        RMSEnergyExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(RMSEnergyExtractorProcessor, self).__init__(**kwargs)


class SpectralCentroidExtractorProcessor(FeatureExtractorProcessor, SpectralCentroidExtractor):
    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 center=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.

        win_length_samples : int
            Window length in samples.

        hop_length_samples : int
            Hop length in samples.

        win_length_seconds : float
            Window length in seconds.

        hop_length_seconds : float
            Hop length in seconds.

        center : bool
            If true, input signal is padded so to the frame is centered at hop length

        """

        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type,
            'center': center
        })

        # Run FeatureExtractorProcessor init
        FeatureExtractorProcessor.__init__(self, **kwargs)

        # Run SpectralCentroidExtractor init
        SpectralCentroidExtractor.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(SpectralCentroidExtractorProcessor, self).__init__(**kwargs)
