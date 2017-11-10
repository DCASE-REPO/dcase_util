import nose.tools
import dcase_util


def test_ProcessingChain():

    chain = dcase_util.processors.ProcessingChain()
    chain.push_processor(
        processor_name='dcase_util.processors.MonoAudioReadingProcessor',
        init_parameters={'fs': 44100}
    )
    chain.push_processor(
        processor_name='dcase_util.processors.MelExtractorProcessor',
        init_parameters={}
    )
    nose.tools.eq_(len(chain), 2)

    nose.tools.eq_(chain.processor_exists('dcase_util.processors.MonoAudioReadingProcessor'), True)
    nose.tools.eq_(chain.processor_exists('dcase_util.processors.MelExtractorProcessor'), True)
    nose.tools.eq_(chain.processor_exists('dcase_util.processors.AudioReadingProcessor'), False)

    data = chain.process(
        filename=dcase_util.utils.Example().audio_filename(),
        focus_start_seconds=1.0,
        duration_seconds=2.0
    )
    nose.tools.eq_(data.shape, (40, 501))
