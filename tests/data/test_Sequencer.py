""" Unit tests for Sequencer """

import nose.tools
import tempfile
import os
import numpy
import dcase_util
from dcase_util.data import Sequencer


def test_sequence():
    # Get data in container
    container = dcase_util.containers.FeatureContainer(
        data=numpy.repeat(numpy.arange(0, 100).reshape(1, -1), 3, axis=0),
        time_resolution=1
    )

    # Initialize sequencer, 10 frames long sequences, non-overlapping sequences
    sequencer = Sequencer(
        sequence_length=10,
        hop_length=10
    )
    sequenced_data = sequencer.sequence(
        data=container
    )
    # Check shape
    nose.tools.eq_(sequenced_data.length, 10)
    nose.tools.eq_(sequenced_data.vector_length, 3)
    nose.tools.eq_(sequenced_data.data.shape, (3, 10, 10))

    # Check content
    numpy.testing.assert_equal(sequenced_data.data[0, :, 0], numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 1], numpy.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 2], numpy.array([20, 21, 22, 23, 24, 25, 26, 27, 28, 29]))

    # Initialize sequencer, 10 frames long sequences, 1 frame hop
    sequencer = Sequencer(
        sequence_length=10,
        hop_length=1
    )
    sequenced_data = sequencer.sequence(
        data=container
    )
    # Check shape
    nose.tools.eq_(sequenced_data.length, 10)
    nose.tools.eq_(sequenced_data.vector_length, 3)
    nose.tools.eq_(sequenced_data.data.shape, (3, 10, 91))

    # Check content
    numpy.testing.assert_equal(sequenced_data.data[0, :, 0], numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 1], numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 2], numpy.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))

    # Initialize sequencer, 10 frames long sequences, 1 frame hop
    sequencer = Sequencer(
        sequence_length=10,
        hop_length=1
    )
    # Shift with one frame (+1 from original)
    sequencer.increase_shifting(1)
    sequenced_data = sequencer.sequence(
        data=container
    )
    numpy.testing.assert_equal(sequenced_data.data[0, :, 0], numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 1], numpy.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 2], numpy.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))

    # Shift with one frame (+2 from original)
    sequencer.increase_shifting(1)
    sequenced_data = sequencer.sequence(
        data=container
    )
    numpy.testing.assert_equal(sequenced_data.data[0, :, 0], numpy.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 1], numpy.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 2], numpy.array([4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))

    # Initialize sequencer, 10 frames long sequences, 1 frame hop, shifting border handling mode 'shift'
    sequencer = Sequencer(
        sequence_length=10,
        hop_length=1,
        shift_border='shift'
    )
    sequencer.increase_shifting(1)
    sequenced_data = sequencer.sequence(
        data=container
    )
    numpy.testing.assert_equal(sequenced_data.data[0, :, 0], numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 1], numpy.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
    numpy.testing.assert_equal(sequenced_data.data[0, :, 2], numpy.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))

    # Get feature data
    container = dcase_util.utils.Example.feature_container()

    sequencer = Sequencer(
        sequence_length=10,
        hop_length=10,
    )
    sequenced_data = sequencer.sequence(data=container)
    nose.tools.eq_(sequenced_data.length, 10)
    nose.tools.eq_(sequenced_data.vector_length, 40)
    nose.tools.eq_(sequenced_data.data.shape, (40, 10, 50))

    sequencer = Sequencer(
        sequence_length=10,
        hop_length=1,
    )
    sequenced_data = sequencer.sequence(data=container)

    nose.tools.eq_(sequenced_data.length, 10)
    nose.tools.eq_(sequenced_data.vector_length, 40)
    nose.tools.eq_(sequenced_data.data.shape, (40, 10, 492))


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

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir=tempfile.gettempdir(), delete=False)
    try:

        sequencer = Sequencer(
            sequence_length=10,
            hop_length=10,
        ).save(filename=tmp.name).load()

        sequenced_data = sequencer.sequence(data=container)
        nose.tools.eq_(sequenced_data.length, 10)
        nose.tools.eq_(sequenced_data.vector_length, 40)
        nose.tools.eq_(sequenced_data.data.shape, (40, 10, 50))

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_log():
    with dcase_util.utils.DisableLogger():
        Sequencer(
            sequence_length=10,
            hop_length=10,
            filename='Sequencer.cpickle'
        ).log()
