import dcase_util
data = dcase_util.utils.Example.feature_container()
normalizer = dcase_util.data.Normalizer(
    **data.stats
)
normalizer.normalize(data)
data.plot()