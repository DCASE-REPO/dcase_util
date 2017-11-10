import dcase_util
data = dcase_util.utils.Example.feature_container()
data_aggregator = dcase_util.data.Aggregator(
    recipe=['mean', 'std'],
    win_length_frames=10,
    hop_length_frames=1,
)
data_aggregator.aggregate(data)
data.plot()