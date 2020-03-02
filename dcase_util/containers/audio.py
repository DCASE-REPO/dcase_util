#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
import sys
import os
import soundfile
import tempfile
import numpy
import librosa
from six.moves.http_client import BadStatusLine

from dcase_util.containers import ContainerMixin, FileMixin
from dcase_util.ui.ui import FancyStringifier, FancyHTMLStringifier
from dcase_util.utils import FileFormat, Path, is_int, is_jupyter, get_audio_info


class AudioContainer(ContainerMixin, FileMixin):
    """Audio container class."""
    valid_formats = [FileFormat.WAV, FileFormat.FLAC,
                     FileFormat.OGG,
                     FileFormat.M4A, FileFormat.WEBM,
                     FileFormat.MP3, FileFormat.MP4]  #: Valid file formats

    def __init__(self,
                 data=None, fs=44100,
                 focus_start_samples=None, focus_stop_samples=None, focus_channel=None, channel_labels=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        data : numpy.ndarray or list of numpy.ndarray
            Data to initialize the container
            Default value None

        fs : int
            Target sampling frequency, if loaded audio does have different sampling frequency, audio will be re-sampled.
            Default value "44100"

        focus_start_samples : int
            Focus segment start
            Default value None

        focus_stop_samples : int
            Focus segment stop
            Default value None

        focus_channel : int
            Focus segment channel
            Default value None

        channel_labels : list
            Channel names
            Default value None

        filename : str, optional
            File path

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
        if data is None:
            # Initialize with array
            data = numpy.ndarray((0, ))

        if isinstance(data, list):
            data = numpy.vstack(data)

        self._data = data
        self.data_synced_with_file = False

        self.fs = fs
        self.filetype_info = None

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

        self.channel_labels = channel_labels

    def __getstate__(self):
        d = super(AudioContainer, self).__getstate__()
        d.update({
            'channel_axis': self.channel_axis,
            'time_axis': self.time_axis,
            '_data': self._data,
            'data_synced_with_file': self.data_synced_with_file,
            'fs': self.fs,
            'filetype_info': self.filetype_info,
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
        self.filetype_info = d['filetype_info']
        self.filename = d['filename']
        self._focus_start = None
        self._focus_stop = None
        self._focus_channel = None
        self.focus_start = d['_focus_start']
        self.focus_stop = d['_focus_stop']
        self.focus_channel = d['_focus_channel']

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = ''
        output += ui.class_name(self.__class__.__name__, indent=indent) + '\n'
        if self.filename:
            output += ui.data(
                field='Filename',
                value=self.filename,
                indent=indent
            ) + '\n'

            if self.filetype_info and self.filetype_info.values:
                output += ui.data(
                    field='Format',
                    value=self.format + ' (' + ', '.join(self.filetype_info.values()) + ')',
                    indent=indent
                ) + '\n'

            else:
                output += ui.data(field='Format', value=self.format, indent=indent) + '\n'

            output += ui.data(
                field='Synced',
                value='Yes' if self.data_synced_with_file else 'No',
                indent=indent
            ) + '\n'

        output += ui.data(
            field='Sampling rate',
            value=str(self.fs),
            unit='hz',
            indent=indent
        ) + '\n'

        output += ui.data(
            field='Channels',
            value=str(self.channels),
            indent=indent
        ) + '\n'

        if self.channel_labels:
            if isinstance(self.channel_labels, list):
                output += ui.data(
                    field='Labels',
                    value='',
                    indent=indent + 2
                ) + '\n'
                for channel_id, label in enumerate(self.channel_labels):
                    output += ui.data(
                        field='[{channel_id}]'.format(channel_id=channel_id),
                        value=str(label),
                        indent=indent+3
                    ) + '\n'

        output += ui.line(field='Duration', indent=indent) + '\n'
        output += ui.data(
            indent=indent + 2,
            field='Seconds',
            value=self.duration_sec,
            unit='sec'
        ) + '\n'

        output += ui.data(
            indent=indent + 2,
            field='Milliseconds',
            value=self.duration_ms,
            unit='ms'
        ) + '\n'

        output += ui.data(
            indent=indent + 2,
            field='Samples',
            value=self.duration_samples,
            unit='samples'
        ) + '\n'

        if self._focus_channel is not None or self._focus_start is not None or self._focus_stop is not None:
            output += ui.line(field='Focus segment', indent=indent) + '\n'
            if self.focus_channel is not None:
                if self.channels == 2:
                    if self._focus_channel == 0:
                        output += ui.data(
                            indent=indent + 4,
                            field='Channel',
                            value='{channel} [{label}]'.format(
                                channel=self._focus_channel,
                                label='Left Channel'
                            )
                        ) + '\n'

                    elif self._focus_channel == 1:
                        output += ui.data(
                            indent=indent + 4,
                            field='Channel',
                            value='{channel} [{label}]'.format(
                                channel=self._focus_channel,
                                label='Right Channel'
                            )
                        ) + '\n'

                else:
                    output += ui.data(
                        indent=indent + 4,
                        field='Channel',
                        value=self._focus_channel
                    ) + '\n'

            output += ui.line(
                indent=indent + 2,
                field='Duration'
            ) + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Seconds',
                value=self.focus_stop_seconds - self.focus_start_seconds,
                unit='sec'
            ) + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Samples',
                value=self.focus_stop_samples - self.focus_start_samples,
                unit='sec'
            ) + '\n'

            output += ui.line(
                indent=indent + 2,
                field='Start point'
            ) + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Seconds',
                value=self.focus_start_seconds,
                unit='sec') + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Samples',
                value=self.focus_start_samples,
                unit='samples'
            ) + '\n'

            output += ui.line(
                indent=indent + 2,
                field='Stop point'
            ) + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Seconds',
                value=self.focus_stop_seconds,
                unit='sec'
            ) + '\n'

            output += ui.data(
                indent=indent + 4,
                field='Samples',
                value=self.focus_stop_samples,
                unit='samples'
            ) + '\n'

        return output

    def __nonzero__(self):
        return self.loaded

    def __getitem__(self, i):
        """Get ith sample, in case of multiple channels array is across channels is returned"""

        if not isinstance(i, int):
            raise TypeError("Index should be integer")

        if i < 0 or i > self.length:
            raise KeyError(i)

        if len(self._data.shape) == 1:
            return self._data[i]

        elif len(self._data.shape) > 1:
            return self._data[:, i]

        else:
            return None

    def __setitem__(self, i, value):
        """Set ith sample"""

        if not isinstance(i, int):
            raise TypeError("Index should be integer")

        if i < 0 or i > self.length:
            raise KeyError(i)

        if len(self._data.shape) == 1:
            self._data[i] = value

        elif len(self._data.shape) > 1:
            self._data[:, i] = value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return self.length

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

    def load(self, filename=None, fs='native', mono=False, res_type='kaiser_best', start=None, stop=None, auto_trimming=False):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path, if None given filename parameter given to class constructor is used.

        fs : int or str
            Target sampling frequency, if loaded audio does have different sampling frequency, audio will
            be re-sampled. If None given, value given to class constructor is used. If 'native' is given then
            native sampling frequency defined by audio file is used.
            Default value 'native'

        mono : bool
            Monophonic target, multi-channel audio will be down-mixed.
            Default value False

        res_type : str
            Resample type, defined by Librosa.
            Default value 'kaiser_best'

        start : float, optional
            Segment start time in seconds.
            Default value None

        stop : float, optional
            Segment stop time in seconds.
            Default value None

        auto_trimming : bool
            In case using segment stop parameter, the parameter is adjusted automatically if it exceeds the file duration.
            Default value False

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
            if fs is None:
                # Use sampling frequency defined in class construction.
                fs = self.fs
            info = get_audio_info(filename=self.filename)
            # Check start and stop parameters against file duration
            if start is not None and start < 0:
                message = '{name}: Start parameter is negative [{file}]'.format(
                    name=self.__class__.__name__,
                    file=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

            elif info['duration_sec'] and start is not None and start > info['duration_sec']:
                message = '{name}: Start parameter exceeds file length [{file}]'.format(
                    name=self.__class__.__name__,
                    file=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

            if stop is not None and stop < 0:
                message = '{name}: Stop parameter is negative [{file}]'.format(
                    name=self.__class__.__name__,
                    file=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

            elif info['duration_sec'] and stop is not None and stop > info['duration_sec'] and not auto_trimming:
                message = '{name}: Stop parameter exceeds file length [{file}]'.format(
                    name=self.__class__.__name__,
                    file=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

            if self.format == FileFormat.WAV:

                self.filetype_info = {
                    'subtype': info['subtype']['name'],
                    'subtype_info': info['subtype']['info']
                }

                # Handle segment start and stop
                if start is not None and stop is not None:
                    start_sample = int(start * info['fs'])
                    stop_sample = int(stop * info['fs'])

                    if stop_sample > info['duration_samples']:
                        stop_sample = info['duration_samples']

                else:
                    start_sample = None
                    stop_sample = None

                self._data, source_fs = soundfile.read(
                    file=self.filename,
                    start=start_sample,
                    stop=stop_sample
                )

                self._data = self._data.T

                # Down-mix audio
                if mono and len(self._data.shape) > 1:
                    self._data = numpy.mean(self._data, axis=self.channel_axis)

                if fs == 'native':
                    # Use native sampling frequency.
                    self.fs = source_fs

                else:
                    # Target sampling frequency defined, possibly re-sample signal.
                    if fs != source_fs:
                        self._data = librosa.core.resample(
                            self._data,
                            source_fs,
                            fs,
                            res_type=res_type
                        )

                    # Store sampling frequency
                    self.fs = fs

            elif self.format in [FileFormat.FLAC, FileFormat.OGG,
                                 FileFormat.MP3,
                                 FileFormat.M4A, FileFormat.MP4, FileFormat.WEBM]:
                # Handle segment start and stop
                if start is not None and stop is not None:
                    offset = start
                    duration = stop - start

                elif start is not None:
                    offset = start
                    duration = None

                else:
                    offset = 0.0
                    duration = None

                if fs == 'native':
                    # Use native sampling frequency
                    sr = None

                else:
                    # Use target sampling frequency
                    sr = fs

                self._data, self.fs = librosa.load(
                    self.filename,
                    sr=sr,
                    mono=mono,
                    res_type=res_type,
                    offset=offset,
                    duration=duration
                )

                if not auto_trimming and duration is not None and duration != self.duration_sec:
                    message = '{name}: Check start and stop parameter, requested duration exceeds the file length [{file}]'.format(
                        name=self.__class__.__name__,
                        file=self.filename
                    )

                    self.logger.exception(message)
                    raise IOError(message)

            else:
                message = '{name}: Unknown format [{format}]'.format(
                    name=self.__class__.__name__,
                    format=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File does not exists [{file}]'.format(
                name=self.__class__.__name__,
                file=self.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        # Check if after load function is defined, call if found
        if hasattr(self, '_after_load'):
            self._after_load()

        # Internal data is synced with the file, until it is edited.
        self.data_synced_with_file = True

        return self

    def save(self, filename=None, bit_depth=16, bit_rate=None):
        """Save audio

        Parameters
        ----------
        filename : str, optional
            File path, if None given filename parameter given to class constructor is used.
            Default value None

        bit_depth : int, optional
            Bit depth for audio.
            Default value 16

        bit_rate : int, optional
            Bit rate for compressed audio formats.
            Default value None

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
                subtype = 'PCM_16'

            elif bit_depth == 24:
                subtype = 'PCM_24'

            elif bit_depth == 32:
                subtype = 'PCM_32'

            else:
                message = '{name}: Unexpected bit depth [{bitdepth}]'.format(
                    name=self.__class__.__name__,
                    bitdepth=bit_depth
                )

                self.logger.exception(message)
                raise IOError(message)

            soundfile.write(
                file=self.filename,
                data=self._data.T,
                samplerate=self.fs,
                subtype=subtype
            )

        elif self.format == FileFormat.FLAC:
            if bit_depth == 16:
                subtype = 'PCM_16'

            elif bit_depth == 24:
                subtype = 'PCM_24'

            elif bit_depth == 32:
                subtype = 'PCM_32'

            else:
                message = '{name}: Unexpected bit depth [{bitdepth}]'.format(
                    name=self.__class__.__name__,
                    bitdepth=bit_depth
                )

                self.logger.exception(message)
                raise IOError(message)

            soundfile.write(
                file=self.filename,
                data=self._data.T,
                samplerate=self.fs,
                format='flac',
                subtype=subtype
            )

        elif self.format == FileFormat.OGG:
            soundfile.write(
                file=self.filename,
                data=self._data.T,
                samplerate=self.fs,
                format='OGG',
                subtype='VORBIS'
            )

        elif self.format == FileFormat.MP3:
            # Notice: Saving with MP3 format results in slightly longer signal than original.
            # Difference is due to padding in the compression algorithm, and is usually around 200 - 1000 samples.
            import subprocess
            import platform

            if platform.system() == 'Windows':
                ffmpeg_binary = "ffmpeg.exe"

            else:
                ffmpeg_binary = "ffmpeg"

            if bit_rate not in [8, 16, 24, 32, 40, 48, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]:
                message = '{name}: Unsupported bit rate [{bitrate}]'.format(
                    name=self.__class__.__name__,
                    bitrate=bit_rate
                )

                self.logger.exception(message)
                raise IOError(message)

            command = [
                ffmpeg_binary,
                '-y',                                               # enable overwrite file
                '-f', 's16le',                                      # input format
                '-acodec', 'pcm_s16le',                             # input bit depth
                '-r', str(self.fs),                                 # sampling rate
                '-ac', str(self.channels),                          # amount of channels
                '-i', '-',                                          # input from pipe
                '-vn',                                              # no video input
                '-acodec', 'libmp3lame',                            # output audio codec
                '-b:a', "{bitrate:d}k".format(bitrate=bit_rate),    # bit rate
                self.filename                                       # output filename
            ]

            popen_parameters = {
                'stdin': subprocess.PIPE,
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE
            }

            pipe = subprocess.Popen(
                command,
                **popen_parameters
            )

            # Convert signal data from float [-1,1] to signed 16-bit
            audio_signal = numpy.asarray(self.data).T
            signal_max_value = 2 ** (16 - 1)
            audio_signal = (audio_signal * signal_max_value).clip(
                -signal_max_value,
                signal_max_value - 1
            ).astype('int16')

            try:
                try:
                    pipe.stdin.write(
                        audio_signal.tobytes()
                    )

                except NameError:
                    pipe.stdin.write(
                        audio_signal.tostring()
                    )

            except IOError as error:
                pipe_error = pipe.stderr.read()
                error = str(error)
                error += "\n\nFFMPEG encountered the following error {filename}:".format(filename=self.filename)
                error += "\n\n" + str(pipe_error)

                raise IOError(error)

            pipe.stdin.close()
            if pipe.stderr is not None:
                pipe.stderr.close()

            pipe.wait()

        else:
            message = '{name}: Unknown format for saving [{format}]'.format(
                name=self.__class__.__name__,
                format=self.filename
            )

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
            Youtube query id.

        start : float, optional
            Segment start time in seconds.
            Default value None

        stop : float, optional
            Segment stop time in seconds.
            Default value None

        mono : bool
            Monophonic target, multi-channel audio will be down-mixed.
            Default value False

        silent : bool
            Switch to show progress bar.
            Default value True

        Raises
        ------
        IOError:
            Youtube video does not exists or cannot be downloaded

        Returns
        -------
        self

        """

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        def progress_hook(t):
            """Wraps tqdm instance. Don't forget to close() or __exit__()
            the tqdm instance once you're done with it (easiest using `with` syntax).
            """

            def inner(total, recvd, ratio, rate, eta):
                t.total = int(total / 1024.0)
                t.update(int(recvd / 1024.0))

            return inner

        try:
            import pafy

        except ImportError:
            message = '{name}: Unable to import pafy module. You can install it with `pip install pafy`.'.format(
                name=self.__class__.__name__
            )

            self.logger().exception(message)
            raise ImportError(message)

        try:
            from youtube_dl.utils import ExtractorError

        except ImportError:
            message = '{name}: Unable to import youtube_dl module. You can install it with `pip install youtube-dl`.'.format(
                name=self.__class__.__name__
            )

            self.logger().exception(message)
            raise ImportError(message)

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
            
            # Get temporary filename
            tmp_filename = tmp_file.name
            
            # Remove temporary file (avoid FileExistsError on Windows)
            tmp_file.close()

            download_progress_bar = None

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
                filepath=tmp_filename,
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
                filename=tmp_filename,
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
            How much headroom there should be left under 1.0.
            Default value 0.005

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
            Scale the resampled signal to have approximately equal total energy (see `librosa.core.resample`).
            Default value True

        res_type : str
            Resample type (see `librosa.core.resample`)
            Default value 'kaiser_best'

        Returns
        -------
        self

        """

        if target_fs != self.fs:
            self._data = numpy.asfortranarray(self._data)
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
                  channel=None):
        """Set focus segment

        Parameters
        ----------
        start : int
            Sample index of focus segment start.
            Default value None

        stop : int
            Sample index of focus segment stop.
            Default value None

        duration : int
            Sample count of focus segment.
            Default value None

        start_seconds : float
            Time stamp (in seconds) of focus segment start.
            Default value None

        stop_seconds : float
            Time stamp (in seconds) of focus segment stop.
            Default value None

        duration_seconds : float
            Duration (in seconds) of focus segment.
            Default value None

        channel : int or str
            Audio channel id or name to focus. In case of stereo signal, valid channel labels to select
            single channel are 'L', 'R', 'left', and 'right' or 0, 1, and to get mixed down
            version of all channels 'mixdown'.
            Default value None

        Returns
        -------
        self

        """

        if start is not None or stop is not None or duration is not None:
            # Sample based setting
            if start is not None and stop is not None:
                self.reset_focus()
                self.focus_start_samples = start
                self.focus_stop_samples = stop

            elif start is not None and duration is not None:
                self.reset_focus()
                self.focus_start_samples = start
                self.focus_stop_samples = start + duration

        elif start_seconds is not None or stop_seconds is not None or duration_seconds is not None:
            # Time based setting
            if start_seconds is not None and stop_seconds is not None:
                self.reset_focus()
                self.focus_start_samples = self._time_to_sample(time=start_seconds)
                self.focus_stop_samples = self._time_to_sample(time=stop_seconds)

            elif start_seconds is not None and duration_seconds is not None:
                self.reset_focus()
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

        elif self.focus_channel == 'mixdown' and self.channels > 1:
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

    def frames(self,
               frame_length=None, hop_length=None,
               frame_length_seconds=None, hop_length_seconds=None):
        """Slice audio into overlapping frames.

        Parameters
        ----------
        frame_length : int, optional
            Frame length in samples. Set either frame_length or frame_length_seconds.
            Default value None

        hop_length : int, optional
            Frame hop length in samples. Set either hop_length or hop_length_seconds.
            Default value None

        frame_length_seconds : float, optional
            Frame length in seconds, converted into samples based on sampling rate.
            Default value None

        hop_length_seconds: float, optional
            Frame hop length in seconds, converted into samples based on sampling rate.
            Default value None

        Raises
        ------
        ValueError:
            No frame_length and no frame_length_seconds given.
            No hop_length and no hop_length_seconds given.

        Returns
        -------
        numpy.ndarray

        """

        if not frame_length and frame_length_seconds:
            frame_length = int(self.fs * frame_length_seconds)

        if not hop_length and hop_length_seconds:
            hop_length = int(self.fs * hop_length_seconds)

        if not frame_length:
            message = '{name}: Specify frame_length parameter for frame splitting.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if not hop_length:
            message = '{name}: Specify hop_length parameter for frame splitting.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if self.channels == 1:
            return librosa.util.frame(
                x=self.get_focused(),
                frame_length=frame_length,
                hop_length=hop_length
            )

        else:
            data = []
            for channel_id, channel_data in enumerate(self.get_focused()):
                data.append(
                    librosa.util.frame(
                        x=channel_data,
                        frame_length=frame_length,
                        hop_length=hop_length
                    )
                )

            return numpy.array(data)

    def segments(self,
                 segment_length=None, segment_length_seconds=None,
                 segments=None,
                 active_segments=None,
                 skip_segments=None):
        """Slice audio into segments.

        Parameters
        ----------
        segment_length : int, optional
            Segment length in samples. Set either segment_length or segment_length_seconds. Used to produce
            consecutive non-overlapping segments.
            Default value None

        segment_length_seconds : float, optional
            Segment length in seconds, converted into samples based on sampling rate. Used to produce consecutive
            non-overlapping segments.
            Set either segment_length or segment_length_seconds.
            Default value None

        segments : list of dict or MetaDataContainer, optional
            List of time segments (onset and offset). If none given, segment length is used to produce consecutive
            non-overlapping segments.
            Default value None

        active_segments : list of dict or MetaDataContainer, optional
            List of time segments (onset and offset) to be used when creating segments.
            Only used when segment_length or segment_length_seconds are given and segments are generated
            within this method.
            Default value None

        skip_segments : list of dict or MetaDataContainer, optional
            List of time segments (onset and offset) to be skipped when creating segments.
            Only used when segment_length or segment_length_seconds are given and segments are generated
            within this method.
            Default value None

        Raises
        ------
        ValueError:
            No segments and no segment_length given.

        Returns
        -------
        list, MetaDataContainer

        """
        from dcase_util.containers import MetaDataContainer

        if not segment_length and segment_length_seconds:
            # Get segment_length from segment_length_seconds
            segment_length = int(self.fs * segment_length_seconds)

        if segments is None and segment_length is not None:
            if skip_segments is not None:
                # Make sure skip segments is MetaDataContainer
                skip_segments = MetaDataContainer(skip_segments)

            if active_segments is not None:
                # Make sure active segments is MetaDataContainer
                active_segments = MetaDataContainer(active_segments)

                segments = MetaDataContainer()
                for active_seg in active_segments:
                    segment_start = int(self.fs * active_seg.onset)

                    while segment_start + segment_length < int(self.fs * active_seg.offset):
                        # Segment stop
                        segment_stop = segment_start + segment_length
                        if skip_segments is not None:
                            # Go through skip segments and adjust segment start and stop to avoid segments
                            for item in skip_segments:
                                if item.active_within_segment(
                                        start=segment_start / float(self.fs),
                                        stop=segment_stop / float(self.fs)
                                ):
                                    # Adjust segment start to avoid current skip segment
                                    segment_start = int(self.fs * item.offset)
                                    # Adjust segment stop accordingly
                                    segment_stop = segment_start + segment_length

                        if segment_stop < self.length:
                            # Valid segment found, store it
                            segments.append(
                                {
                                    'onset': segment_start / float(self.fs),
                                    'offset': segment_stop / float(self.fs),
                                }
                            )

                        # Set next segment start
                        segment_start = segment_stop

                        # Stop loop if segment_start is out of signal
                        if segment_start > self.length:
                            break

            else:
                # No segments given, get segments based on segment_length
                segment_start = 0
                segments = MetaDataContainer()
                while True:
                    # Segment stop
                    segment_stop = segment_start + segment_length
                    if skip_segments is not None:
                        # Go through skip segments and adjust segment start and stop to avoid segments
                        for item in skip_segments:
                            if item.active_within_segment(
                                start=segment_start/float(self.fs),
                                stop=segment_stop/float(self.fs)
                            ):
                                # Adjust segment start to avoid current skip segment
                                segment_start = int(self.fs * item.offset)
                                # Adjust segment stop accordingly
                                segment_stop = segment_start + segment_length

                    if segment_stop < self.length:
                        # Valid segment found, store it
                        segments.append(
                            {
                                'onset': segment_start/float(self.fs),
                                'offset': segment_stop/float(self.fs),
                            }
                        )

                    # Set next segment start
                    segment_start = segment_stop

                    # Stop loop if segment_start is out of signal
                    if segment_start > self.length:
                        break

        elif segments is not None:
            # Make sure segments is MetadataContainer
            segments = MetaDataContainer(segments)

        else:
            message = '{name}: Specify segments parameter or segment_length for segment creation.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        # Get audio segments
        data = []
        for segment in segments:
            segment_start_samples = int(self.fs * segment.onset)
            segment_stop_samples = int(self.fs * segment.offset)
            if self.channels > 1:
                data.append(
                    self._data[:, segment_start_samples:segment_stop_samples]
                )

            else:
                data.append(
                    self._data[segment_start_samples:segment_stop_samples]
                )

        return data, segments

    def pad(self, type='silence', length=None, length_seconds=None):
        """Generate signal

        Parameters
        ----------
        type : str
            Default value 'silence'

        length : int, optional
            Default value None

        length_seconds : float, optional
            Default value None

        Returns
        -------
        list, MetaDataContainer

        """

        if not length and length_seconds is not None:
            # Get length from length_seconds
            length = int(self.fs * length_seconds)

        if self.length < length:
            if type == 'silence':
                if len(self.data.shape) == 1:
                    self._data = numpy.pad(
                        array=self._data,
                        pad_width=(0, length-self.length),
                        mode='constant'
                    )

                else:
                    self._data = numpy.pad(
                        array=self._data,
                        pad_width=((0, 0), (0, length-self.length)),
                        mode='constant'
                    )

        return self

    def plot(self, plot_type='wave', **kwargs):
        """Visualize audio data

        Parameters
        ----------

        plot_type : str
            Visualization type, 'wave' for waveform plot, 'spec' for spectrogram, 'dual' for showing both at the same time.
            Default value 'wave'

        Returns
        -------
        self

        """

        if plot_type == 'wave':
            self.plot_wave(**kwargs)

        elif plot_type == 'spec':
            self.plot_spec(**kwargs)

        elif plot_type == 'dual':
            if self.channels == 1:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.subplot(2, 1, 1)
                self.plot_wave(
                    x_axis=kwargs.get('x_axis', 'time'),
                    max_points=kwargs.get('max_points', 50000.0),
                    max_sr=kwargs.get('max_sr', 1000),
                    offset=kwargs.get('offset', 0.0),
                    color=kwargs.get('color', '#333333'),
                    alpha=kwargs.get('alpha', 1.0),
                    show_filename=kwargs.get('show_filename', True),
                    show_xaxis=False,
                    plot=False,
                    figsize=kwargs.get('figsize', None),
                    channel_labels=kwargs.get('channel_labels', None)
                )

                plt.subplot(2, 1, 2)
                self.plot_spec(
                    spec_type=kwargs.get('spec_type', 'log'),
                    hop_length=kwargs.get('hop_length', 512),
                    cmap=kwargs.get('cmap', 'magma'),
                    show_filename=False,
                    show_xaxis=kwargs.get('show_xaxis', True),
                    show_colorbar=False,
                    plot=False,
                    figsize=kwargs.get('figsize', None),
                    channel_labels=kwargs.get('channel_labels', None)
                )

                plt.show()

            else:
                # TODO dual plotting for multichannel audio.
                message = '{name}: Dual plotting of multi-channel audio is not yet implemented.'.format(
                    name=self.__class__.__name__
                )
                self.logger.exception(message)
                raise NotImplementedError(message)

    def plot_wave(self, x_axis='time', max_points=50000.0, max_sr=1000, offset=0.0, color='#333333', alpha=1.0,
                  show_filename=True, show_xaxis=True, plot=True, figsize=None, channel_labels=None):
        """Visualize audio data as waveform.

        Parameters
        ----------

        x_axis : str
            X-axis type.
            Default value 'time'

        max_points : float
            Maximum number of time-points to plot (see `librosa.display.waveplot`).
            Default value 50000

        max_sr : number
            Maximum sampling rate for the visualization
            Default value 1000

        offset : float
            Horizontal offset (in time) to start the waveform plot (see `librosa.display.waveplot`).
            Default value 0.0

        color : str or list of str
            Waveform fill color in hex-code. Per channel colors can be given as list of str.
            Default value '#333333'

        alpha : float
            Alpha of the waveform fill color.
            Default value 1.0

        show_filename : bool
            Show filename as figure title.
            Default value True

        show_xaxis : bool
            Show X-axis.
            Default value True

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same figure
            outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        channel_labels : list
            Channel names
            Default value None

        Returns
        -------
        self

        """

        if channel_labels is None:
            channel_labels = self.channel_labels

        if figsize is None:
            figsize = (10, 5)

        import matplotlib.pyplot as plt
        from librosa.display import waveplot
        if plot:
            plt.figure(figsize=figsize)

        title = Path(self.filename).shorten()

        if self.channels > 1 and len(self.get_focused().shape) > 1:
            # Plotting for multi-channel audio
            for channel_id, channel_data in enumerate(self.get_focused()):
                ax = plt.subplot(self.channels, 1, channel_id + 1)
                if channel_id + 1 != self.channels:
                    current_x_axis = None

                else:
                    current_x_axis = x_axis

                if isinstance(color, list) and channel_id < len(color):
                    current_color = color[channel_id]
                else:
                    current_color = color

                waveplot(
                    y=channel_data.ravel(),
                    sr=self.fs,
                    x_axis=current_x_axis,
                    max_points=max_points,
                    max_sr=max_sr,
                    offset=offset,
                    color=current_color,
                    alpha=alpha
                )

                if isinstance(channel_labels, list) and channel_id < len(channel_labels):
                    plt.ylabel('{channel_label} / Ch{channel:d}'.format(
                        channel_label=channel_labels[channel_id],
                        channel=channel_id)
                    )

                else:
                    plt.ylabel('Channel {channel:d}'.format(channel=channel_id))

                if channel_id == 0 and show_filename:
                    if self.filename:
                        plt.title(title)

                if channel_id+1 != self.channels or not show_xaxis:
                    ax.axes.get_xaxis().set_visible(False)

        else:
            # Plotting for single channel audio
            if isinstance(color, list) and len(color):
                current_color = color[0]
            else:
                current_color = color

            ax = waveplot(
                y=self.get_focused().ravel(),
                sr=self.fs,
                x_axis=x_axis,
                max_points=max_points,
                max_sr=max_sr,
                offset=offset,
                color=current_color,
                alpha=alpha
            )

            if isinstance(channel_labels, list) and len(channel_labels):
                plt.ylabel('{channel_label}'.format(channel_label=channel_labels[0]))

            else:
                plt.ylabel('Channel {channel:d}'.format(channel=0))

            if self.filename and show_filename:
                plt.title(title)

            if not show_xaxis:
                ax.axes.get_xaxis().set_visible(False)

        if plot:
            plt.show()

    def plot_spec(self, spec_type='log', hop_length=512, cmap='magma',
                  show_filename=True, show_xaxis=True, show_colorbar=False, plot=True, figsize=None, channel_labels=None):
        """Visualize audio data as spectrogram.

        Parameters
        ----------

        spec_type : str
            Spectrogram type, use 'linear', 'log', 'cqt', 'cqt_hz', and 'cqt_note'.
            Default value 'log'

        hop_length : float
            Hop length, also used to determine time scale in x-axis (see `librosa.display.specshow`).
            Default value 512

        cmap : float
            Color map (see `librosa.display.specshow`).
            Default value 'magma'

        show_filename : bool
            Show filename as figure title.
            Default value True

        show_xaxis : bool
            Show X-axis.
            Default value True

        show_colorbar : bool
            Show color bar next to plot.
            Default value False

        plot : bool
            If true, figure is shown automatically. Set to False if collecting multiple plots into same
            figure outside this method.
            Default value True

        figsize : tuple
            Size of the figure. If None given, default size (10,5) is used.
            Default value None

        channel_labels : list
            Channel names
            Default value None

        Returns
        -------
        self

        """

        if channel_labels is None:
            channel_labels = self.channel_labels

        if figsize is None:
            figsize = (10, 5)

        from librosa.display import specshow
        import matplotlib.pyplot as plt

        if plot:
            plt.figure(figsize=figsize)

        title = Path(self.filename).shorten()

        if self.channels > 1:
            for channel_id, channel_data in enumerate(self.get_focused()):
                ax = plt.subplot(self.channels, 1, channel_id+1)

                if spec_type in ['linear', 'log']:
                    D = librosa.core.amplitude_to_db(numpy.abs(librosa.stft(channel_data.ravel())) ** 2, ref=numpy.max)

                elif spec_type.startswith('cqt'):
                    D = librosa.core.amplitude_to_db(librosa.cqt(channel_data.ravel(), sr=self.fs), ref=numpy.max)

                else:
                    message = '{name}: Unknown spec_type given for plot_spec'.format(
                        name=self.__class__.__name__
                    )

                    self.logger.exception(message)
                    raise ValueError(message)

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

                if show_colorbar:
                    plt.colorbar(format='%+2.0f dB')

                if isinstance(channel_labels, list) and channel_id < len(channel_labels):
                    plt.ylabel('{channel_label} / Ch{channel:d}'.format(
                        channel_label=channel_labels[channel_id],
                        channel=channel_id)
                    )

                else:
                    plt.ylabel('Channel {channel:d}'.format(channel=channel_id))

                if channel_id == 0 and self.filename:
                    plt.title(title)

                if channel_id+1 != self.channels or not show_xaxis:
                    ax.axes.get_xaxis().set_visible(False)

        else:
            channel_id = 0

            if spec_type in ['linear', 'log']:
                D = librosa.core.amplitude_to_db(
                    numpy.abs(librosa.stft(self.get_focused().ravel())) ** 2,
                    ref=numpy.max
                )

            elif spec_type.startswith('cqt'):
                D = librosa.core.amplitude_to_db(
                    librosa.cqt(self.get_focused().ravel(), sr=self.fs),
                    ref=numpy.max
                )

            else:
                message = '{name}: Unknown spec_type given'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise ValueError(message)

            if spec_type == 'linear':
                ax = specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='linear',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'log':
                ax = specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='log',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'cqt_hz' or 'cqt':
                ax = specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='cqt_hz',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            elif spec_type == 'cqt_note':
                ax = specshow(
                    data=D,
                    sr=self.fs,
                    y_axis='cqt_note',
                    x_axis='time',
                    hop_length=hop_length,
                    cmap=cmap
                )

            if show_colorbar:
                plt.colorbar(format='%+2.0f dB')

            if isinstance(channel_labels, list) and len(channel_labels):
                plt.ylabel('{channel_label}'.format(
                    channel_label=channel_labels[0])
                )

            else:
                plt.ylabel('Channel {channel:d}'.format(channel=0))

            if not show_xaxis:
                ax.axes.get_xaxis().set_visible(False)

            if show_filename and channel_id == 0:
                plt.title(title)

        if plot:
            plt.show()

    def _time_to_sample(self, time):
        """Time to sample index.

        Parameters
        ----------
        time : float
            Time stamp in seconds.

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
            Sample index.

        Returns
        -------
        float

        """

        return sample / float(self.fs)

