import dcase_util
audio_container = dcase_util.containers.AudioContainer().load(
    filename=dcase_util.utils.Example.audio_filename(),
    mono=True
)
plt.figure()
plt.subplot(2, 1, 1)
audio_container.plot(plot_type='wave', plot=False, show_filename=False)
plt.subplot(2, 1, 2)
audio_container.plot(plot_type='spec', plot=False, show_filename=False, show_colorbar=False)
plt.show()