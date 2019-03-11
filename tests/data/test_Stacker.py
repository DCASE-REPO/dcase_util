""" Unit tests for Stacker """

import nose.tools
import tempfile
import os

import dcase_util
from dcase_util.data import Stacker


def test_stack():
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
            'processor_name': 'dcase_util.processors.RepositoryFeatureExtractorProcessor',
            'init_parameters': {
                'parameters': {
                    'mel': param['feature_extraction'],
                    'mfcc': param['feature_extraction']
                }
            }
        }
    ])
    repository = chain.process(filename=dcase_util.utils.Example.audio_filename())

    stacked_data = Stacker(recipe='mel').stack(repository=repository)

    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, param['feature_extraction']['n_mels'])

    stacked_data = Stacker(recipe='mel=0-5').stack(repository=repository)

    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, 6)

    stacked_data = Stacker(recipe='mel=1-5').stack(repository=repository)

    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, 5)

    stacked_data = Stacker(recipe='mel=1,2,3,4').stack(repository=repository)

    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, 4)

    stacked_data = Stacker(recipe='mel;mfcc=1-10').stack(repository=repository)
    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, 50)

    stacked_data = Stacker(recipe='mel=0;mfcc=0:1-10').stack(repository=repository)
    nose.tools.eq_(stacked_data.length, 501)
    nose.tools.eq_(stacked_data.vector_length, 50)


def test_save():
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
            'processor_name': 'dcase_util.processors.RepositoryFeatureExtractorProcessor',
            'init_parameters': {
                'parameters': {
                    'mel': param['feature_extraction'],
                    'mfcc': param['feature_extraction']
                }
            }
        }
    ])
    repository = chain.process(filename=dcase_util.utils.Example.audio_filename())

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir=tempfile.gettempdir(), delete=False)
    try:
        stacked_data = Stacker(recipe='mel').stack(repository=repository).save(filename=tmp.name).load()

        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, param['feature_extraction']['n_mels'])

        stacked_data = Stacker(recipe='mel=0-5').stack(repository=repository)

        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, 6)

        stacked_data = Stacker(recipe='mel=1-5').stack(repository=repository)

        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, 5)

        stacked_data = Stacker(recipe='mel=1,2,3,4').stack(repository=repository)

        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, 4)

        stacked_data = Stacker(recipe='mel;mfcc=1-10').stack(repository=repository)
        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, 50)

        stacked_data = Stacker(recipe='mel=0;mfcc=0:1-10').stack(repository=repository)
        nose.tools.eq_(stacked_data.length, 501)
        nose.tools.eq_(stacked_data.vector_length, 50)

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_log():
    with dcase_util.utils.DisableLogger():
        Stacker(recipe='mel', filename='Stacker.cpickle').log()
