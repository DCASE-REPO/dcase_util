import nose.tools
import dcase_util
import numpy


def test_AggregationProcessor():

    a = dcase_util.processors.AggregationProcessor(
        recipe=['flatten']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (400, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['mean']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (40, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['mean']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (40, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['cov']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (1600, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['kurtosis']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (40, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['skew']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (40, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['flatten', 'mean']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (440, 501))

    a = dcase_util.processors.AggregationProcessor(
        recipe=['mean', 'std']
    )
    processed = a.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (80, 501))


def test_SequencingProcessor():

    s = dcase_util.processors.SequencingProcessor()
    processed = s.process(dcase_util.utils.Example.feature_container())
    nose.tools.eq_(processed.data.shape, (40, 10, 50))


def test_NormalizationProcessor():
    data = dcase_util.utils.Example.feature_container()

    normalizer = dcase_util.processors.NormalizationProcessor(
        mean=data.stats['mean'], std=data.stats['std']
    )
    processed = normalizer.process(dcase_util.utils.Example.feature_container())
    nose.tools.assert_almost_equal(numpy.sum(numpy.std(processed.data, axis=1)), 40.0)


def test_RepositoryNormalizationProcessor():
    repo = dcase_util.utils.Example.feature_repository()
    normalizer = dcase_util.processors.RepositoryNormalizationProcessor(
        parameters={
            'mel': repo['mel'][0].stats,
            'mfcc': repo['mfcc'][0].stats
        }
    )
    processed = normalizer.process(repo)

    nose.tools.assert_almost_equal(numpy.sum(numpy.std(processed['mel'][0].data, axis=1)), 40.0, delta=0.0001)
    nose.tools.assert_almost_equal(numpy.sum(numpy.std(processed['mfcc'][0].data, axis=1)), 20.0, delta=0.0001)


def test_StackingProcessor():
    repo = dcase_util.utils.Example.feature_repository()
    stacker = dcase_util.processors.StackingProcessor(recipe='mel;mfcc')
    processed = stacker.process(repo)

    nose.tools.eq_(processed.data.shape, (60, 501))


def test_RepositoryMaskingProcessor():
    repo = dcase_util.utils.Example.feature_repository()
    mask = dcase_util.utils.Example.event_metadata_container()
    mask_events = dcase_util.containers.MetaDataContainer([mask[1]])
    masker = dcase_util.processors.RepositoryMaskingProcessor()
    processed = masker.process(
        data=repo,
        mask_events=mask_events
    )

    nose.tools.eq_(processed['mel'][0].shape, (40, 318))
    nose.tools.eq_(processed['mfcc'][0].shape, (20, 318))
    nose.tools.eq_(processed['zcr'][0].shape, (1, 318))


def test_OneHotEncodingProcessor():
    encoder = dcase_util.processors.OneHotEncodingProcessor(
        label_list=dcase_util.utils.Example.scene_metadata_container().unique_scene_labels,
        time_resolution=1.0
    )
    scene = dcase_util.utils.Example.scene_metadata_container().filter(filename='test1.wav')
    processed = encoder.process(scene, length_seconds=10.0)

    nose.tools.eq_(processed.shape, (5, 10))


def test_ManyHotEncodingProcessor():
    encoder = dcase_util.processors.ManyHotEncodingProcessor(
        label_list=dcase_util.utils.Example.scene_metadata_container().unique_scene_labels,
        time_resolution=1.0,
        focus_field='scene_label'
    )
    scene = dcase_util.utils.Example.scene_metadata_container().filter(filename='test1.wav')

    processed = encoder.process(scene, length_seconds=10.0)

    nose.tools.eq_(processed.shape, (5, 10))


def test_EventRollEncodingProcessor():
    encoder = dcase_util.processors.EventRollEncodingProcessor(
        label_list=dcase_util.utils.Example.event_metadata_container().unique_event_labels,
        time_resolution=1.0
    )

    events = dcase_util.utils.Example.event_metadata_container().filter(filename='test1.wav')
    processed = encoder.process(data=events)

    nose.tools.eq_(processed.shape, (2, 8))
