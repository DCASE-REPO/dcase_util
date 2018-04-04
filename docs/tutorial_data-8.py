import dcase_util
data = dcase_util.utils.Example.feature_container()
data_sequencer = dcase_util.data.Sequencer(
    sequence_length=10,
    hop_length=100
)
sequenced_data = data_sequencer.sequence(data)
sequenced_data.plot()