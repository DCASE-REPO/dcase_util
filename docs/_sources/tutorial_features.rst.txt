.. _tutorial_features:

Acoustic features
-----------------

Library provides basic acoustic feature extractors: `dcase_util.features.MelExtractor`,
`dcase_util.features.MfccStaticExtractor`, `dcase_util.features.MfccDeltaExtractor`, `dcase_util.features.MfccAccelerationExtractor`,
`dcase_util.features.ZeroCrossingRateExtractor`, `dcase_util.features.RMSEnergyExtractor`, and
`dcase_util.features.SpectralCentroidExtractor`.

Extracting features
===================

Extracting mel-band energies for the audio signal (using default parameters)::

    # Get audio in a container, mixdown of a stereo signal
    audio_container = dcase_util.containers.AudioContainer().load(
      filename=dcase_util.utils.Example.audio_filename()
    ).mixdown()

    # Create extractor
    mel_extractor = dcase_util.features.MelExtractor()

    # Extract features
    mels = mel_extractor.extract(audio_container)

Extracting mel-band energies for specific audio segment::

    # Get audio in a container, mixdown of a stereo signal
    audio_container = dcase_util.containers.AudioContainer().load(
      filename=dcase_util.utils.Example.audio_filename()
    ).mixdown()

    # Set focus
    audio_container.set_focus(start_seconds=1.0, stop_seconds=4.0)

    # Create extractor
    mel_extractor = dcase_util.features.MelExtractor()

    # Extract features
    mels = mel_extractor.extract(audio_container.get_focused())

    # Plot
    dcase_util.containers.DataMatrix2DContainer(
        data=mels,
        time_resolution=mel_extractor.hop_length_seconds
    ).plot()


Extract features directly from numpy matrix::

    # Create an audio signal
    t = numpy.linspace(0, 2, 2 * 44100, endpoint=False)
    x1 = numpy.sin(220 * 2 * numpy.pi * t)

    # Create extractor
    mel_extractor = dcase_util.features.MelExtractor()

    # Extract features
    mels = mel_extractor.extract(x1)

    # Plot
    dcase_util.containers.DataMatrix2DContainer(
        data=mels,
        time_resolution=mel_extractor.hop_length_seconds
    ).plot()

All audio extractors provided in the library work for single channel audio.

Visualization
=============

Plotting the extracted features::

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

.. plot::

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