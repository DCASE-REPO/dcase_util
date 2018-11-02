import nose.tools
import dcase_util
import tempfile
import os


def test_RepositoryFeatureExtractorProcessor():
    extractor = dcase_util.processors.RepositoryFeatureExtractorProcessor(
        parameters={
            'mel': {},
            'mfcc': {}
        }
    )
    processed = extractor.process(data=dcase_util.utils.Example.audio_container())
    nose.tools.eq_(processed['mel'][0].data.shape, (40, 101))
    nose.tools.eq_(processed['mfcc'][0].data.shape, (20, 101))

    # With processing chain
    processed = extractor.process(
        data=dcase_util.utils.Example.audio_container(),
        store_processing_chain=True
    )
    nose.tools.eq_(processed['mel'][0].data.shape, (40, 101))
    nose.tools.eq_(processed['mfcc'][0].data.shape, (20, 101))
    nose.tools.eq_(len(processed.processing_chain), 1)

    # Copied
    import copy
    processed_copy = copy.deepcopy(processed)
    nose.tools.eq_(processed_copy['mel'][0].data.shape, (40, 101))
    nose.tools.eq_(processed_copy['mfcc'][0].data.shape, (20, 101))
    nose.tools.eq_(len(processed_copy.processing_chain), 1)


def test_MelExtractorProcessor():
    extractor = dcase_util.processors.MelExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (40, 101))


def test_MfccStaticExtractorProcessor():
    extractor = dcase_util.processors.MfccStaticExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (20, 101))


def test_MfccDeltaExtractorProcessor():
    extractor = dcase_util.processors.MfccDeltaExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (20, 101))


def test_MfccAccelerationExtractorProcessor():
    extractor = dcase_util.processors.MfccAccelerationExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (20, 101))


def test_ZeroCrossingRateExtractorProcessor():
    extractor = dcase_util.processors.ZeroCrossingRateExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (1, 101))


def test_RMSEnergyExtractorProcessor():
    extractor = dcase_util.processors.RMSEnergyExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (1, 101))


def test_SpectralCentroidExtractorProcessor():
    extractor = dcase_util.processors.SpectralCentroidExtractorProcessor()
    processed = extractor.process(data=dcase_util.utils.Example.audio_container().mixdown())
    nose.tools.eq_(processed.shape, (1, 101))


def test_writing_reading():
    chain = dcase_util.processors.ProcessingChain([
        {
            'processor_name': 'MonoAudioReadingProcessor',
            'init_parameters': {
                'fs': 44100
            }
        },
        {
            'processor_name': 'MelExtractorProcessor'
        },
        {
            'processor_name': 'FeatureWritingProcessor'
        }
    ])

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir=tempfile.gettempdir(), delete=False)
    try:
        # Run the processing chain
        data = chain.process(
            filename=dcase_util.utils.Example().audio_filename(),
            output_filename=tmp.name
        )

        data_loaded = dcase_util.containers.FeatureContainer().load(filename=tmp.name)

        nose.tools.eq_(data.shape, data_loaded.shape)

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

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
            'processor_name': 'RepositoryFeatureWritingProcessor'
        }
    ])

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir=tempfile.gettempdir(), delete=False)
    try:
        # Run the processing chain
        repo = chain.process(
            filename=dcase_util.utils.Example().audio_filename(),
            output_filename=tmp.name
        )

        repo_loaded = dcase_util.containers.FeatureRepository().load(filename=tmp.name)

        nose.tools.eq_(repo.labels, repo_loaded.labels)

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

