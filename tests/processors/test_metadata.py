import nose.tools
import dcase_util
import tempfile
import os


def test_MetadataReadingProcessor():
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        dcase_util.utils.Example.event_metadata_container().save(tmp.name)

        m = dcase_util.processors.MetadataReadingProcessor()
        processed = m.process(
            filename=tmp.name,
            focus_filename='test1.wav'
        )
        nose.tools.eq_(processed.event_count, 3)
        nose.tools.eq_(processed.file_count, 1)

        m = dcase_util.processors.MetadataReadingProcessor()
        processed = m.process(
            filename=tmp.name,
            focus_filename='test1.wav',
            focus_start_seconds=0.0,
            focus_stop_seconds=3.0
        )
        nose.tools.eq_(processed.event_count, 1)
        nose.tools.eq_(processed.file_count, 1)

        m = dcase_util.processors.MetadataReadingProcessor()
        processed = m.process(
            filename=tmp.name,
            focus_filename='test1.wav',
            focus_start_seconds=0,
            focus_duration_seconds=3.0
        )
        nose.tools.eq_(processed.event_count, 1)
        nose.tools.eq_(processed.file_count, 1)

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass
