import dcase_util
data = dcase_util.utils.Example.feature_container()
data_sequencer = dcase_util.data.Sequencer(
    frames=10,
    hop_length_frames=100
)
sequenced_data = data_sequencer.sequence(data)
sequenced_data.plot()