import dcase_util
audio_container = dcase_util.containers.AudioContainer().load(
  filename=dcase_util.utils.Example.audio_filename()
)
audio_container.filename = None
audio_container.plot_wave(channel_labels=['Left', 'Right'], color=['#333333', '#777777'])