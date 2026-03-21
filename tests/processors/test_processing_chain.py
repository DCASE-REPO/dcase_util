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
    assert len(chain) == 2

    assert chain.processor_exists('dcase_util.processors.MonoAudioReadingProcessor') == True
    assert chain.processor_exists('dcase_util.processors.MelExtractorProcessor') == True
    assert chain.processor_exists('dcase_util.processors.AudioReadingProcessor') == False

    data = chain.process(
        filename=dcase_util.utils.Example().audio_filename(),
        focus_start_seconds=1.0,
        duration_seconds=2.0
    )
    assert data.shape == (40, 501)
