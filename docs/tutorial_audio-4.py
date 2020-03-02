import dcase_util
audio_container = dcase_util.containers.AudioContainer().load(
    filename=dcase_util.utils.Example.audio_filename(),
    mono=True
)
audio_container.plot(plot_type='dual')