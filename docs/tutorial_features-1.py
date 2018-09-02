import dcase_util
# Get audio in a container, mixdown of a stereo signal
audio_container = dcase_util.containers.AudioContainer().load(
  filename=dcase_util.utils.Example.audio_filename()
).mixdown()

# Create extractor
mel_extractor = dcase_util.features.MelExtractor()

# Extract features
mels = mel_extractor.extract(audio_container)

# Plotting
dcase_util.containers.DataMatrix2DContainer(
    data=mels,
    time_resolution=mel_extractor.hop_length_seconds
).plot()