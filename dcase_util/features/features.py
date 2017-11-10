#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import numpy
import librosa
import scipy
from dcase_util.containers import ContainerMixin
from dcase_util.ui import FancyStringifier


class FeatureExtractor(ContainerMixin):
    """Feature extractor base class"""
    def __init__(self, fs=44100, win_length_samples=None, hop_length_samples=None, win_length_seconds=0.04,
                 hop_length_seconds=0.02, **kwargs):
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

    def __str__(self):
        ui = FancyStringifier()
        output = ''
        output += FancyStringifier().class_name(self.__class__.__name__) + '\n'

        if hasattr(self, 'filename') and self.filename:
            output += FancyStringifier().data(field='filename', value=self.filename) + '\n'

        output += ui.data(field='fs', value=self.fs) + '\n'
        output += ui.line(field='Frame blocking') + '\n'
        output += ui.data(indent=4, field='hop_length_samples', value=self.hop_length_samples) + '\n'
        output += ui.data(indent=4, field='hop_length_seconds', value=self.hop_length_seconds, unit='sec') + '\n'

        output += ui.data(indent=4, field='win_length_samples', value=self.win_length_samples) + '\n'
        output += ui.data(indent=4, field='win_length_seconds', value=self.win_length_seconds, unit='sec') + '\n'

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

        n_fft : int
            Length of the FFT window.

        window_type : str
            Window function type.

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(SpectralFeatureExtractor, self).__str__()

        output += ui.line(field='Spectrogram') + '\n'
        output += ui.data(indent=4, field='spectrogram_type', value=self.spectrogram_type) + '\n'
        output += ui.data(indent=4, field='n_fft', value=self.n_fft) + '\n'
        output += ui.data(indent=4, field='window_type', value=self.window_type) + '\n'

        return output

    def get_window_function(self, n, window_type='hamming_asymmetric'):
        """Window function

        Parameters
        ----------
        n : int
            window length

        window_type : str
            window type

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

    def get_spectrogram(self, y, n_fft=2048, win_length_samples=None, hop_length_samples=None,
                        window=None, center=True, spectrogram_type=None):
        """Spectrogram

        Parameters
        ----------
        y : numpy.ndarray
            Audio data

        n_fft : int
            FFT size

        win_length_samples : float
            Window length in seconds

        hop_length_samples : float
            Hop length in seconds

        window : numpy.array
            Window function

        center : bool
            If true, input signal is padded so to the frame is centered at hop length

        spectrogram_type : str
            Type of spectrogram "magnitude" or "power"

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


class MelExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract mel band energy features"""
    label = 'mel'  #: Extractor label

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(MelExtractor, self).__str__()

        output += ui.line(field='Mel') + '\n'
        output += ui.data(indent=4, field='n_mels', value=self.n_mels) + '\n'
        output += ui.data(indent=4, field='fmin', value=self.fmin) + '\n'
        output += ui.data(indent=4, field='fmax', value=self.fmax) + '\n'
        output += ui.data(indent=4, field='normalize_mel_bands', value=self.normalize_mel_bands) + '\n'
        output += ui.data(indent=4, field='htk', value=self.htk) + '\n'
        output += ui.data(indent=4, field='logarithmic', value=self.logarithmic) + '\n'

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

        omit_zeroth : bool
            Omit 0th coefficient

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(MfccStaticExtractor, self).__str__()

        output += ui.line(field='MFCC') + '\n'
        output += ui.data(indent=4, field='n_mels', value=self.n_mels) + '\n'
        output += ui.data(indent=4, field='fmin', value=self.fmin) + '\n'
        output += ui.data(indent=4, field='fmax', value=self.fmax) + '\n'
        output += ui.data(indent=4, field='normalize_mel_bands', value=self.normalize_mel_bands) + '\n'
        output += ui.data(indent=4, field='htk', value=self.htk) + '\n'
        output += ui.data(indent=4, field='n_mfcc', value=self.n_mfcc) + '\n'

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

        omit_zeroth : bool
            Omit 0th coefficient

        width : int
            Width of the delta window.

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(MfccDeltaExtractor, self).__str__()

        output += ui.line(field='Delta') + '\n'
        output += ui.data(indent=4, field='width', value=self.width) + '\n'

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

        omit_zeroth : bool
            Omit 0th coefficient

        width : int
            Width of the delta window.

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(MfccAccelerationExtractor, self).__str__()

        output += ui.line(field='Acceleration') + '\n'
        output += ui.data(indent=4, field='width', value=self.width) + '\n'

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(ZeroCrossingRateExtractor, self).__str__()

        output += ui.line(field='ZCR') + '\n'
        output += ui.data(indent=4, field='center', value=self.center) + '\n'

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(RMSEnergyExtractor, self).__str__()

        output += ui.line(field='RMSEnergy') + '\n'
        output += ui.data(indent=4, field='center', value=self.center) + '\n'

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

        return librosa.feature.rmse(
            S=spectrogram
        ).reshape((1, -1))


class SpectralCentroidExtractor(SpectralFeatureExtractor):
    """Feature extractor class to extract Centroid features"""
    label = 'centroid'  #: Extractor label

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

    def __str__(self):
        ui = FancyStringifier()
        output = super(SpectralCentroidExtractor, self).__str__()

        output += ui.line(field='SpectralCentroid') + '\n'
        output += ui.data(indent=4, field='center', value=self.center) + '\n'

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

