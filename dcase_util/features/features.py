#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import numpy
import librosa
import scipy
import logging
import importlib
from dcase_util.containers import ContainerMixin
from dcase_util.ui import FancyStringifier, FancyHTMLStringifier
from dcase_util.utils import setup_logging, get_class_inheritors, is_jupyter


def feature_extractor_list(display=True):
    """List of feature extractors available

    Parameters
    ----------
    display : bool
        Display list immediately, otherwise return string
        Default value True

    Returns
    -------
    str
        Multi line string containing extractor table

    """

    class_list = get_class_inheritors(FeatureExtractor)
    class_list.sort(key=lambda x: x.__name__, reverse=False)
    class_names = []
    labels = []
    descriptions = []
    for extractor_class in class_list:
        if not extractor_class.__name__.endswith('Processor'):
            e = extractor_class()
            class_names.append(extractor_class.__name__)
            labels.append(e.label)
            descriptions.append(e.description)

    if is_jupyter():
        ui = FancyHTMLStringifier()

    else:
        ui = FancyStringifier()

    output = ui.table(
        cell_data=[class_names, labels, descriptions],
        column_headers=['Class name', 'Feature label', 'Description'],
        column_types=['str30', 'str20', 'str50'],
        column_separators=[0, 1]
    )

    if display:
        if is_jupyter():
            from IPython.core.display import display, HTML
            display(HTML(output))

        else:
            print(output)

    else:
        return output


def feature_extractor_factory(feature_extractor_label, **kwargs):
    """Function to get correct feature extractor class instance based on extractor label or class name.

    Parameters
    ----------
    feature_extractor_label : str
        Class name or extractor label

    Raises
    ------
    NameError
        Class does not exists

    Returns
    -------
    Feature extractor class instance

    """

    try:
        feature_extractor_class = None

        # Get all classes inherited from FeatureExtractor
        class_list = get_class_inheritors(FeatureExtractor)

        # Search correct feature extractor
        for item in class_list:
            if str(item.__name__) == feature_extractor_label:
                feature_extractor_class = getattr(
                    importlib.import_module(str(item.__module__)),
                    feature_extractor_label
                )
                break

            elif hasattr(item, 'label') and item.label == feature_extractor_label and item.__name__.endswith('Extractor'):
                feature_extractor_class = getattr(
                    importlib.import_module(str(item.__module__)),
                    item.__name__
                )
                break

        # Valid feature extractor class not found, raise error
        if not feature_extractor_class:
            raise AttributeError

    except AttributeError:

        message = 'Invalid FeatureExtractor class name or extractor label given [{label}].'.format(
            label=feature_extractor_label
        )
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        logger.exception(message)
        raise AttributeError(message)

    return feature_extractor_class(**dict(kwargs))


class FeatureExtractor(ContainerMixin):
    """Feature extractor base class"""
    label = 'extractor_base'  #: Extractor label
    description = 'Feature extractor base class' #: Extractor description

    def __init__(self, fs=44100,
                 win_length_samples=None, hop_length_samples=None,
                 win_length_seconds=0.04, hop_length_seconds=0.02, **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal

        win_length_samples : int
            Window length in samples

        hop_length_samples : int
            Hop length in samples

        win_length_seconds : float
            Window length in seconds

        hop_length_seconds : float
            Hop length in seconds

        """

        # Run ContainerMixin init
        ContainerMixin.__init__(self, **kwargs)

        self.eps = numpy.spacing(1)
        if fs is not None:
            self.fs = fs

        else:
            message = '{name}: No fs set'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        self.win_length_samples = win_length_samples
        self.hop_length_samples = hop_length_samples

        self.win_length_seconds = win_length_seconds
        self.hop_length_seconds = hop_length_seconds

        if not self.win_length_samples and self.win_length_seconds and self.fs:
            self.win_length_samples = int(self.fs * self.win_length_seconds)

        if not self.hop_length_samples and self.hop_length_seconds and self.fs:
            self.hop_length_samples = int(self.fs * self.hop_length_seconds)

        if self.win_length_samples is None:
            message = '{name}: No win_length_samples set'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if self.hop_length_samples is None:
            message = '{name}: No hop_length_samples set'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

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

        if hasattr(self, 'filename') and self.filename:
            output += FancyStringifier().data(field='filename', value=self.filename, indent=indent) + '\n'

        output += ui.data(field='fs', value=self.fs, indent=indent) + '\n'
        output += ui.line(field='Frame blocking', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='hop_length_samples', value=self.hop_length_samples) + '\n'
        output += ui.data(indent=indent + 2, field='hop_length_seconds', value=self.hop_length_seconds, unit='sec') + '\n'

        output += ui.data(indent=indent + 2, field='win_length_samples', value=self.win_length_samples) + '\n'
        output += ui.data(indent=indent + 2, field='win_length_seconds', value=self.win_length_seconds, unit='sec') + '\n'

        return output

    def __getstate__(self):
        # Return only needed data for pickle
        return {
            'eps': self.eps,
            'fs': self.fs,
            'win_length_samples': self.win_length_samples,
            'hop_length_samples': self.hop_length_samples,
            'win_length_seconds': self.win_length_seconds,
            'hop_length_seconds': self.hop_length_seconds
        }

    def __setstate__(self, d):
        self.eps = d['eps']
        self.fs = d['fs']
        self.win_length_samples = d['win_length_samples']
        self.hop_length_samples = d['hop_length_samples']
        self.win_length_seconds = d['win_length_seconds']
        self.hop_length_seconds = d['hop_length_seconds']

    def __call__(self, *args, **kwargs):
        return self.extract(*args, **kwargs)

    def extract(self, y):
        """Extract features for the audio signal (PLACEHOLDER).

        Parameters
        ----------
        y : AudioContainer or numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        None

        """

        pass


class SpectralFeatureExtractor(FeatureExtractor):
    """Spectral feature extractor base class"""
    label = 'spectrogram'  #: Extractor label
    description = 'Spectral feature extractor base class (Librosa)'  #: Extractor description

    def __init__(self, spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric', **kwargs):
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
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        """

        super(SpectralFeatureExtractor, self).__init__(**kwargs)

        # Run FeatureExtractor init
        FeatureExtractor.__init__(self, **kwargs)

        self.spectrogram_type = spectrogram_type
        self.n_fft = n_fft
        self.window_type = window_type

        self.window = self.get_window_function(
            n=self.win_length_samples,
            window_type=self.window_type
        )

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

        output = super(SpectralFeatureExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Spectrogram', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='spectrogram_type', value=self.spectrogram_type) + '\n'
        output += ui.data(indent=indent + 2, field='n_fft', value=self.n_fft) + '\n'
        output += ui.data(indent=indent + 2, field='window_type', value=self.window_type) + '\n'

        return output

    def get_window_function(self, n, window_type='hamming_asymmetric'):
        """Window function

        Parameters
        ----------
        n : int
            window length

        window_type : str
            window type
            Default value 'hamming_asymmetric'

        Raises
        ------
        ValueError:
            Unknown window type

        Returns
        -------
        numpy.array
            window function

        """

        # Windowing function
        if window_type == 'hamming_asymmetric':
            return scipy.signal.hamming(n, sym=False)

        elif window_type == 'hamming_symmetric' or window_type == 'hamming':
            return scipy.signal.hamming(n, sym=True)

        elif window_type == 'hann_asymmetric':
            return scipy.signal.hann(n, sym=False)

        elif window_type == 'hann_symmetric' or window_type == 'hann':
            return scipy.signal.hann(n, sym=True)

        else:
            message = '{name}: Unknown window type [{window_type}]'.format(
                name=self.__class__.__name__,
                window_type=window_type
            )

            self.logger.exception(message)
            raise ValueError(message)

    def get_spectrogram(self, y, n_fft=None, win_length_samples=None, hop_length_samples=None,
                        window=None, center=True, spectrogram_type=None):
        """Spectrogram

        Parameters
        ----------
        y : numpy.ndarray
            Audio data

        n_fft : int
            FFT size
            Default value 2048

        win_length_samples : int
            Window length in samples
            Default value None

        hop_length_samples : int
            Hop length in samples
            Default value None

        window : numpy.array
            Window function
            Default value None

        center : bool
            If true, input signal is padded so to the frame is centered at hop length
            Default value True

        spectrogram_type : str
            Type of spectrogram "magnitude" or "power"
            Default value None

        Returns
        -------
        numpy.ndarray [shape=(1 + n_fft/2, t), dtype=dtype]
            STFT matrix

        """

        if n_fft is None:
            n_fft = self.n_fft

        if win_length_samples is None:
            win_length_samples = self.win_length_samples

        if hop_length_samples is None:
            hop_length_samples = self.hop_length_samples

        if window is None and self.window is not None:
            window = self.window

        if spectrogram_type is None:
            spectrogram_type = self.spectrogram_type

        from dcase_util.containers import AudioContainer

        if isinstance(y, AudioContainer):
            if y.channels == 1:
                y = y.data

            else:
                message = '{name}: Input has more than one audio channel.'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise ValueError(message)

        if spectrogram_type == 'magnitude':
            return numpy.abs(librosa.stft(y + self.eps,
                                          n_fft=n_fft,
                                          win_length=win_length_samples,
                                          hop_length=hop_length_samples,
                                          center=center,
                                          window=window
                                          )
                             )
        elif spectrogram_type == 'power':
            return numpy.abs(librosa.stft(y + self.eps,
                                          n_fft=n_fft,
                                          win_length=win_length_samples,
                                          hop_length=hop_length_samples,
                                          center=center,
                                          window=window
                                          )) ** 2
        else:
            message = '{name}: Unknown spectrum type [{spectrogram_type}]'.format(
                name=self.__class__.__name__,
                spectrogram_type=spectrogram_type
            )

            self.logger.exception(message)
            raise ValueError(message)

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : AudioContainer or numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(n_fft, t)]
            spectrum
        """

        return self.get_spectrogram(
            y=y,
            n_fft=self.n_fft,
            win_length_samples=self.win_length_samples,
            hop_length_samples=self.hop_length_samples,
            spectrogram_type=self.spectrogram_type,
            center=True,
            window=self.window
        )


class MelExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract mel band energy features"""
    label = 'mel'  #: Extractor label
    description = 'Mel band energy (Librosa)'  #: Extractor description

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
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        n_mels : int
            Number of mel bands to generate
            Default value 40

        fmin : int
            Lowest frequency in mel bands (in Hz)
            Default value 0

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0
            Default value None

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0
            Default value False

        htk : bool
            Use HTK formula for mel band creation instead of Slaney
            Default value False

        logarithmic : bool
            Switch for log mel-band energies
            Default value True

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type
        })

        super(MelExtractor, self).__init__(**kwargs)

        # Run SpectralFeatureExtractor init
        SpectralFeatureExtractor.__init__(self, **kwargs)

        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax
        self.normalize_mel_bands = normalize_mel_bands
        self.htk = htk
        self.logarithmic = logarithmic

        self.mel_basis = librosa.filters.mel(
            sr=self.fs,
            n_fft=self.n_fft,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax,
            htk=self.htk
        )

        if self.normalize_mel_bands:
            self.mel_basis /= numpy.max(self.mel_basis, axis=-1)[:, None]

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

        output = super(MelExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Mel', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='n_mels', value=self.n_mels) + '\n'
        output += ui.data(indent=indent + 2, field='fmin', value=self.fmin) + '\n'
        output += ui.data(indent=indent + 2, field='fmax', value=self.fmax if self.fmax is not None else 'None') + '\n'
        output += ui.data(indent=indent + 2, field='normalize_mel_bands', value=self.normalize_mel_bands) + '\n'
        output += ui.data(indent=indent + 2, field='htk', value=self.htk) + '\n'
        output += ui.data(indent=indent + 2, field='logarithmic', value=self.logarithmic) + '\n'

        return output

    def __getstate__(self):
        d = super(MelExtractor, self).__getstate__()
        d.update({
            'n_mels': self.n_mels,
            'fmin': self.fmin,
            'fmax': self.fmax,
            'normalize_mel_bands': self.normalize_mel_bands,
            'htk': self.htk,
            'logarithmic': self.logarithmic,
        })

        return d

    def __setstate__(self, d):
        super(MelExtractor, self).__setstate__(d)

        self.n_mels = d['n_mels']
        self.fmin = d['fmin']
        self.fmax = d['fmax']
        self.normalize_mel_bands = d['normalize_mel_bands']
        self.htk = d['htk']
        self.logarithmic = d['logarithmic']

        self.mel_basis = librosa.filters.mel(
            sr=self.fs,
            n_fft=self.n_fft,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax,
            htk=self.htk
        )

        if self.normalize_mel_bands:
            self.mel_basis /= numpy.max(self.mel_basis, axis=-1)[:, None]

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : AudioContainer or numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(n_mels, t)]
            mel band energies
        """

        spectrogram = self.get_spectrogram(
            y=y,
            n_fft=self.n_fft,
            win_length_samples=self.win_length_samples,
            hop_length_samples=self.hop_length_samples,
            spectrogram_type=self.spectrogram_type,
            center=True,
            window=self.window
        )
        mel_spectrum = numpy.dot(self.mel_basis, spectrogram)

        if self.logarithmic:
            mel_spectrum = numpy.log(mel_spectrum + self.eps)

        return mel_spectrum


class MfccStaticExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract static MFCC features"""
    label = 'mfcc'  #: Extractor label
    description = 'MFCC (Librosa)'  #: Extractor description

    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 n_mfcc=20, omit_zeroth=False,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        n_mels : int
            Number of mel bands to generate.
            Default value 40

        fmin : int
            Lowest frequency in mel bands (in Hz).
            Default value 0

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0
            Default value None

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0
            Default value False

        htk : bool
            Use HTK formula for mel band creation instead of Slaney
            Default value False

        n_mfcc : int
            Number of MFCC coefficients
            Default value 20

        omit_zeroth : bool
            Omit 0th coefficient
            Default value False

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type
        })

        super(MfccStaticExtractor, self).__init__(**kwargs)

        # Run SpectralFeatureExtractor init
        SpectralFeatureExtractor.__init__(self, **kwargs)

        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax
        self.normalize_mel_bands = normalize_mel_bands
        self.htk = htk
        self.n_mfcc = n_mfcc
        self.omit_zeroth = omit_zeroth

        self.mel_basis = librosa.filters.mel(
            sr=self.fs,
            n_fft=self.n_fft,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax,
            htk=self.htk
        )

        if self.normalize_mel_bands:
            self.mel_basis /= numpy.max(self.mel_basis, axis=-1)[:, None]

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

        output = super(MfccStaticExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='MFCC', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='n_mels', value=self.n_mels) + '\n'
        output += ui.data(indent=indent + 2, field='fmin', value=self.fmin) + '\n'
        output += ui.data(indent=indent + 2, field='fmax', value=self.fmax) + '\n'
        output += ui.data(indent=indent + 2, field='normalize_mel_bands', value=self.normalize_mel_bands) + '\n'
        output += ui.data(indent=indent + 2, field='htk', value=self.htk) + '\n'
        output += ui.data(indent=indent + 2, field='n_mfcc', value=self.n_mfcc) + '\n'

        return output

    def __getstate__(self):
        d = super(MfccStaticExtractor, self).__getstate__()
        d.update({
            'n_mels': self.n_mels,
            'fmin': self.fmin,
            'fmax': self.fmax,
            'normalize_mel_bands': self.normalize_mel_bands,
            'htk': self.htk,
            'n_mfcc': self.n_mfcc,
            'omit_zeroth': self.omit_zeroth,
        })

        return d

    def __setstate__(self, d):
        super(MfccStaticExtractor, self).__setstate__(d)

        self.n_mels = d['n_mels']
        self.fmin = d['fmin']
        self.fmax = d['fmax']
        self.normalize_mel_bands = d['normalize_mel_bands']
        self.htk = d['htk']
        self.n_mfcc = d['n_mfcc']
        self.omit_zeroth = d['omit_zeroth']

        self.mel_basis = librosa.filters.mel(
            sr=self.fs,
            n_fft=self.n_fft,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax,
            htk=self.htk
        )

        if self.normalize_mel_bands:
            self.mel_basis /= numpy.max(self.mel_basis, axis=-1)[:, None]

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(n_mels, t)]
            mfccs

        """

        spectrogram = self.get_spectrogram(
            y=y,
            n_fft=self.n_fft,
            win_length_samples=self.win_length_samples,
            hop_length_samples=self.hop_length_samples,
            spectrogram_type=self.spectrogram_type,
            center=True,
            window=self.window
        )

        mel_spectrum = numpy.dot(self.mel_basis, spectrogram)
        mfccs = librosa.feature.mfcc(
            S=librosa.power_to_db(mel_spectrum),
            n_mfcc=self.n_mfcc
        )

        if self.omit_zeroth:
            # Remove first coefficient
            mfccs = mfccs[1:, :]

        return mfccs


class MfccDeltaExtractor(MfccStaticExtractor):
    """Feature extractor class to extract MFCC delta features"""
    label = 'mfcc_delta'  #: Extractor label
    description = 'MFCC delta (Librosa)'  #: Extractor description

    def __init__(self,
                 fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 n_mfcc=20, omit_zeroth=False,
                 width=9,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        n_mels : int
            Number of mel bands to generate.
            Default value 40

        fmin : int
            Lowest frequency in mel bands (in Hz).
            Default value 0

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0.
            Default value None

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0.
            Default value False

        htk : bool
            Use HTK formula for mel band creation instead of Slaney.
            Default value False

        n_mfcc : int
            Number of MFCC coefficients.
            Default value 20

        omit_zeroth : bool
            Omit 0th coefficient.
            Default value False

        width : int
            Width of the delta window.
            Default value 9

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
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
            'n_mfcc': n_mfcc,
            'omit_zeroth': omit_zeroth
        })

        super(MfccStaticExtractor, self).__init__(**kwargs)

        # Run MfccStaticExtractor init
        MfccStaticExtractor.__init__(self, **kwargs)

        self.width = width

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

        output = super(MfccDeltaExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Delta', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='width', value=self.width) + '\n'
        return output

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(1, t)]
            MFCC delta

        """

        mfccs = super(MfccDeltaExtractor, self).extract(y=y)
        return librosa.feature.delta(mfccs, width=self.width, order=1, axis=-1)


class MfccAccelerationExtractor(MfccStaticExtractor):
    """Feature extractor class to extract MFCC acceleration features"""
    label = 'mfcc_acceleration'  #: Extractor label
    description = 'MFCC acceleration (Librosa)'  #: Extractor description

    def __init__(self, fs=44100,
                 win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04, hop_length_seconds=0.02,
                 spectrogram_type='magnitude', n_fft=2048, window_type='hamming_asymmetric',
                 n_mels=40, fmin=0, fmax=None, normalize_mel_bands=False, htk=False,
                 n_mfcc=20, omit_zeroth=False,
                 width=9,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal.
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        n_mels : int
            Number of mel bands to generate.
            Default value 40

        fmin : int
            Lowest frequency in mel bands (in Hz).
            Default value 0

        fmax : int
            Highest frequency in mel bands (in Hz), if None, fmax = fs/2.0.
            Default value None

        normalize_mel_bands : bool
            Normalize mel band to have peak at 1.0.
            Default value False

        htk : bool
            Use HTK formula for mel band creation instead of Slaney.
            Default value False

        n_mfcc : int
            Number of MFCC coefficients.
            Default value 20

        omit_zeroth : bool
            Omit 0th coefficient.
            Default value False

        width : int
            Width of the delta window.
            Default value 9

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
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
            'n_mfcc': n_mfcc,
            'omit_zeroth': omit_zeroth
        })

        super(MfccAccelerationExtractor, self).__init__(**kwargs)

        # Run MfccStaticExtractor init
        MfccStaticExtractor.__init__(self, **kwargs)

        self.width = width

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

        output = super(MfccAccelerationExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='Acceleration', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='width', value=self.width) + '\n'
        return output

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(1, t)]
            MFCC acceleration

        """

        mfccs = super(MfccAccelerationExtractor, self).extract(y=y)
        return librosa.feature.delta(mfccs, width=self.width, order=2, axis=-1)


class ZeroCrossingRateExtractor(FeatureExtractor):
    """Feature extractor class to extract zero crossing rate features"""
    label = 'zcr'  #: Extractor label
    description = 'Zero crossing rate (Librosa)'  #: Extractor description

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
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        center : bool
            If True, frames are centered by padding the edges of signal.
            Default value True

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
        })

        super(ZeroCrossingRateExtractor, self).__init__(**kwargs)

        self.center = center

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

        output = super(ZeroCrossingRateExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='ZCR', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='center', value=self.center) + '\n'

        return output

    def __getstate__(self):
        d = super(ZeroCrossingRateExtractor, self).__getstate__()
        d.update({
            'center': self.center
        })

        return d

    def __setstate__(self, d):
        super(ZeroCrossingRateExtractor, self).__setstate__(d)

        self.center = d['center']

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(1, t)]
            zero crossing rate

        """

        from dcase_util.containers import AudioContainer
        if isinstance(y, AudioContainer):
            y = y.data

        return librosa.feature.zero_crossing_rate(
            y=y,
            frame_length=self.win_length_samples,
            hop_length=self.hop_length_samples,
            center=self.center
        ).reshape((1, -1))


class RMSEnergyExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract Root-mean-square energy features"""
    label = 'rmse'  #: Extractor label
    description = 'Root-mean-square energy (Librosa)'  #: Extractor description

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
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        center : bool
            If True, frames are centered by padding the edges of signal.
            Default value True

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type
        })

        # Run SpectralFeatureExtractor init
        SpectralFeatureExtractor.__init__(self, **kwargs)

        super(RMSEnergyExtractor, self).__init__(**kwargs)

        self.spectrogram_type = 'magnitude'
        self.center = center

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

        output = super(RMSEnergyExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='RMSEnergy', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='center', value=self.center) + '\n'

        return output

    def __getstate__(self):
        d = super(RMSEnergyExtractor, self).__getstate__()
        d.update({
            'center': self.center
        })

        return d

    def __setstate__(self, d):
        super(RMSEnergyExtractor, self).__setstate__(d)

        self.center = d['center']

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(1, t)]
            rmse

        """

        spectrogram = self.get_spectrogram(
            y=y,
            n_fft=self.n_fft,
            win_length_samples=self.win_length_samples,
            hop_length_samples=self.hop_length_samples,
            spectrogram_type=self.spectrogram_type,
            center=self.center,
            window=self.window
        )

        return librosa.feature.rms(
            S=spectrogram
        ).reshape((1, -1))


class SpectralCentroidExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract Centroid features"""
    label = 'centroid'  #: Extractor label
    description = 'Centroid (Librosa)'  #: Extractor description

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
            Default value 44100

        win_length_samples : int
            Window length in samples.
            Default value None

        hop_length_samples : int
            Hop length in samples.
            Default value None

        win_length_seconds : float
            Window length in seconds.
            Default value 0.04

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        spectrogram_type : str
            Spectrogram type, magnitude or power spectrogram.
            Default value 'magnitude'

        n_fft : int
            Length of the FFT window.
            Default value 2048

        window_type : str
            Window function type.
            Default value 'hamming_asymmetric'

        center : bool
            If true, input signal is padded so to the frame is centered at hop length
            Default value True

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': win_length_samples,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': win_length_seconds,
            'hop_length_seconds': hop_length_seconds,
            'spectrogram_type': spectrogram_type,
            'n_fft': n_fft,
            'window_type': window_type
        })

        # Run SpectralFeatureExtractor init
        SpectralFeatureExtractor.__init__(self, **kwargs)

        super(SpectralCentroidExtractor, self).__init__(**kwargs)

        self.spectrogram_type = 'magnitude'
        self.center = center

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

        output = super(SpectralCentroidExtractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='SpectralCentroid', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='center', value=self.center) + '\n'

        return output

    def __getstate__(self):
        d = super(SpectralCentroidExtractor, self).__getstate__()
        d.update({
            'center': self.center
        })

        return d

    def __setstate__(self, d):
        super(SpectralCentroidExtractor, self).__setstate__(d)

        self.center = d['center']

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        numpy.ndarray [shape=(1, t)]
            spectral centroid

        """
        spectrogram = self.get_spectrogram(
            y=y,
            n_fft=self.n_fft,
            win_length_samples=self.win_length_samples,
            hop_length_samples=self.hop_length_samples,
            spectrogram_type=self.spectrogram_type,
            center=self.center,
            window=self.window
        )

        return librosa.feature.spectral_centroid(
            S=spectrogram).reshape((1, -1))


class EmbeddingExtractor(FeatureExtractor):
    """Embedding extractor base class"""
    label = 'embedding'  #: Extractor label
    description = 'Embedding extractor base class'  #: Extractor description

    def __init__(self, **kwargs):
        """Constructor

        """

        super(EmbeddingExtractor, self).__init__(**kwargs)

        # Run FeatureExtractor init
        FeatureExtractor.__init__(self, **kwargs)


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

        output = super(EmbeddingExtractor, self).to_string(ui=ui, indent=indent)

        return output

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : AudioContainer or numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        None

        """

        pass


class OpenL3Extractor(EmbeddingExtractor):
    """OpenL3 Embedding extractor class"""
    label = 'openl3'  #: Extractor label
    description = 'OpenL3 (embedding)'  #: Extractor description

    def __init__(self, fs=48000, hop_length_samples=None, hop_length_seconds=0.02,
                 model=None, input_repr='mel256', content_type="music",
                 embedding_size=6144,
                 center=True, batch_size=32, verbose=False,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal. If not 48kHz audio will be resampled.
            Default value 48000

        hop_length_samples : int
            Hop length in samples.
            Default value None

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        model : keras.models.Model or None
            Loaded model object. If a model is provided, then `input_repr`, `content_type`, and `embedding_size` will be ignored. If None is provided, the model will be loaded using the provided values of `input_repr`, `content_type` and `embedding_size`.
            Default value None

        input_repr : "linear", "mel128", or "mel256"
            Spectrogram representation used for model. Ignored if `model` is
            a valid Keras model.
            Default value "mel256"

        content_type : "music" or "env"
            Type of content used to train the embedding model. Ignored if `model` is
            a valid Keras model.
            Default value "music"

        embedding_size : 6144 or 512
            Embedding dimensionality. Ignored if `model` is a valid Keras model.
            Default value 6144

        center : bool
            If True, pads beginning of signal so timestamps correspond to center of window.
            Default value True

        batch_size : int
            Batch size used for input to embedding model
            Default value 32

        verbose : bool
            If True, prints verbose messages.
            Default value False

        """
        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': fs,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': 1.0,
            'hop_length_seconds': hop_length_seconds,
        })

        # Run EmbeddingExtractor init
        EmbeddingExtractor.__init__(self, **kwargs)

        super(OpenL3Extractor, self).__init__(**kwargs)

        self.model = model
        self.input_repr = input_repr
        self.content_type = content_type
        self.embedding_size = embedding_size
        self.center = center
        self.batch_size = batch_size
        self.verbose = verbose

        try:
            # Suppress tensorflow warnings
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import logging
            logging.getLogger('tensorflow').setLevel(logging.FATAL)

            import openl3

        except ImportError:
            message = '{name}: Unable to import OpenL3 module. You can install it with `pip install openl3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        if self.model is None:
            self.model = openl3.models.load_audio_embedding_model(
                input_repr=self.input_repr ,
                content_type=self.content_type,
                embedding_size=self.embedding_size
            )

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

        output = super(OpenL3Extractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='OpenL3Extractor', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='input_repr', value=self.input_repr) + '\n'
        output += ui.data(indent=indent + 2, field='content_type', value=self.content_type) + '\n'
        output += ui.data(indent=indent + 2, field='embedding_size', value=self.embedding_size) + '\n'
        output += ui.data(indent=indent + 2, field='center', value=self.center) + '\n'
        output += ui.data(indent=indent + 2, field='batch_size', value=self.batch_size) + '\n'
        output += ui.data(indent=indent + 2, field='verbose', value=self.verbose) + '\n'

        return output

    def __getstate__(self):
        d = super(OpenL3Extractor, self).__getstate__()
        d.update({
            'input_repr': self.input_repr,
            'content_type': self.content_type,
            'embedding_size': self.embedding_size,
            'center': self.center,
            'batch_size': self.batch_size,
            'verbose': self.verbose
        })

        return d

    def __setstate__(self, d):
        super(OpenL3Extractor, self).__setstate__(d)
        self.input_repr =  d['input_repr']
        self.content_type =  d['content_type']
        self.embedding_size =  d['embedding_size']
        self.center =  d['center']
        self.batch_size =  d['batch_size']
        self.verbose =  d['verbose']

        try:
            import openl3

        except ImportError:
            message = '{name}: Unable to import OpenL3 module. You can install it with `pip install openl3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        self.model = openl3.models.load_audio_embedding_model(
            input_repr=self.input_repr,
            content_type=self.content_type,
            embedding_size=self.embedding_size
        )

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        embedding : np.ndarray [shape=(T, D)] or list[np.ndarray]
            Array of embeddings for each window or list of such arrays for multiple audio clips.

        """
        try:
            import openl3

        except ImportError:
            message = '{name}: Unable to import OpenL3 module. You can install it with `pip install openl3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        embedding, timestamps = openl3.get_audio_embedding(
            audio=y,
            sr=self.fs,
            model=self.model,
            center=self.center,
            hop_size=self.hop_length_seconds,
            batch_size=self.batch_size,
            verbose=self.verbose
        )
        return embedding.T


class EdgeL3Extractor(EmbeddingExtractor):
    """EdgeL3 Embedding extractor class"""
    label = 'edgel3'  #: Extractor label
    description = 'EdgeL3 (embedding)'  #: Extractor description

    def __init__(self, fs=48000, hop_length_samples=None, hop_length_seconds=0.02,
                 model=None, retrain_type='ft', sparsity=95.45,
                 center=True, verbose=False,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        fs : int
            Sampling rate of the incoming signal. If not 48kHz audio will be resampled.
            Default value 48000

        hop_length_samples : int
            Hop length in samples.
            Default value None

        hop_length_seconds : float
            Hop length in seconds.
            Default value 0.02

        model : keras.models.Model or None
            Loaded model object. If a model is provided, then `sparsity` will be ignored. If None is provided, the model will be loaded using the provided `sparsity` value.
            Default value None

        retrain_type : {'ft', 'kd'}
            Type of retraining for the sparsified weights of L3 audio model. 'ft' chooses the fine-tuning method
            and 'kd' returns knowledge distilled model.
            Default value "ft"

        sparsity : {95.45, 53.5, 63.5, 72.3, 73.5, 81.0, 87.0, 90.5}
            The desired sparsity of audio model.
            Default value 95.45

        center : bool
            If True, pads beginning of signal so timestamps correspond to center of window.
            Default value True

        verbose : bool
            If True, prints verbose messages.
            Default value False

        """

        # Inject parameters for the parent classes back to kwargs. For the convenience they are expose explicitly here.
        kwargs.update({
            'fs': fs,
            'win_length_samples': fs,
            'hop_length_samples': hop_length_samples,
            'win_length_seconds': 1.0,
            'hop_length_seconds': hop_length_seconds,
        })

        # Run EmbeddingExtractor init
        EmbeddingExtractor.__init__(self, **kwargs)

        super(EdgeL3Extractor, self).__init__(**kwargs)

        self.model = model
        self.retrain_type = retrain_type
        self.sparsity = sparsity
        self.center = center
        self.verbose = verbose

        try:
            # Suppress tensorflow warnings
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import logging
            logging.getLogger('tensorflow').setLevel(logging.FATAL)

            import edgel3

        except ImportError:
            message = '{name}: Unable to import EdgeL3 module. You can install it with `pip install edgel3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        if self.model is None:
            self.model = edgel3.models.load_embedding_model(
                retrain_type=self.retrain_type ,
                sparsity=self.sparsity
            )

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

        output = super(EdgeL3Extractor, self).to_string(ui=ui, indent=indent)

        output += ui.line(field='EdgeL3Extractor', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='retrain_type', value=self.retrain_type) + '\n'
        output += ui.data(indent=indent + 2, field='sparsity', value=self.sparsity) + '\n'
        output += ui.data(indent=indent + 2, field='center', value=self.center) + '\n'
        output += ui.data(indent=indent + 2, field='verbose', value=self.verbose) + '\n'

        return output

    def __getstate__(self):
        d = super(EdgeL3Extractor, self).__getstate__()
        d.update({
            'retrain_type': self.retrain_type,
            'sparsity': self.sparsity,
            'center': self.center,
            'verbose': self.verbose
        })

        return d

    def __setstate__(self, d):
        super(EdgeL3Extractor, self).__setstate__(d)
        self.retrain_type = d['retrain_type']
        self.sparsity = d['sparsity']
        self.center = d['center']
        self.verbose = d['verbose']

        try:
            import edgel3

        except ImportError:
            message = '{name}: Unable to import EdgeL3 module. You can install it with `pip install edgel3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        self.model = edgel3.models.load_embedding_model(
            retrain_type=self.retrain_type,
            sparsity=self.sparsity
        )

    def extract(self, y):
        """Extract features for the audio signal.

        Parameters
        ----------
        y : numpy.ndarray [shape=(n,)]
            Audio signal

        Returns
        -------
        embedding : np.ndarray [shape=(T, D)] or list[np.ndarray]
            Array of embeddings for each window or list of such arrays for multiple audio clips.

        """

        try:
            import edgel3

        except ImportError:
            message = '{name}: Unable to import EdgeL3 module. You can install it with `pip install edgel3`.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ImportError(message)

        embedding, timestamps = edgel3.get_embedding(
            audio=y,
            sr=self.fs,
            model=self.model,
            center=self.center,
            hop_size=self.hop_length_seconds,
            verbose=self.verbose
        )
        return embedding.T
