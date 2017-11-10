#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
from six import iteritems
import sys
import os
import soundfile
import tempfile
import numpy
import librosa
from tqdm import tqdm
from six.moves.http_client import BadStatusLine

from dcase_util.containers import ContainerMixin, FileMixin
from dcase_util.ui.ui import FancyStringifier
from dcase_util.utils import FileFormat, is_int


class AudioContainer(ContainerMixin, FileMixin):
    """Audio container class."""
    valid_formats = [FileFormat.WAV, FileFormat.FLAC, FileFormat.M4A, FileFormat.WEBM, FileFormat.MP3]  #: Valid file formats

    def __init__(self,
                 data=None, fs=44100,
                 focus_start_samples=None, focus_stop_samples=None, focus_channel=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path
        fs : int
            Target sampling frequency, if loaded audio does have different sampling frequency, audio will be re-sampled.
            Default value "44100"

        """
        # Run ContainerMixin init
        ContainerMixin.__init__(self, **kwargs)

        # Run FileMixin init
        FileMixin.__init__(self, **kwargs)

        # Run super init to call init of mixins too
        super(AudioContainer, self).__init__(**kwargs)

        self.channel_axis = 0
        self.time_axis = 1

        # Audio data
        self._data = data
        self.data_synced_with_file = False

        self.fs = fs

        # Filename
        if self.filename:
            self.detect_file_format()
            self.validate_format()

        # Initialize focus segment variables
        self._focus_start = None
        self._focus_stop = None
        self._focus_channel = None

        # Set focus segment through properties
        self.focus_start_samples = focus_start_samples
        self.focus_stop_samples = focus_stop_samples
        self.focus_channel = focus_channel

    def __getstate__(self):
        d = super(AudioContainer, self).__getstate__()
        d.update({
            'channel_axis': self.channel_axis,
            'time_axis': self.time_axis,
            '_data': self._data,
            'data_synced_with_file': self.data_synced_with_file,
            'fs': self.fs,
            'filename': self.filename,
            '_focus_start': self._focus_start,
            '_focus_stop': self._focus_stop,
            '_focus_channel': self._focus_channel,
        })

        return d

    def __setstate__(self, d):
        super(AudioContainer, self).__setstate__(d)

        self.channel_axis = d['channel_axis']
        self.time_axis = d['time_axis']

        self._data = d['_data']
        self.data_synced_with_file = d['data_synced_with_file']
        self.fs = d['fs']
        self.filename = d['filename']
        self._focus_start = None
        self._focus_stop = None
        self._focus_channel = None
        self.focus_start = d['_focus_start']
        self.focus_stop = d['_focus_stop']
        self.focus_channel = d['_focus_channel']

    def __str__(self):
        output = ''
        ui = FancyStringifier()
        output += ui.class_name(self.__class__.__name__) + '\n'
        if self.filename:
            output += ui.data(field='Filename', value=self.filename) + '\n'
            output += ui.data(field='Synced', value='Yes' if self.data_synced_with_file else 'No') + '\n'

        output += ui.data(field='Sampling rate', value=str(self.fs)) + '\n'

        output += ui.data(indent=4, field='Channels', value=str(self.channels)) + '\n'

        output += ui.line(field='Duration') + '\n'
        output += ui.data(indent=4, field='Seconds', value=self.duration_sec, unit='sec') + '\n'
        output += ui.data(indent=4, field='Milliseconds', value=self.duration_ms, unit='ms') + '\n'
        output += ui.data(indent=4, field='Samples', value=self.duration_samples, unit='samples') + '\n'

        if self._focus_channel is not None or self._focus_start is not None or self._focus_stop is not None:
            output += ui.line(field='Focus segment') + '\n'
            if self.focus_channel is not None:
                if self.channels == 2:
                    if self._focus_channel == 0:
                        output += ui.data(indent=4,
                                          field='Channel',
                                          value='{channel} [{label}]'.format(channel=self._focus_channel,
                                                                             label='Left Channel')) + '\n'

                    elif self._focus_channel == 1:
                        output += ui.data(indent=4,
                                          field='Channel',
                                          value='{channel} [{label}]'.format(channel=self._focus_channel,
                                                                             label='Right Channel')) + '\n'

                else:
                    output += ui.data(indent=4, field='Channel', value=self._focus_channel) + '\n'

            output += ui.line(indent=4, field='Duration') + '\n'
            output += ui.data(indent=6, field='Seconds', value=self.focus_stop_seconds - self.focus_start_seconds, unit='sec') + '\n'
            output += ui.data(indent=6, field='Samples', value=self.focus_stop_samples - self.focus_start_samples, unit='sec') + '\n'

            output += ui.line(indent=4, field='Start point') + '\n'
            output += ui.data(indent=6, field='Seconds', value=self.focus_start_seconds, unit='sec') + '\n'
            output += ui.data(indent=6, field='Samples', value=self.focus_start_samples, unit='samples') + '\n'

            output += ui.line(indent=4, field='Stop point') + '\n'
            output += ui.data(indent=6, field='Seconds', value=self.focus_stop_seconds, unit='sec') + '\n'
            output += ui.data(indent=6, field='Samples', value=self.focus_stop_samples, unit='samples') + '\n'

        return output

    def __nonzero__(self):
        return self.loaded

    def __getitem__(self, i):
        """
        Get ith sample of first channel
        """

        return self._data[0][i]

    @property
    def data(self):
        """Audio data

        Returns
        -------
        numpy.ndarray
            Audio data

        """

        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.data_synced_with_file = False

    @property
    def focus_start_samples(self):
        """Focus segment start in samples.

        Returns
        -------
        int
            Focus segment start in samples

        """

        return self._focus_start

    @focus_start_samples.setter
    def focus_start_samples(self, value):
        if value is not None and value > 0:
            value = int(value)
            self._focus_start = value

            if self._focus_stop is not None and self._focus_stop < self._focus_start:
                # focus points are reversed
                start = self._focus_start
                self._focus_start = self._focus_stop
                self._focus_stop = start

        else:
            self._focus_start = 0

    @property
    def focus_start_seconds(self):
        """Focus segment start in seconds.

        Returns
        -------
        int
            Focus segment start in seconds

        """

        return self._sample_to_time(sample=self.focus_start_samples)

    @focus_start_seconds.setter
    def focus_start_seconds(self, value):
        self.focus_start_samples = self._time_to_sample(time=value)

    @property
    def focus_stop_samples(self):
        """Focus segment stop in samples.

        Returns
        -------
        int
            Focus segment stop in samples

        """
        if self._focus_stop is None:
            return self.length

        else:
            return self._focus_stop

    @focus_stop_samples.setter
    def focus_stop_samples(self, value):
        if value is None:
            self._focus_stop = None

        else:
            if value <= self.duration_samples and value is not None:
                value = int(value)
                self._focus_stop = value

                if self._focus_start is not None and self._focus_stop < self._focus_start:
                    # focus points are reversed
                    start = self._focus_start
                    self._focus_start = self._focus_stop
                    self._focus_stop = start

            else:
                self._focus_stop = self.duration_samples

    @property
    def focus_stop_seconds(self):
        """Focus segment stop in seconds.

        Returns
        -------
        int
            Focus segment stop in seconds

        """

        return self._sample_to_time(sample=self.focus_stop_samples)

    @focus_stop_seconds.setter
    def focus_stop_seconds(self, value):
        self.focus_stop_samples = self._time_to_sample(time=value)

    @property
    def focus_channel(self):
        """Focus channel

        Returns
        -------
        int or str
            Focus channel

        """

        return self._focus_channel

    @focus_channel.setter
    def focus_channel(self, value):
        if value is not None and is_int(value):
            if 0 <= value < self.channels:
                self._focus_channel = value

            else:
                self._focus_channel = None

        elif value is not None and isinstance(value, str):
            if value.lower() == 'mixdown':
                self._focus_channel = 'mixdown'

            elif value.lower() == 'left' or value.lower() == 'l':
                self._focus_channel = 0

            elif value.lower() == 'right' or value.lower() == 'r':
                self._focus_channel = 1

            else:
                # Unknown channel label given
                message = '{name}: Unknown channel [{channel}]'.format(name=self.__class__.__name__, channel=value)
                self.logger.exception(message)
                raise ValueError(message)

        else:
            self._focus_channel = None

    @property
    def loaded(self):
        """Audio load status.

        Returns
        -------
        bool
            Audio status

        """

        if isinstance(self._data, numpy.ndarray) and len(self._data) > 0:
            return True
        else:
            return False

    @property
    def shape(self):
        """Audio data shape.

        Returns
        -------
        tuple
            shape of audio data

        """

        if self.loaded:
            return self._data.shape
        else:
            return None

    @property
    def length(self):
        """Length of audio data in samples.

        Returns
        -------
        int
            Audio length

        """

        if self.loaded:
            if len(self._data.shape) == 1:
                return self._data.shape[0]

            elif len(self._data.shape) > 1:
                return self._data.shape[-1]

            else:
                return 0

        else:
            return 0

    @property
    def duration_samples(self):
        """Duration of audio data in samples.

        Returns
        -------
        int
            Audio duration

        """

        return self.length

    @property
    def duration_ms(self):
        """Duration of audio data in milliseconds.

        Returns
        -------
        float
            Audio duration

        """

        return (self.length / float(self.fs)) * 1000

    @property
    def duration_sec(self):
        """Duration of audio data in seconds.

        Returns
        -------
        float
            Audio duration

        """

        return self.length / float(self.fs)

    @property
    def channels(self):
        """Number of audio channels.

        Returns
        -------
        int
            Number of audio channels

        """

        if self.loaded:
            if len(self.data.shape) == 2:
                return self._data.shape[self.channel_axis]
            elif len(self.data.shape) == 1:
                return 1
            else:
                return 0
        else:
            return 0

    @property
    def streams(self):
        """Rename channels for compatibility.

        Returns
        -------
        int
            Number of streams

        """
        return self.channels

    @property
    def empty(self):
        """Check if audio data is empty.

        In case audio is not yet loaded it is first loaded into container from disk.

        Returns
        -------
        bool

        """

        if self.loaded:
            if self.length == 0:
                return True

            else:
                return False

        else:
            if self.filename and self.exists():
                # Audio data is not yet loaded and filename set and file exists, load the data from a file
                self.load()

                if self.length == 0:
                    return True

                else:
                    return False

            else:
                return True

    def load(self, filename=None, fs=None, mono=False, res_type='kaiser_best', start=None, stop=None):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path, if None given filename parameter given to class constructor is used.

        fs : int
            Target sampling frequency, if loaded audio does have different sampling frequency, audio will
            be re-sampled. If None given, value given to class constructor is used.

        mono : bool
            Monophonic target, multi-channel audio will be down-mixed.

        res_type : str
            Resample type, defined by Librosa

        start : float, optional
            Segment start time in seconds

        stop : float, optional
            Segment stop time in seconds

        Raises
        ------
        IOError:
            File does not exists or has unknown file format

        Returns
        -------
        self

        """

        if filename is not None:
            self.filename = filename
            self.detect_file_format()
            self.validate_format()

        if self.exists():
            if fs is not None:
                self.fs = fs

            if self.format == FileFormat.WAV:
                info = soundfile.info(file=self.filename)

                # Handle segment start and stop
                if start is not None and stop is not None:
                    start_sample = int(start * info.samplerate)
                    stop_sample = int(stop * info.samplerate)
                    if stop_sample > info.frames:
                        stop_sample = info.frames
                else:
                    start_sample = None
                    stop_sample = None

                self._data, source_fs = soundfile.read(file=self.filename, start=start_sample, stop=stop_sample)
                self._data = self._data.T

                # Down-mix audio
                if mono and len(self._data.shape) > 1:
                    self._data = numpy.mean(self._data, axis=self.channel_axis)

                # Resample
                if self.fs != source_fs:
                    import librosa
                    self._data = librosa.core.resample(self._data, source_fs, self.fs, res_type=res_type)

            elif self.format in [FileFormat.FLAC, FileFormat.M4A, FileFormat.WEBM]:
                import librosa
                if start is not None and stop is not None:
                    offset = start
                    duration = stop - start
                else:
                    offset = 0.0
                    duration = None

                self._data, self.fs = librosa.load(
                    self.filename,
                    sr=self.fs,
                    mono=mono,
                    res_type=res_type,
                    offset=offset,
                    duration=duration
                )

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File does not exists [{file}]'.format(name=self.__class__.__name__, file=self.filename)
            self.logger.exception(message)
            raise IOError(message)

        # Check if after load function is defined, call if found
        if hasattr(self, '_after_load'):
            self._after_load()

        # Internal data is synced with the file, until it is edited.
        self.data_synced_with_file = True

        return self

    def save(self, filename=None, bit_depth=16):
        """Save audio

        Parameters
        ----------
        filename : str, optional
            File path, if None given filename parameter given to class constructor is used.

        bit_depth : int, optional
            Bit depth for audio

        Raises
        ------
        ImportError:
            Error if file format specific module cannot be imported
        IOError:
            File has unknown file format

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename
            self.detect_file_format()
            self.validate_format()

        if self.filename is None or self.filename == '':
            message = '{name}: Filename is empty [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        # Check if before save function is defined, call if found
        if hasattr(self, '_before_save'):
            self._before_save()

        if self.format == FileFormat.WAV:
            if bit_depth == 16:
                soundfile.write(file=self.filename,
                                data=self._data.T,
                                samplerate=self.fs,
                                subtype='PCM_16')

            elif bit_depth == 24:
                soundfile.write(file=self.filename,
                                data=self._data.T,
                                samplerate=self.fs,
                                subtype='PCM_24')

            elif bit_depth == 32:
                soundfile.write(file=self.filename,
                                data=self._data.T,
                                samplerate=self.fs,
                                subtype='PCM_32')

            elif bit_depth is None:
                soundfile.write(file=self.filename,
                                data=self._data.T,
                                samplerate=self.fs)

            else:
                message = '{name}: Unexpected bit depth [{bitdepth}]'.format(name=self.__class__.__name__,
                                                                             bitdepth=bit_depth)
                self.logger.exception(message)
                raise IOError(message)

        elif self.format == FileFormat.FLAC:
            soundfile.write(file=self.filename,
                            data=self._data.T,
                            samplerate=self.fs)

        else:
            message = '{name}: Unknown format for saving [{format}]'.format(name=self.__class__.__name__,
                                                                            format=self.filename)
            self.logger.exception(message)
            raise IOError(message)

        # Check if after save function is defined, call if found
        if hasattr(self, '_after_save'):
            self._after_save()

        # Internal data is synced with the file, until it is edited.
        self.data_synced_with_file = True

        return self

    def load_from_youtube(self, query_id, start=None, stop=None, mono=False, silent=True):
        """Load audio data from youtube

        Parameters
        ----------
        query_id : str
            Youtube query id

        start : float, optional
            Segment start time in seconds

        stop : float, optional
            Segment stop time in seconds

        mono : bool
            Monophonic target, multi-channel audio will be down-mixed.

        silent : bool
            Switch to show progress bar

        Raises
        ------
        IOError:
            Youtube video does not exists or cannot be downloaded

        Returns
        -------
        self

        """

        def progress_hook(t):
            """Wraps tqdm instance. Don't forget to close() or __exit__()
            the tqdm instance once you're done with it (easiest using `with` syntax).
            """

            def inner(total, recvd, ratio, rate, eta):
                t.total = int(total / 1024.0)
                t.update(int(recvd / 1024.0))

            return inner

        import pafy
        from youtube_dl.utils import ExtractorError

        try:
            # Access youtube video and get best quality audio stream
            youtube_audio = pafy.new(
                url='https://www.youtube.com/watch?v={query_id}'.format(query_id=query_id),
                basic=False,
                gdata=False,
                size=False
            ).getbestaudio()

            # Get temp file
            tmp_file = tempfile.NamedTemporaryFile(suffix='.'+youtube_audio.extension)
            if not silent:
                # Create download progress bar
                download_progress_bar = tqdm(
                    desc="{0: <25s}".format('Download youtube item '),
                    file=sys.stdout,
                    unit='B',
                    unit_scale=True,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )
                callback = progress_hook(download_progress_bar)
            else:
                callback = None

            # Download audio
            youtube_audio.download(
                filepath=tmp_file.name,
                quiet=True,
                callback=callback
            )

            if not silent:
                # Close progress bar
                download_progress_bar.close()

                # Create audio processing progress bar
                audio_processing_progress_bar = tqdm(
                    desc="{0: <25s}".format('Processing '),
                    initial=0,
                    total=4,
                    file=sys.stdout,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )

            # Store current filename
            filename = self.filename

            # Load audio segment
            self.load(
                filename=tmp_file.name,
                mono=mono,
                fs=self.fs,
                res_type='kaiser_best',
                start=float(start) if start is not None else None,
                stop=float(stop) if stop is not None else None
            )

            # Restore filename
            if filename:
                self.filename = filename
                self.detect_file_format()

            if not silent:
                audio_processing_progress_bar.update(1)
                audio_processing_progress_bar.update(3)
                audio_processing_progress_bar.close()

        except (IOError, BadStatusLine, ExtractorError) as e:
            # Store files with errors
            raise IOError(e.message)

        except (KeyboardInterrupt, SystemExit):
            # Remove temporal file and current audio file.
            os.remove(self.filename)
            raise

        return self

    def normalize(self, headroom=0.005):
        """Normalize audio data.

        Data is normalized between -(1.0 - headroom) and +(1.0 - headroom)

        Parameters
        ----------
        headroom : float
            How much headroom there should be left under 1.0

        Returns
        -------
        self

        """

        if self.channels > 1:
            for channel_data in self._data:
                mean_value = numpy.mean(channel_data)
                channel_data -= mean_value

                max_value = max(abs(channel_data)) + headroom
                channel_data /= max_value
        else:
            mean_value = numpy.mean(self._data)
            self._data -= mean_value

            max_value = max(abs(self._data)) + headroom
            self._data /= max_value

        return self

    def resample(self, target_fs, scale=True, res_type='kaiser_best'):
        """Resample audio data.

        Parameters
        ----------
        target_fs : int
            Target sampling rate

        scale : bool
            Scale the resampled signal to have approximately equal total energy (see `librosa.core.resample`)

        res_type : str
            Resample type (see `librosa.core.resample`)

        Returns
        -------
        self

        """

        if target_fs != self.fs:
            self._data = librosa.resample(
                y=self._data,
                orig_sr=self.fs,
                target_sr=target_fs,
                scale=scale,
                res_type=res_type
            )
            self.fs = target_fs

        return self

    def mixdown(self):
        """Mix all audio channels into single channel.

        Returns
        -------
        self

        """

        self.reset_focus()
        self.set_focus(channel='mixdown')
        self.freeze()

        return self

    def reset_focus(self):
        """Reset focus segment.

        Returns
        -------
        self

        """

        self._focus_start = None
        self._focus_stop = None
        self._focus_channel = None

        return self

    def set_focus(self,
                  start=None, stop=None, duration=None,
                  start_seconds=None, stop_seconds=None, duration_seconds=None,
                  channel=None
                  ):
        """Set focus segment

        Parameters
        ----------
        start : int
            Sample index of focus segment start

        stop : int
            Sample index of focus segment stop

        duration : int
            Sample count of focus segment

        start_seconds : float
            Time stamp (in seconds) of focus segment start

        stop_seconds : float
            Time stamp (in seconds) of focus segment stop

        duration_seconds : float
            Duration (in seconds) of focus segment

        channel : int or str
            Audio channel id or name to focus. In case of stereo signal, valid channel labels to select
            single channel are 'L', 'R', 'left', and 'right' or 0, 1, and to get mixed down
            version of all channels 'mixdown'.

        Returns
        -------
        self

        """

        if start is not None or stop is not None or duration is not None:
            # Sample based setting
            if start is not None and stop is not None:
                self.focus_start_samples = start
                self.focus_stop_samples = stop

            elif start is not None and duration is not None:
                self.focus_start_samples = start
                self.focus_stop_samples = start + duration

        elif start_seconds is not None or stop_seconds is not None or duration_seconds is not None:
            # Time based setting
            if start_seconds is not None and stop_seconds is not None:
                self.focus_start_samples = self._time_to_sample(time=start_seconds)
                self.focus_stop_samples = self._time_to_sample(time=stop_seconds)

            elif start_seconds is not None and duration_seconds is not None:
                self.focus_start_samples = self._time_to_sample(time=start_seconds)
                self.focus_stop_samples = self._time_to_sample(time=start_seconds + duration_seconds)

        else:
            # Reset
            self._focus_start = None
            self._focus_stop = None

        self.focus_channel = channel

        return self

    def get_focused(self):
        """Get focus segment from audio data.

        Returns
        -------
        numpy.ndarray

        """

        focused_data = None

        if self.focus_start_samples is not None or self.focus_stop_samples is not None:
            if self.focus_start_samples is not None:
                focus_start_samples = self.focus_start_samples

            else:
                focus_start_samples = 0

            if self.focus_stop_samples is not None:
                focus_stop_samples = self.focus_stop_samples

            else:
                focus_stop_samples = self.length

            if self.channels == 1:
                # We have single channel
                focused_data = self._data[focus_start_samples:focus_stop_samples]

            elif self.channels > 1:
                # We have multichannel audio
                focused_data = []
                for channel_data in self._data:
                    focused_data.append(channel_data[focus_start_samples:focus_stop_samples])

                focused_data = numpy.vstack(focused_data)

        else:
            focused_data = self._data

        if self.focus_channel is not None and is_int(self.focus_channel) and 0 <= self.focus_channel < self.channels:
            return focused_data[self.focus_channel, :]

        elif self.focus_channel == 'mixdown':
            return numpy.mean(focused_data, axis=self.channel_axis)

        else:
            return focused_data

    def freeze(self):
        """Freeze focus segment, copy segment to be container's data.

        Returns
        -------
        self

        """

        self._data = self.get_focused()
        self.reset_focus()

        return self

    def plot(self, plot_type='wave'):
        """Visualize audio data

        Parameters
        ----------

        plot_type : str
            Visualization type, 'wave' for waveform plot, 'spec' for spectrogram.

        Returns
        -------
        self

        """

        if plot_type == 'wave':
            self.plot_wave()
        elif plot_type == 'spec':
            self.plot_spec()

    def plot_wave(self, x_axis='time', max_points=50000.0, offset=0.0, color='#333333', alpha=1.0):
        """Visualize audio data as waveform.

        Parameters
        ----------

        x_axis : str
            X-axis type

        max_points : float
            Maximum number of time-points to plot (see `librosa.display.waveplot`).

        offset : float
            Horizontal offset (in time) to start the waveform plot (see `librosa.display.waveplot`).

        color : str
            Waveform fill color in hex-code.

        alpha : float
            Alpha of the waveform fill color.

        Returns
        -------
        self

        """

        import matplotlib.pyplot as plt
        from librosa.display import waveplot
        plt.figure()
        for channel_id, channel_data in enumerate(self.get_focused()):
            plt.subplot(self.channels, 1, channel_id + 1)

            waveplot(
                y=channel_data.ravel(),
                sr=self.fs,
                x_axis=x_axis,
                max_points=max_points,
                offset=offset,
                color=color,
                alpha=alpha
            )

            plt.ylabel('Channel {channel:d}'.format(channel=channel_id))
            if channel_id == 0:
                if self.filename:
                    plt.title(self.filename)

        plt.show()

        return self

    def plot_spec(self, spec_type='log', hop_length=512, cmap='magma'):
        """Visualize audio data as spectrogram.

        Parameters
        ----------

        spec_type : str
            Spectrogram type, use 'linear', 'log', 'cqt', 'cqt_hz', and 'cqt_note'.

        hop_length : float
            Hop length, also used to determine time scale in x-axis (see `librosa.display.specshow`).

        cmap : float
            Color map (see `librosa.display.specshow`).

        Returns
        -------
        self

        """

        from librosa.display import specshow
        import matplotlib.pyplot as plt

        plt.figure()
        for channel_id, channel_data in enumerate(self.get_focused()):
            plt.subplot(self.channels, 1, channel_id+1)

            if spec_type in ['linear', 'log']:
                D = librosa.logamplitude(numpy.abs(librosa.stft(channel_data.ravel())) ** 2, ref_power=numpy.max)
            elif spec_type.startswith('cqt'):
                D = librosa.amplitude_to_db(librosa.cqt(channel_data.ravel(), sr=self.fs), ref=numpy.max)

            if spec_type == 'linear':
                specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='linear',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'log':
                specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='log',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'cqt_hz' or 'cqt':
                specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='cqt_hz',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'cqt_note':
                specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='cqt_note',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            plt.colorbar(format='%+2.0f dB')
            plt.ylabel('Channel {channel:d}'.format(channel=channel_id))
            if channel_id == 0 and self.filename:
                plt.title(self.filename)

        plt.show()

    def _time_to_sample(self, time):
        """Time to sample index.

        Parameters
        ----------
        time : float
            Time stamp in seconds

        Returns
        -------
        int

        """

        return int(time * self.fs)

    def _sample_to_time(self, sample):
        """Sample index to time.

        Parameters
        ----------
        sample : int
            Sample index

        Returns
        -------
        float

        """

        return sample / float(self.fs)
