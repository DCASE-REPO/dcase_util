import nose.tools
import dcase_util


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
