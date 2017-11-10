""" Unit tests for Sequencer """

import nose.tools
import tempfile
import os
import dcase_util
from dcase_util.data import Sequencer


def test_sequence():

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

    sequencer = Sequencer(
        frames=10,
        hop_length_frames=10,
    )
    sequenced_data = sequencer.sequence(data=container)
    nose.tools.eq_(sequenced_data.length, 10)
    nose.tools.eq_(sequenced_data.vector_length, 40)
    nose.tools.eq_(sequenced_data.data.shape, (40, 10, 50))


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
            'processor_name': 'dcase_util.processors.MelExtractorProcessor',
            'init_parameters': param['feature_extraction']
        }
    ])
    container = chain.process(filename=dcase_util.utils.Example.audio_filename())

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir='/tmp', delete=False)
    try:

        sequencer = Sequencer(
            frames=10,
            hop_length_frames=10,
        ).save(filename=tmp.name).load()

        sequenced_data = sequencer.sequence(data=container)
        nose.tools.eq_(sequenced_data.length, 10)
        nose.tools.eq_(sequenced_data.vector_length, 40)
        nose.tools.eq_(sequenced_data.data.shape, (40, 10, 50))

    finally:
        os.unlink(tmp.name)


def test_log():
    with dcase_util.utils.DisableLogger():
        Sequencer(
            frames=10,
            hop_length_frames=10,
            filename='Sequencer.cpickle'
        ).log()
