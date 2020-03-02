#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import six

import os
import sys
import locale
import logging
import logging.config
import pkg_resources


def get_class_inheritors(klass):
    """Get all classes inherited from given class

    Parameters
    ----------
    klass : class

    Returns
    -------
    list
        List of classes
    """

    sub_classes = []
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in sub_classes:
                sub_classes.append(child)
                work.append(child)

    return sub_classes


def get_byte_string(num_bytes, show_bytes=True):
    """Output number of bytes according to locale and with IEC binary prefixes

    Parameters
    ----------
    num_bytes : int > 0 [scalar]
        Bytes
    show_bytes : bool, optional
        Show byte count
        Default value "True"

    Returns
    -------
    str
        Human readable byte string

    """

    KB = float(1024)
    MB = float(KB * KB)
    GB = float(KB * MB)
    TB = float(KB * GB)
    PB = float(KB * TB)
    EB = float(KB * PB)
    ZB = float(KB * EB)
    YB = float(KB * ZB)

    locale.setlocale(locale.LC_ALL, '')

    output = ''
    if show_bytes and num_bytes > KB:
        output += locale.format("%d", num_bytes, grouping=True) + ' bytes'
        output += ' ('

    if num_bytes >= YB:
        output += '%.4g YB' % (num_bytes / YB)

    elif num_bytes >= ZB:
        output += '%.4g ZB' % (num_bytes / ZB)

    elif num_bytes >= EB:
        output += '%.4g EB' % (num_bytes / EB)

    elif num_bytes >= PB:
        output += '%.4g PB' % (num_bytes / PB)

    elif num_bytes >= TB:
        output += '%.4g TB' % (num_bytes / TB)

    elif num_bytes >= GB:
        output += '%.4g GB' % (num_bytes / GB)

    elif num_bytes >= MB:
        output += '%.4g MB' % (num_bytes / MB)

    elif num_bytes >= KB:
        output += '%.4g KB' % (num_bytes / KB)
    else:
        output += '%d bytes' % (num_bytes)

    if show_bytes and num_bytes > KB:
        output += ')'

    return output


def check_pkg_resources(package_requirement, logger=None):
    working_set = pkg_resources.WorkingSet()
    if logger is None:
        logger = logging.getLogger(__name__)

    try:
        working_set.require(package_requirement)

    except pkg_resources.VersionConflict:
        message = '{name}: Version conflict, update package [pip install {package_requirement}]'.format(
            name=__name__,
            package_requirement=package_requirement
        )
        logger.exception(message)
        raise

    except pkg_resources.DistributionNotFound:
        message = '{name}: Package not found, install package [pip install {package_requirement}]'.format(
            name=__name__,
            package_requirement=package_requirement
        )
        logger.exception(message)
        raise


def is_int(value):
    """Check if given value is integer

    Parameters
    ----------
    value : variable

    Returns
    -------
    bool

    """

    if value is not None:
        try:
            int(value)
            return True

        except ValueError:
            return False

    else:
        return False


def is_float(value):
    """Check if given value is float

    Parameters
    ----------
    value : variable

    Returns
    -------
    bool

    """

    if value is not None:
        try:
            float(value)
            return True

        except ValueError:
            return False

    else:
        return False


def is_jupyter():
    """Check if code is run in Jupyter (Jupyter notebook, Jupyter console, or ipython qtconsole).

    Returns
    -------
    bool

    """

    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            # Jupyter notebook, Jupyter console, or qtconsole
            return True

        elif shell == 'google.colab._shell':
            # Google Colab
            return True

        elif shell == 'TerminalInteractiveShell':
            # Normal terminal console with IPython
            return False

        else:
            return False

    except NameError:
        # Normal python interpreter
        return False


def get_audio_info(filename, logger=None):
    """Get information about audio file without opening it.

    Parameters
    ----------
    filename : str
        filename

    logger : Logger class
        Logger class
        Default value None

    Returns
    -------
    DictContainer
        Dict with audio file information

    """

    from dcase_util.utils.files import FileFormat
    from dcase_util.files import File
    from dcase_util.containers import DictContainer

    if logger is None:
        logger = logging.getLogger(__name__)

    file = File(
        filename=filename,
        valid_formats=[
            FileFormat.WAV,
            FileFormat.FLAC,
            FileFormat.OGG,
            FileFormat.MP3,
            FileFormat.M4A,
            FileFormat.MP4,
            FileFormat.WEBM
        ]
    )

    if not file.exists():
        # File does not exists
        message = '{name}: File does not exists [{filename}] '.format(
            name=__name__,
            filename=filename
        )
        logger.exception(message)

        raise IOError(message)
    file.detect_file_format()

    if file.format is None:
        # Unknown format
        message = '{name}: File format cannot be detected for file [{filename}] '.format(
            name=__name__,
            filename=filename
        )
        logger.exception(message)

        raise IOError(message)

    info = DictContainer({
        'filename': file.filename,
        'bytes': file.bytes,
        'format': file.format
    })

    if file.format == FileFormat.WAV:
        import soundfile

        wav_info = soundfile.info(file=file.filename)
        info['fs'] = wav_info.samplerate
        info['channels'] = wav_info.channels
        info['duration_sec'] = wav_info.duration
        info['duration_ms'] = (wav_info.frames / float(wav_info.samplerate)) * 1000
        info['duration_samples'] = wav_info.frames
        info['subtype'] = {
            'name': wav_info.subtype,
            'info': wav_info.subtype_info
        }

        # Map sub type to bit depth
        if info['subtype'] == 'PCM_16':
            info['bit_depth'] = 16

        elif info['subtype'] == 'PCM_24':
            info['bit_depth'] = 24

        elif info['subtype'] == 'PCM_32':
            info['bit_depth'] = 32

    elif file.format in [FileFormat.FLAC, FileFormat.OGG,
                         FileFormat.MP3, FileFormat.M4A, FileFormat.MP4,
                         FileFormat.WEBM]:
        # Use ffprobe to get file info from other formats
        import subprocess
        import json
        import shlex

        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = shlex.split(cmd)
        args.append(file.filename)

        # Run command line command, fetch and parse json output
        try:
            output = subprocess.check_output(args).decode('utf-8')

        except OSError:
            # Error while running the command
            message = '{name}: It seems that ffmpeg (ffprobe) is not installed.'.format(
                name=__name__,
                filename=filename
            )
            logger.exception(message)

            raise IOError(message)

        ffmpeg_meta = json.loads(output)

        for stream in ffmpeg_meta['streams']:
            if stream['codec_type'] == 'audio':
                # Fetch audio info from first audio stream
                info['fs'] = int(stream['sample_rate'])

                # Get duration
                if 'duration' not in stream:
                    info['duration_sec'] = None
                elif is_float(stream['duration']):
                    info['duration_sec'] = float(stream['duration'])
                else:
                    info['duration_sec'] = None

                # Get bit rate
                if 'bit_rate' not in stream:
                    info['bit_rate'] = None
                elif is_int(stream['bit_rate']):
                    info['bit_rate'] = int(stream['bit_rate'])
                else:
                    info['bit_rate'] = None

                # Get codec info
                info['codec'] = {}

                if 'codec_name' in stream:
                    info['codec']['name'] = stream['codec_name']

                if 'codec_long_name' in stream:
                    info['codec']['name_long'] = stream['codec_long_name']

                if 'codec_type' in stream:
                    info['codec']['type'] = stream['codec_type']

                break

    return info


class SuppressStdoutAndStderr(object):
    """Context manager to suppress STDOUT and STDERR

    A context manager for doing a deep suppression of stdout and stderr, i.e. will suppress all print,
    even if the print originates in a compiled C/Fortran sub-function.

    After:
    http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions

    """

    def __enter__(self):
        if not is_jupyter():  # Only redirect STDOUT and STDERR in console
            self.stdout_null_file = open(os.devnull, 'w')
            self.stderr_null_file = open(os.devnull, 'w')

            self.stdout_fileno_undup_original = sys.stdout.fileno()
            self.stderr_fileno_undup_original = sys.stderr.fileno()

            self.stdout_fileno_original = os.dup (sys.stdout.fileno())
            self.stderr_fileno_original = os.dup (sys.stderr.fileno())

            self.stdout_original = sys.stdout
            self.stderr_original = sys.stderr

            # Assign stdout and stderr
            os.dup2(self.stdout_null_file.fileno(), self.stdout_fileno_undup_original)
            os.dup2(self.stderr_null_file.fileno(), self.stderr_fileno_undup_original)

            sys.stdout = self.stdout_null_file
            sys.stderr = self.stderr_null_file

        return self

    def __exit__(self, *_):
        if not is_jupyter():
            # Return stdout and stderr
            sys.stdout = self.stdout_original
            sys.stderr = self.stderr_original

            os.dup2(self.stdout_fileno_original, self.stdout_fileno_undup_original)
            os.dup2(self.stderr_fileno_original, self.stderr_fileno_undup_original)

            os.close(self.stdout_fileno_original)
            os.close(self.stderr_fileno_original)

            self.stdout_null_file.close()
            self.stderr_null_file.close()


class VectorRecipeParser(object):
    def __init__(self, delimiters=None, default_stream=0, **kwargs):

        # Define delimiters
        self.delimiters = {
            'block': ';',
            'detail': '=',
            'dimension': ':',
            'segment': '-',
            'vector': ','
        }

        if delimiters:
            self.delimiters.update(delimiters)

        self.default_stream = default_stream

    def parse(self, recipe):
        """Parse feature vector recipe

        Overall format: [block #1];[block #2];[block #3];...

        Block formats:
         - [label (string)]=full vector
         - [label (string)]=[start index (int)]-[end index (int)] => default stream and vector [start:end]
         - [label (string)]=[stream (int or string)]:[start index (int)]-[end index (int)] => specified stream and vector [start:end]
         - [label (string)]=1,2,3,4,5 => vector [1,2,3,4,4]
         - [label (string)]=0 => specified stream and full vector

        Parameters
        ----------
        recipe : str
            Feature recipe

        Returns
        -------
        data : dict
            Feature recipe structure

        """

        if isinstance(recipe, six.string_types):
            data = []
            labels = recipe.split(self.delimiters['block'])
            for label in labels:
                label = label.strip()
                if label:
                    detail_parts = label.split(self.delimiters['detail'])
                    label = detail_parts[0].strip()

                    # Default values, used when only extractor is
                    # defined e.g. [extractor (string)]; [extractor (string)]
                    vector_index_structure = {
                        'stream': self.default_stream,
                        'selection': False,
                        'full': True,
                    }

                    # Inspect recipe further
                    if len(detail_parts) == 2:
                        main_index_parts = detail_parts[1].split(self.delimiters['dimension'])
                        vector_indexing_string = detail_parts[1]

                        if len(main_index_parts) > 1:
                            # Channel has been defined,
                            # e.g. [extractor (string)]=[channel (int)]:[start index (int)]-[end index (int)]
                            vector_index_structure['stream'] = int(main_index_parts[0])
                            vector_indexing_string = main_index_parts[1]

                        vector_indexing = vector_indexing_string.split(self.delimiters['segment'])
                        if len(vector_indexing) > 1:
                            vector_index_structure['start'] = int(vector_indexing[0].strip())
                            vector_index_structure['stop'] = int(vector_indexing[1].strip()) + 1
                            vector_index_structure['full'] = False
                            vector_index_structure['selection'] = False

                        else:
                            vector_indexing = vector_indexing_string.split(self.delimiters['vector'])
                            if len(vector_indexing) > 1:
                                a = list(map(int, vector_indexing))
                                vector_index_structure['full'] = False
                                vector_index_structure['selection'] = True
                                vector_index_structure['vector'] = a

                            else:
                                vector_index_structure['stream'] = int(vector_indexing[0])
                                vector_index_structure['full'] = True
                                vector_index_structure['selection'] = False

                        current_data = {
                            'label': label,
                            'vector-index': vector_index_structure,
                        }

                    else:
                        current_data = {
                            'label': label,
                        }

                    data.append(current_data)

            from dcase_util.containers import ListDictContainer
            return ListDictContainer(data)

        else:
            return recipe
