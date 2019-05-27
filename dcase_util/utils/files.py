#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems

import os
import argparse
import itertools
import platform
import logging


def argument_file_exists(filename):
    """Argument file checker

    Type for argparse. Checks that file exists but does not open.

    Parameters
    ----------
    filename : str

    Returns
    -------
    str
        filename
    """

    if not os.path.exists(filename):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(filename))
    return filename


def filelist_exists(filelist):
    """Check that all file in the list exists

    Parameters
    ----------
    filelist : dict of paths
        Dict containing paths to files. Two level of dict inspected.

    Returns
    -------
    bool
        Returns True if all files exists, False if any of them does not
    """

    file_exist = []
    for item_key, item_value in iteritems(filelist):
        if isinstance(item_value, dict):
            for sub_item_key, sub_item_value in iteritems(item_value):
                if isinstance(sub_item_value, str):
                    file_exist.append(os.path.isfile(sub_item_value))

        elif isinstance(item_value, str):
            file_exist.append(os.path.isfile(item_value))

    return all(file_exist)


def posix_path(path):
    """Converts path to POSIX format

    Parameters
    ----------
    path : str
        Path

    Returns
    -------
    str

    """

    return os.path.normpath(path).replace('\\', '/')


class Path(object):
    """Utility class for paths"""
    def __init__(self, path=None):
        """Constructor

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        """

        self.path = path
        self.path = self.posix()

    @property
    def logger(self):
        """Logger instance"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            from dcase_util.utils import setup_logging
            setup_logging()

        return logger

    def posix(self, path=None):
        """Converts path to POSIX format

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        str

        """

        if path is None:
            path = self.path

        if path is not None:
            return os.path.normpath(path).replace('\\', '/')

        else:
            return None

    def posix_to_nt(self, path=None):
        """Converts posix formatted path to nt

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        str

        """

        if path is None:
            path = self.path

        return path.replace('/', os.path.sep)

    def shorten(self, path=None, part_count=3):
        """Shorten path into given parts length

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        part_count : int
            Count of path parts
            Default value 3

        Returns
        -------
        str

        """

        if path is None:
            path = self.path

        if path is not None:
            parts = path.split(os.sep)
            if len(parts) > part_count:
                return '.....' + os.path.join(*parts[-part_count:])
            else:
                return path

        else:
            return path

    def file_list(self, path=None, recursive=True, extensions=None,
                  case_sensitive=False, absolute_paths=False, offset=0, limit=None):

        """Get file list

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        recursive : bool
            Do recursive search to sub-directories
            Default value True

        extensions : str or list
            List valid file extensions or comma-separated string.
            Default value None

        case_sensitive : bool
            Use case sensitive file extension matching.
            Default value False

        absolute_paths : bool
            Return absolute paths instead of relative ones.
            Default value False

        offset : int
            Offset of files to be included.
            Default value 0

        limit : int
            Amount of files to be included.
            Default value None

        Returns
        -------
        list

        """

        def process_file(path, filename, extensions, absolute_paths=False):
            current_path = None
            filename_base, file_extension = os.path.splitext(filename)
            if extensions is None or file_extension[1:] in extensions:
                current_path = os.path.join(path, filename)

                if absolute_paths:
                    current_path = os.path.abspath(current_path)

            return current_path

        if path is None:
            path = self.path

        if extensions is not None and isinstance(extensions, str):
            extensions = extensions.split(',')

        if extensions is not None and not case_sensitive:
            for ext in extensions:
                if ext.lower() not in extensions:
                    extensions.append(ext.lower())
                if ext.upper() not in extensions:
                    extensions.append(ext.upper())

        files = []
        if recursive:
            for dir_path, dir_names, filenames in os.walk(path):
                for f in filenames:
                    current_path = process_file(
                        path=dir_path,
                        filename=f,
                        extensions=extensions,
                        absolute_paths=absolute_paths
                    )
                    if current_path:
                        files.append(current_path)
        else:
            for f in os.listdir(path):
                current_path = process_file(
                    path=path,
                    filename=f,
                    extensions=extensions,
                    absolute_paths=absolute_paths
                )
                if current_path:
                    files.append(current_path)

        files.sort()

        if offset and 0 <= offset < len(files):
            files = files[offset:]

        if limit is not None and 0 <= limit < len(files):
            files = files[:limit]

        return files

    def exists(self, path=None):
        """Checks that path exists

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        bool

        """

        if path is None:
            path = self.path

        return os.path.isdir(path)

    def file_count(self, path=None):
        """File count under given path including sub directories.

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        int

        """

        if path is None:
            path = self.path

        total_files = 0
        for root, dirs, files in os.walk(path):
            total_files += len(files)

        return total_files

    def size_bytes(self, path=None):
        """Total byte count of all files under given path.

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        int

        """

        if path is None:
            path = self.path

        total_size = 0
        for f in self.file_list(path=path):
            total_size += os.path.getsize(f)

        return total_size

    def size_string(self, path=None, show_bytes=False):
        """Total data size of all files under given path returned in human readable form.

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        show_bytes : bool
            Show exact byte count
            Default value False

        Returns
        -------
        str

        """

        if path is None:
            path = self.path
        return get_byte_string(self.size_bytes(path=path), show_bytes=show_bytes)

    def makedirs(self, path=None):
        """Create given path.

        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None

        Returns
        -------
        nothing

        """

        if path is None:
            path = self.path

        if isinstance(path, str) and not os.path.isdir(path):
            try:
                os.makedirs(path)
            except OSError as exception:
                pass

    def create(self, paths=None):
        """Create given paths.

        Parameters
        ----------
        paths : str, dict or list or str
            Paths. If None given, path given to initializer is used instead.
            Default value None

        Returns
        -------
        nothing

        """

        if paths is None:
            paths = self.path

        if isinstance(paths, str):
            self.makedirs(paths)

        elif isinstance(paths, dict):
            for key, value in iteritems(paths):
                self.makedirs(value)

        elif isinstance(paths, list):
            for value in paths:
                self.makedirs(value)

        else:
            message = '{name}: Unknown data type for paths.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

    def modify(self, path=None, path_base=None, filename_extension=None, filename_prefix=None, filename_postfix=None):
        """Modify path
        Parameters
        ----------
        path : str
            Path, if none given one given to class constructor is used.
            Default value None
        path_base : str
            Replacement path base, e.g. path base for "/test/audio/audio.wav" is "/test/audio".
            Default value None

        filename_extension : str
            Replacement file extension
            Default value None

        filename_prefix : str
            Prefix to be added to the filename body
            Default value None

        filename_postfix : str
            Postfix to be added to the filename body
            Default value None

        Returns
        -------
        str

        """

        if path is None:
            path = self.path

        current_path_base, current_last_level_path = os.path.split(path)
        current_filename_base, current_extension = os.path.splitext(current_last_level_path)

        if path_base:
            current_path_base = path_base

        if filename_extension:
            current_extension = filename_extension

        if filename_prefix:
            current_filename_base = filename_prefix + current_filename_base

        if filename_postfix:
            current_filename_base = current_filename_base + filename_postfix

        return os.path.join(current_path_base, current_filename_base+current_extension)


class ApplicationPaths(Path):
    """Utility class for application paths, paths are automatically generated based on parameters through parameter hash."""
    def __init__(self, parameter_container=None):
        """Constructor

        Parameters
        ----------
        parameter_container : ParameterContainer
            Application parameter container
            Default value None

        """

        self.parameter_container = parameter_container

    def generate(self, path_base, structure):
        """Generate application paths and include parameter hashes to the paths

        Parameters
        ----------
        path_base : str
            Path base, this is used as base of all paths

        structure : dict
            Dictionary where key is path name, and value is list of parameter paths

        Returns
        -------
        dict

        """

        path_parts = [path_base]
        keys = []
        wild_card_found = False
        for part in structure:
            if '*' in part:
                wild_card_found = True
                path_ = self.parameter_container.get_path(
                    path=part[:part.find('*') - 1]
                )

                if path_:
                    keys = list(path_.keys())

            param_hash = self.parameter_container.get_path(
                path=part + '._hash'
            )

            if param_hash is not None:
                if isinstance(param_hash, list):
                    directory_name = []
                    for h in param_hash:
                        directory_name.append(part.split('.')[0]+'_'+h)
                else:
                    directory_name = self.directory_name(
                        prefix=part.split('.')[0],
                        param_hash=param_hash
                    )

                path_parts.append(directory_name)

        paths = self.construct_path(path_parts)

        if not wild_card_found and len(paths) == 1:
            return paths[0]

        else:
            return dict(zip(keys, paths))

    @staticmethod
    def directory_name(prefix, param_hash):
        """Generate directory name.

        Parameters
        ----------
        prefix : str
            Prefix

        param_hash : str
            Parameter hash

        Returns
        -------
        str

        """

        if platform.system() == 'Windows':
            # Use short directory names and truncated hash for Windows, as it has path length limit (260)
            return param_hash[0:20]

        else:
            return prefix + '_' + param_hash

    def save_parameters_to_path(self, path_base, structure, parameter_filename='parameters.yaml'):
        """Save parameters to each application sub-directory.

        Parameters
        ----------
        path_base : str
            Base path

        structure : dict
            Dictionary where key is path name, and value is list of parameter paths

        parameter_filename : str
            Default value "parameters.yaml"

        Returns
        -------
        nothing

        """

        from dcase_util.containers import ParameterContainer

        path_parts = [path_base]
        for part in structure:
            param_hash = self.parameter_container.get_path(path=part + '._hash')
            if param_hash is not None:
                if isinstance(param_hash, list):
                    directory_name = []
                    for h in param_hash:
                        directory_name.append(part.split('.')[0] + '_' + h)
                else:
                    directory_name = self.directory_name(
                        prefix=part.split('.')[0],
                        param_hash=param_hash
                    )

                parameters = self.parameter_container.get_path(path=part)
                path_parts.append(directory_name)

                current_path = self.construct_path(path_parts)

                if isinstance(current_path, str):
                    ParameterContainer(parameters).save(
                        filename=os.path.join(current_path[0], parameter_filename)
                    )

                else:
                    if isinstance(parameters, dict):
                        ParameterContainer(parameters).save(
                            filename=os.path.join(current_path[0], parameter_filename)
                        )

                    else:
                        for path_id, path in enumerate(current_path):
                            if parameters[path_id]:
                                ParameterContainer(parameters[path_id]).save(
                                    filename=os.path.join(path, parameter_filename)
                                )

    @staticmethod
    def construct_path(path_parts):
        """Generate all combinations of based on path parts

        Parameters
        ----------
        path_parts : list
            Path parts

        Returns
        -------
        list

        """

        if len(path_parts) > 1:
            for i, value in enumerate(path_parts):
                if isinstance(value, str):
                    path_parts[i] = [value]

            if len(path_parts) == 2:
                path_parts = list(itertools.product(path_parts[0], path_parts[1]))

            elif len(path_parts) == 3:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2]))

            elif len(path_parts) == 4:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2], path_parts[3]))

            elif len(path_parts) == 5:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2], path_parts[3],
                                                    path_parts[4]))

            elif len(path_parts) == 6:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2], path_parts[3],
                                                    path_parts[4], path_parts[5]))

            elif len(path_parts) == 7:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2], path_parts[3],
                                                    path_parts[4], path_parts[5], path_parts[6]))

            elif len(path_parts) == 8:
                path_parts = list(itertools.product(path_parts[0], path_parts[1], path_parts[2], path_parts[3],
                                                    path_parts[4], path_parts[5], path_parts[6], path_parts[7]))

            out_path = []
            for l in path_parts:
                out_path.append(os.path.join(*l))

            return out_path

        else:
            return path_parts


class FileFormat(object):
    YAML = 'YAML'  #: YAML file
    CPICKLE = 'CPICKLE'  #: pickled Python object
    NUMPY = 'NPY'  #: Numpy data object
    NUMPYZ = 'NPZ'  #: Numpy zip data object
    XML = 'XML'  #: Extensible Markup Language (XML) file
    JSON = 'JSON'  #: JavaScript Object Notation (JSON) file
    MARSHAL = 'MARSHAL'  #: Marshal Data Migration Model File
    MSGPACK = 'MSGPACK'  #: MessagePack
    TXT = 'TXT'  #: TXT file
    CSV = 'CSV'  #: Comma-separated values (CSV) file
    ANN = 'ANN'  #: Annotation file
    META = 'META' #: Annotation file

    WAV = 'WAV'  #: Audio file, Waveform Audio File Format (WAVE) file
    FLAC = 'FLAC'  #: Audio file, Free Lossless Audio Codec (FLAC) file
    MP3 = 'MP3'  #: Audio file (compressed), MPEG-2 Audio Layer III file
    AAC = 'AAC'  #: Audio file (compressed), Advanced Audio Coding file
    AC3 = 'AC3'  #: Audio file (compressed), Audio Codec 3 file
    M4A = 'M4A'   #: Audio file (compressed), MPEG-4 codec audio file
    AIFF = 'AIFF'  #: Audio file, Audio Interchange File Format file
    AMR = 'AMR'  #: Audio file, Adaptive Multi-Rate audio codec file
    AU = 'AU'  #: Audio file, AU file format
    OGG = 'OGG'  #: Audio file (compressed)
    RA = 'RA'  #: Audio file (compressed), RealAudio files
    VOC = 'VOC'  #: Audio file, Creative voice file
    WMA = 'WMA'  #: Audio file, Windows Media Audio File
    MKA = 'MKA'  #: Audio file, Matroska audio

    FLV = 'FLV'  #: Video file, Flash video
    WEBM = 'WEBM'  #: Video file
    MKV = 'MKV'  #: Video file, Matroska video
    MOV = 'MOV'  #: Video file, Apple QuickTime Movie
    MP4 = 'MP4'  #: Video file, MPEG-4 Video File
    MPG = 'MPG'  #: Video file, MPEG Video File
    AVI = 'AVI'  #: Video file, Audio Video Interleave File
    WMV = 'WMV'  #: Video file, Windows Media Video File

    TAR = 'TAR'  #: Consolidated Unix File Archive
    GZ = 'GZ'  #: Compressed file, Gnu Zipped Archive
    ZIP = 'ZIP'  #: Compressed file, Zipped File
    RAR = 'RAR'  #: Compressed file, WinRAR Compressed Archive

    PDF = 'PDF'  #: Document file, Portable Document Format File

    GIF = 'GIF'  #: Image file, Graphical Interchange Format File
    JPG = 'JPG'  #: Image file, JPEG Image
    PNG = 'PNG'  #: Image file, Portable Network Graphic
    SVG = 'SVG'  #: Image file, Scalable Vector Graphics File

    RAW = 'RAW'  #: Raw binary file

    UNKNOWN = 'UNKNOWN'  #: Unknown format

    @classmethod
    def detect_based_on_filename(cls, filename):
        """Detect file format based on filename.

        Parameters
        ----------
        filename : str
            Path to the file

        Returns
        -------
        str
            File format label

        """

        extension = os.path.splitext(filename.lower())[1]
        if extension == '.yaml':
            return cls.YAML

        elif extension == '.xml':
            return cls.XML

        elif extension == '.json':
            return cls.JSON

        elif extension in ['.cpickle', '.pickle', '.pkl']:
            return cls.CPICKLE

        elif extension == '.npy':
            return cls.NUMPY

        elif extension == '.npz':
            return cls.NUMPYZ

        elif extension == '.marshal':
            return cls.MARSHAL

        elif extension == '.msgpack':
            return cls.MSGPACK

        elif extension in ['.txt', '.hash']:
            return cls.TXT

        elif extension == '.csv':
            return cls.CSV

        elif extension == '.ann':
            return cls.ANN

        elif extension == '.meta':
            return cls.META

        elif extension == '.wav':
            return cls.WAV

        elif extension == '.flac':
            return cls.FLAC

        elif extension == '.mp3':
            return cls.MP3

        elif extension == '.ogg':
            return cls.OGG

        elif extension == '.aac':
            return cls.AAC

        elif extension == '.ac3':
            return cls.AC3

        elif extension == '.aiff':
            return cls.AIFF

        elif extension == '.amr':
            return cls.AMR

        elif extension == '.au':
            return cls.AU

        elif extension == '.ra':
            return cls.RA

        elif extension == '.voc':
            return cls.VOC

        elif extension == '.m4a':
            return cls.M4A

        elif extension == '.wma':
            return cls.WMA

        elif extension == '.wmv':
            return cls.WMV

        elif extension == '.webm':
            return cls.WEBM

        elif extension == '.avi':
            return cls.AVI

        elif extension == '.flv':
            return cls.FLV

        elif extension == '.mka':
            return cls.MKA

        elif extension == '.mkv':
            return cls.MKV

        elif extension == '.mov':
            return cls.MOV

        elif extension == '.mp4':
            return cls.MP4

        elif extension == '.mpg':
            return cls.MPG

        elif extension == '.tar':
            return cls.TAR

        elif extension == '.gz':
            if '.tar' in filename.lower():
                return cls.TAR
            else:
                return cls.GZ

        elif extension == '.zip':
            return cls.ZIP

        elif extension == '.rar':
            return cls.RAR

        elif extension == '.pdf':
            return cls.PDF

        elif extension == '.png':
            return cls.PNG

        elif extension == '.jpg':
            return cls.JPG

        elif extension == '.gif':
            return cls.GIF

        elif extension == '.svg':
            return cls.SVG

        elif extension == '.raw':
            return cls.RAW

        else:
            return cls.UNKNOWN

    @classmethod
    def detect_based_on_content(cls, filename):
        """Detect file format based on content by using python-magic.

        Parameters
        ----------
        filename : str
            Path to the file

        Returns
        -------
        str
            File format label

        """

        if os.path.isfile(filename):
            try:
                import magic
                file_description = magic.from_file(filename).split(',')

                if file_description[0] == 'FLAC audio bitstream data':
                    return cls.FLAC

                elif file_description[0] == 'RIFF (little-endian) data' and file_description[1].strip() == 'WAVE audio':
                    return cls.WAV

                elif file_description[0] == 'Ogg data':
                    return cls.OGG

                elif file_description[0] == 'MPEG ADTS' and file_description[1].strip() == 'AAC':
                    return cls.AAC

                elif file_description[0] == 'ATSC A/52 aka AC-3 aka Dolby Digital stream':
                    return cls.AC3

                elif file_description[0] == 'IFF data' and file_description[1].strip() == 'AIFF audio':
                    return cls.AIFF

                elif file_description[0] == 'Adaptive Multi-Rate Codec (GSM telephony)':
                    return cls.AMR

                elif file_description[0].startswith('Creative Labs voice data'):
                    return cls.VOC

                elif file_description[0].startswith('Sun/NeXT audio data'):
                    return cls.AU

                elif file_description[0] == 'RealMedia file':
                    return cls.RA

                elif file_description[0] == 'Macromedia Flash Video':
                    return cls.FLV

                elif file_description[0] == 'RIFF (little-endian) data' and file_description[1].strip() == 'AVI':
                    return cls.AVI

                elif file_description[0] == 'EBML file' and file_description[1].strip() == 'creator matroska':
                    return cls.MKA # cls.MKA or cls.MKV

                elif file_description[0] == 'ISO Media' and file_description[1].strip() == 'Apple QuickTime movie':
                    return cls.MOV

                elif file_description[0] == 'ISO Media' and file_description[1].strip() == 'MPEG v4 system':
                    return cls.MP4

                elif file_description[0] == 'WebM':
                    return cls.WEBM

                elif file_description[0] == 'MPEG sequence':
                    return cls.MPG

                elif file_description[0] == 'Microsoft ASF':
                    return cls.WMA # cls.WMA  or cls.WMV

                elif file_description[0] == 'Zip archive data':
                    return cls.ZIP

                elif file_description[0] == 'PDF document':
                    return cls.PDF

                elif file_description[0] == 'SVG Scalable Vector Graphics image':
                    return cls.SVG

                elif file_description[0] == 'GIF image data':
                    return cls.GIF

                elif file_description[0] == 'JPEG image data':
                    return cls.JPG

                elif file_description[0] == 'PNG image data':
                    return cls.PNG

                elif file_description[0].startswith('Audio file with ID3') and file_description[1] == ' layer III':
                    return cls.MP3

                elif file_description[0] == 'RAR archive data':
                    return cls.RAR

                elif file_description[0] == 'POSIX tar archive':
                    return cls.TAR

                elif file_description[0] == 'gzip compressed data':
                    f = magic.Magic(uncompress=True)
                    file_description = f.from_file(filename).split(',')

                    if file_description[0].startswith('POSIX tar archive (GNU)'):
                        return cls.TAR

                    else:
                        return cls.GZ

                elif file_description[0] == '8086 relocatable (Microsoft)':
                    import cPickle as pickle
                    try:
                        pickle.load(open(filename, "rb"))
                        return cls.CPICKLE

                    except:
                        pass

                elif file_description[0] == 'ASCII text':
                    with open(filename, "r") as in_fh:
                        # Read the file into memory for parsing
                        data = in_fh.read()

                    import json
                    try:
                        json.loads(data)
                        return cls.JSON

                    except ValueError:
                        pass

                    import xml.etree.ElementTree
                    try:
                        xml.etree.ElementTree.parse(filename).getroot()
                        return cls.XML

                    except xml.etree.ElementTree.ParseError:
                        pass

                    import yaml
                    try:
                        yaml.safe_load(data)
                        return cls.YAML

                    except (TypeError, yaml.scanner.ScannerError, yaml.constructor.ConstructorError):
                        pass

                    import csv
                    try:
                        with open(filename, 'rb') as f:
                            csv_reader = csv.reader(f)
                        return cls.CSV

                    except ValueError:
                        pass

                return None

            except ImportError:
                return None

        else:
            return None

    @classmethod
    def detect(cls, filename, use_content_for_unknown=True):
        """Detect file format. First the file extension is used, if the format is not recognized based on filename alone then content is checked given that file exists.

        Parameters
        ----------
        filename : str
            Path to the file

        use_content_for_unknown : bool
            Use file content to detect the file format if file exists.
            Default value True

        Returns
        -------
        str
            File format label

        """

        # Detect first from the filename
        result1 = cls.detect_based_on_filename(filename=filename)

        # If format is unknown still, try recover it from the content header
        if use_content_for_unknown:
            if result1 == cls.UNKNOWN:
                result2 = cls.detect_based_on_content(filename=filename)
                if result2 is not None:
                    return result2

        return result1

    @classmethod
    def validate_label(cls, label):
        """Validate file format label against labels known by this class

        Parameters
        ----------
        label : str
            file format label

        Returns
        -------
        bool

        """

        return label in list(cls.__dict__.keys())
