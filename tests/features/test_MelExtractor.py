""" Unit tests for MelExtractor """

import nose.tools
import dcase_util


def test_extract():

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
    mel_extractor = dcase_util.features.MelExtractor(**params)

    audio_container = dcase_util.utils.Example.audio_container()
    audio_container.mixdown()

    mels = mel_extractor.extract(y=audio_container)

    nose.tools.eq_(mels.shape[0], params['n_mels'])
    nose.tools.eq_(mels.shape[1], 101)

