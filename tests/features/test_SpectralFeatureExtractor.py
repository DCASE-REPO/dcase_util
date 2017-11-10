""" Unit tests for SpectralFeatureExtractor """

import nose.tools
from nose.tools import *
import dcase_util


def test_get_spectrogram():
    params = {
            'fs': 44100,
            'win_length_seconds': 0.04,
            'hop_length_seconds': 0.02,
            'n_fft': 2048,  # FFT length
            'spectrogram_type': 'magnitude',
            'window_type': 'hann_symmetric',
    }
    sfe = dcase_util.features.SpectralFeatureExtractor(**params)
    audio_container = dcase_util.utils.Example.audio_container()
    audio_container.mixdown()
    spec = sfe.get_spectrogram(
        y=audio_container,
    )

    nose.tools.eq_(spec.shape[0], (params['n_fft'] / 2) + 1)
    nose.tools.eq_(spec.shape[1], 101)

    spec = sfe.get_spectrogram(
        y=audio_container,
        spectrogram_type='power'
    )

    nose.tools.eq_(spec.shape[0], (params['n_fft'] / 2) + 1)
    nose.tools.eq_(spec.shape[1], 101)


@raises(ValueError)
def test_non_mono():
    with dcase_util.utils.DisableLogger():
        params = {
            'fs': 44100,
            'win_length_seconds': 0.04,
            'hop_length_seconds': 0.02,
            'spectrogram_type': 'magnitude',
            'window_type': 'hann_symmetric',
            'n_mels': 40,                       # Number of MEL bands used
            'n_fft': 2048,                      # FFT length
            'fmin': 0,                          # Minimum frequency when constructing MEL bands
            'fmax': 22050,                      # Maximum frequency when constructing MEL band
            'htk': True,                        # Switch for HTK-styled MEL-frequency equation
        }
        sfe = dcase_util.features.SpectralFeatureExtractor(**params)
        audio_container = dcase_util.utils.Example.audio_container()
        sfe.get_spectrogram(y=audio_container)
