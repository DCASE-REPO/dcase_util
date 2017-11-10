import nose.tools
import dcase_util


def test_AudioReadingProcessor():

    # Simple reading
    processor = dcase_util.processors.AudioReadingProcessor()
    audio = processor.process(filename=dcase_util.utils.Example.audio_filename())

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 2)
    nose.tools.eq_(audio.length, 441001)

    # Mono reading
    processor = dcase_util.processors.AudioReadingProcessor(mono=True)
    audio = processor.process(filename=dcase_util.utils.Example.audio_filename())

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.length, 441001)

    # Focus segment
    processor = dcase_util.processors.AudioReadingProcessor(mono=True)
    audio = processor.process(
        filename=dcase_util.utils.Example.audio_filename(),
        focus_start_seconds=1.0,
        focus_duration_seconds=2.0
    ).freeze()

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.length, 44100*2.0)

    # Focus channel
    processor = dcase_util.processors.AudioReadingProcessor()
    audio = processor.process(
        filename=dcase_util.utils.Example.audio_filename(),
        focus_channel='mixdown',
        focus_start_seconds=1.0,
        focus_duration_seconds=2.0
    ).freeze()

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.length, 44100*2.0)


def test_MonoAudioReadingProcessor():
    # Simple reading
    processor = dcase_util.processors.MonoAudioReadingProcessor()
    audio = processor.process(filename=dcase_util.utils.Example.audio_filename())

    nose.tools.eq_(audio.fs, 44100)
    nose.tools.eq_(len(audio.data.shape), 1)
    nose.tools.eq_(audio.length, 441001)
