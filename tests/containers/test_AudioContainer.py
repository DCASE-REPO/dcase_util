""" Unit tests for AudioContainer """

import nose.tools
import dcase_util
import os
import numpy
import tempfile


def test_load():
    # Mono
    audio = dcase_util.containers.AudioContainer(
        filename=dcase_util.utils.Example.audio_filename()
    ).load(
        mono=True
    )

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.data.shape[0], 441001)

    # Stereo
    audio = dcase_util.containers.AudioContainer(
        filename=dcase_util.utils.Example.audio_filename()
    ).load(
        mono=False
    )

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(audio.data.shape[0], 2)
    nose.tools.eq_(audio.data.shape[1], 441001)

    # Re-sampling
    audio = dcase_util.containers.AudioContainer(
        filename=dcase_util.utils.Example.audio_filename()
    ).load(
        fs=16000,
        mono=True
    )

    nose.tools.eq_(audio.fs, 16000)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.data.shape[0], 160001)

    # Segment
    audio = dcase_util.containers.AudioContainer(
        filename=dcase_util.utils.Example.audio_filename()
    ).load(
        mono=True,
        start=4.0,
        stop=6.0
    )

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.data.shape[0], 88200)


def test_load_youtube():
    with dcase_util.utils.DisableLogger():
        audio_container = dcase_util.containers.AudioContainer().load_from_youtube(
          query_id='2ceUOv8A3FE',
          start=1,
          stop=5
        )

    nose.tools.eq_(audio_container.fs, 44100)
    nose.tools.eq_(len(audio_container.data.shape), 2)
    nose.tools.eq_(audio_container.streams, 2)
    nose.tools.eq_(audio_container.shape, (2, 176400))


def test_container():
    # Empty
    a = dcase_util.utils.Example.audio_container()
    if a:
        pass
    nose.tools.eq_(a.empty, False)
    nose.tools.eq_(dcase_util.containers.AudioContainer().empty, True)

    # Basic info
    a = dcase_util.utils.Example.audio_container()
    nose.tools.eq_(a.fs, 44100)
    nose.tools.eq_(len(a.data.shape), 2)
    nose.tools.eq_(a.data.shape, a.shape)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*44100)
    nose.tools.eq_(a.channels, 2)

    # Focus #1.1
    a = dcase_util.utils.Example.audio_container()
    a.set_focus(start_seconds=0.5, stop_seconds=0.8)
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 13230))

    # Focus #1.2
    a = dcase_util.utils.Example.audio_container()
    a.set_focus(start_seconds=0.5, duration_seconds=0.3)
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 13230))

    # Focus #1.3
    a = dcase_util.utils.Example.audio_container()
    a.set_focus(start=0, duration=44100)
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 44100))

    # Focus #1.4
    a = dcase_util.utils.Example.audio_container()
    a.set_focus(start=0, stop=44100)
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 44100))

    # Focus #1.5
    a = dcase_util.utils.Example.audio_container()
    a.set_focus()
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 2*44100))

    # Focus #2.1
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = int(0.2 * 44100)
    a.focus_stop_samples = int(0.5 * 44100)
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 0.3 * 44100))

    # Focus #2.2
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = 0.2 * 44100
    a.focus_stop_samples = 0.5 * 44100
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 0.3 * 44100))

    # Focus #2.3
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = 0.5 * 44100
    a.focus_stop_samples = 0.2 * 44100
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 0.3 * 44100))

    # Focus #2.4
    a = dcase_util.utils.Example.audio_container()
    a.focus_stop_samples = 0.2 * 44100
    a.focus_start_samples = 0.5 * 44100
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 0.3 * 44100))

    # Focus #2.5
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = 0.5 * 44100
    a.focus_stop_samples = None
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 1.5 * 44100))

    # Focus #2.6
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = None
    a.focus_stop_samples = 0.5 * 44100
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 0.5 * 44100))

    # Focus #2.7
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_samples = 0
    a.focus_stop_samples = 30 * 44100
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, a.length))

    # Focus #3.1
    a = dcase_util.utils.Example.audio_container()
    a.focus_start_seconds = 1.0
    a.focus_stop_seconds = 2.0
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, 1 * 44100))

    # Focus #4.1
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 0
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 1)
    nose.tools.eq_(a_focused.shape, (a.length, ))
    numpy.testing.assert_array_almost_equal(a_focused, a.data[0, :])

    # Focus #4.2
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 1
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 1)
    nose.tools.eq_(a_focused.shape, (a.length, ))
    numpy.testing.assert_array_almost_equal(a_focused, a.data[1, :])

    # Focus #4.3
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 'left'
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 1)
    nose.tools.eq_(a_focused.shape, (a.length, ))
    numpy.testing.assert_array_almost_equal(a_focused, a.data[0, :])

    # Focus #4.4
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 'right'
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 1)
    nose.tools.eq_(a_focused.shape, (a.length, ))
    numpy.testing.assert_array_almost_equal(a_focused, a.data[1, :])

    # Focus #4.5
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 123
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 2)
    nose.tools.eq_(a_focused.shape, (2, a.length))

    # Focus #4.6
    a = dcase_util.utils.Example.audio_container()
    a.focus_channel = 0
    a_focused = a.get_focused()
    nose.tools.eq_(len(a_focused.shape), 1)
    nose.tools.eq_(a_focused.shape, (a.length, ))

    # Channel average
    a = dcase_util.utils.Example.audio_container()
    a.mixdown()
    nose.tools.eq_(a.channels, 1)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*44100)

    # Normalization
    a = dcase_util.utils.Example.audio_container()
    a.normalize(headroom=0.5)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*44100)
    nose.tools.assert_almost_equal(numpy.max(numpy.abs(a.data)), 0.66666661027952101, places=6)

    # Normalization / Mono
    a = dcase_util.utils.Example.audio_container().mixdown()
    a.normalize(headroom=0.5)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*44100)
    nose.tools.assert_almost_equal(numpy.max(numpy.abs(a.data)), 0.63770331161958482, places=6)

    # Re-sampling
    a = dcase_util.utils.Example.audio_container()
    a.resample(target_fs=16000)
    nose.tools.eq_(a.fs, 16000)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*16000)

    # Select channel

    # make_monophonic
    a = dcase_util.utils.Example.audio_container()
    x1 = a.data[0, :]
    x2 = a.data[1, :]

    a.mixdown()
    nose.tools.eq_(a.fs, 44100)
    nose.tools.eq_(len(a.data.shape), 1)
    nose.tools.eq_(a.data.shape, a.shape)
    nose.tools.eq_(a.duration_ms, 2000)
    nose.tools.eq_(a.duration_sec, 2)
    nose.tools.eq_(a.duration_samples, 2*44100)
    nose.tools.eq_(a.channels, 1)


def test_save():
    a_out = dcase_util.utils.Example.audio_container()

    # 16 bit / wav
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.wav', prefix='16_', dir=tempfile.gettempdir(), delete=False)
    try:
        a_out.save(filename=tmp.name, bit_depth=16)
        a_in = dcase_util.containers.AudioContainer().load(filename=tmp.name)
        nose.tools.eq_(a_out.shape, a_in.shape)
        numpy.testing.assert_array_almost_equal(a_out.data, a_in.data, decimal=4)
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # 24 bit / wav
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.wav', prefix='24_', dir=tempfile.gettempdir(), delete=False)
    try:
        a_out.save(filename=tmp.name, bit_depth=24)
        a_in = dcase_util.containers.AudioContainer().load(filename=tmp.name)
        nose.tools.eq_(a_out.shape, a_in.shape)
        numpy.testing.assert_array_almost_equal(a_out.data, a_in.data, decimal=5)
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # 32 bit / wav
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.wav', prefix='32_', dir=tempfile.gettempdir(), delete=False)
    try:
        a_out.save(filename=tmp.name, bit_depth=32)
        a_in = dcase_util.containers.AudioContainer().load(filename=tmp.name)
        nose.tools.eq_(a_out.shape, a_in.shape)
        numpy.testing.assert_array_almost_equal(a_out.data, a_in.data, decimal=6)
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_log():
    with dcase_util.utils.DisableLogger():
        a = dcase_util.utils.Example.audio_container()
        a.log()

        a.filename = 'test.wav'
        a.log()

        a.focus_start_samples = 0.1
        a.focus_stop_samples = 0.5
        a.log()

        a.focus_channel = 'left'
        a.log()


def test_pad():
    a = dcase_util.utils.Example.audio_container().mixdown()
    a.pad(length_seconds=10)
    nose.tools.eq_(a.duration_sec, 10)

    a = dcase_util.utils.Example.audio_container()
    a.pad(length_seconds=10)
    nose.tools.eq_(a.duration_sec, 10)

    a = dcase_util.utils.Example.audio_container_ch4()
    a.pad(length_seconds=10)
    nose.tools.eq_(a.duration_sec, 10)


def test_segments():
    a = dcase_util.utils.Example.audio_container().mixdown()
    segments, segment_meta = a.segments(segment_length=1000)
    nose.tools.eq_(len(segments), 88)
    nose.tools.eq_(len(segments), len(segment_meta))

    segments, segment_meta = a.segments(segment_length_seconds=0.5)
    nose.tools.eq_(len(segments), 3)
    nose.tools.eq_(len(segments), len(segment_meta))

    segments, segment_meta = a.segments(
        segments=[
            {'onset': 0.5, 'offset': 0.8}
        ]
    )
    nose.tools.eq_(len(segments), 1)
    nose.tools.eq_(len(segments), len(segment_meta))
    nose.tools.eq_(segment_meta[0]['onset'], 0.5)
    nose.tools.eq_(segment_meta[0]['offset'], 0.8)

    segments, segment_meta = a.segments(
        segment_length_seconds=0.5,
        skip_segments=[
            {
                'onset': 0.6,
                'offset': 0.8
            }
        ]
    )
    nose.tools.eq_(len(segments), 3)
    nose.tools.eq_(len(segments), len(segment_meta))
    nose.tools.eq_(segment_meta, [
        {
            'onset': 0.0,
            'offset': 0.5
        },
        {
            'onset': 0.8,
            'offset': 1.3
        },
        {
            'onset': 1.3,
            'offset': 1.8
        }
    ])

    a = dcase_util.utils.Example.audio_container()
    segments, segment_meta = a.segments(segment_length=1000)
    nose.tools.eq_(len(segments), 88)
    nose.tools.eq_(len(segments), len(segment_meta))


def test_frames():
    a = dcase_util.utils.Example.audio_container().mixdown()
    frames = a.frames(frame_length=1000, hop_length=1000)
    nose.tools.eq_(frames.shape[0], 1000)
    nose.tools.eq_(frames.shape[1], 88)

    a = dcase_util.utils.Example.audio_container()
    frames = a.frames(frame_length=1000, hop_length=1000)
    nose.tools.eq_(frames.shape[0], 2)
    nose.tools.eq_(frames.shape[1], 1000)
    nose.tools.eq_(frames.shape[2], 88)


@nose.tools.raises(ValueError)
def test_focus_channel():
    with dcase_util.utils.DisableLogger():
        a = dcase_util.utils.Example.audio_container()
        a.focus_channel = 'wrong'


@nose.tools.raises(IOError)
def test_load_error():
    with dcase_util.utils.DisableLogger():
        dcase_util.containers.AudioContainer(
            filename='Test.test'
        ).load()
