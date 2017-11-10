""" Unit tests for Normalizer """

import nose.tools
import numpy

import dcase_util
from dcase_util.data import Normalizer


def test_normalize():

    # Load audio and extract mel features
    param = {
        'feature_extraction': {
            'fs': 44100,
            'win_length_seconds': 0.04,
            'hop_length_seconds': 0.02,
            'spectrogram_type': 'magnitude',
            'window_type': 'hann_symmetric',
            'n_mels': 40,  # Number of MEL bands used
            'n_fft': 2048,  # FFT length
            'fmin': 0,  # Minimum frequency when constructing MEL bands
            'fmax': 22050,  # Maximum frequency when constructing MEL band
            'htk': True,  # Switch for HTK-styled MEL-frequency equation
        },
    }

    chain = dcase_util.processors.ProcessingChain([
        {
            'processor_name': 'dcase_util.processors.MonoAudioReadingProcessor',
            'init_parameters': {
                'fs': param['feature_extraction']['fs']
            }
        },
        {
            'processor_name': 'dcase_util.processors.MelExtractorProcessor',
            'init_parameters': param['feature_extraction']
        }
    ])
    container = chain.process(filename=dcase_util.utils.Example.audio_filename())

    normalizer = Normalizer()
    normalizer.accumulate(container)
    normalizer.finalize()

    numpy.testing.assert_array_equal(
        normalizer.mean,
        numpy.mean(container.data, axis=container.time_axis).reshape(-1, 1)
    )
    numpy.testing.assert_array_equal(
        normalizer.s1,
        numpy.sum(container.data, axis=container.time_axis)
    )
    nose.tools.eq_(normalizer.n, 501)


def test_log():
    with dcase_util.utils.DisableLogger():
        Normalizer(
            filename='Normalizer.cpickle'
        ).log()
