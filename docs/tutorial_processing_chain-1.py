import dcase_util
chain = dcase_util.processors.ProcessingChain([
    {
        'processor_name': 'MonoAudioReadingProcessor',
        'init_parameters': {
            'fs': 44100
        }
    },
    {
        'processor_name': 'MelExtractorProcessor'
    }
])
data = chain.process(filename=dcase_util.utils.Example().audio_filename())
data.plot()