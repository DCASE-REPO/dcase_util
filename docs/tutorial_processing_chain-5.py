import dcase_util
chain = dcase_util.processors.ProcessingChain([
    {
        'processor_name': 'AudioReadingProcessor',
        'init_parameters': {
            'fs': 44100
        }
    },
    {
        'processor_name': 'RepositoryFeatureExtractorProcessor',
        'init_parameters': {
            'parameters': {
                'mel': {}
            }
        }
    },
    {
        'processor_name': 'RepositorySequencingProcessor',
        'init_parameters': {
            'frames': 100,
            'hop_length_frames': 100
        }
    },
    {
        'processor_name': 'RepositoryToMatrixProcessor',
        'init_parameters': {
            'label': 'mel',
            'expanded_dimension': 'last'
        }
    },
])
# Run the processing chain
data = chain.process(filename=dcase_util.utils.Example().audio_filename())
data.plot()