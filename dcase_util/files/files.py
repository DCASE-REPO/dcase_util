#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os
import csv
import time
import zipfile
import tarfile

from dcase_util.containers import FileMixin, ObjectContainer, PackageMixin
from dcase_util.utils import get_byte_string, FileFormat
from dcase_util.ui import FancyStringifier


class File(FileMixin):
    """Generic file class"""
    valid_formats = [FileFormat.YAML, FileFormat.JSON, FileFormat.CPICKLE, FileFormat.MARSHAL, FileFormat.MSGPACK,
                     FileFormat.TXT, FileFormat.CSV, FileFormat.ZIP, FileFormat.TAR]

    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path

        valid_formats : list of FileFormat items
            List of valid formats (FileFormat)
            Default [YAML,JSON,CPICKLE,MARSHAL,MSGPACK,TXT,CSV,ZIP,TAR]

        """

        # Run FileMixin init
        FileMixin.__init__(self, *args, **kwargs)

        # Run super init to call init of mixins too
        super(File, self).__init__(*args, **kwargs)

    def load(self, filename=None):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path
            Default value filename given to class constructor

        Raises
        ------
        ImportError:
            Error if file format specific module cannot be imported

        IOError:
            File does not exists or has unknown file format

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename
            self.detect_file_format()
            self.validate_format()

        if self.exists():
            from dcase_util.files import Serializer

            # File exits
            if self.format == FileFormat.YAML:
                return Serializer.load_yaml(filename=self.filename)

            elif self.format == FileFormat.CPICKLE:
                return Serializer.load_cpickle(filename=self.filename)

            elif self.format == FileFormat.MARSHAL:
                return Serializer.load_marshal(filename=self.filename)

            elif self.format == FileFormat.MSGPACK:
                return Serializer.load_msgpack(filename=self.filename)

            elif self.format == FileFormat.JSON:
                return Serializer.load_json(filename=self.filename)

            elif self.format == FileFormat.TXT:
                with open(self.filename, 'r') as f:
                    lines = f.readlines()
                    return dict(zip(range(0, len(lines)), lines))

            elif self.format == FileFormat.CSV:
                data = {}
                delimiter = self.delimiter()
                with open(self.filename, 'rb') as f:
                    csv_reader = csv.reader(f, delimiter=delimiter)
                    for row in csv_reader:
                        if len(row) == 2:
                            data[row[0]] = row[1]
                return data

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File does not exists [{file}]'.format(name=self.__class__.__name__, file=self.filename)
            self.logger.exception(message)
            raise IOError(message)

    def save(self, data, filename=None):
        """Save file

        Parameters
        ----------
        data
            Data to be saved

        filename : str, optional
            File path
            Default value filename given to class constructor

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

        try:
            from dcase_util.files import Serializer

            if self.format == FileFormat.YAML:
                Serializer.save_yaml(filename=self.filename, data=data)

            elif self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=data)

            elif self.format == FileFormat.MARSHAL:
                Serializer.save_marshal(filename=self.filename, data=data)

            elif self.format == FileFormat.MSGPACK:
                Serializer.save_msgpack(filename=self.filename, data=data)

            elif self.format == FileFormat.JSON:
                Serializer.save_json(filename=self.filename, data=data)

            elif self.format == FileFormat.TXT:
                with open(self.filename, "w") as text_file:
                    for line_id in data:
                        text_file.write(data[line_id])

            else:
                message = '{name}: Unknown format [{format}]'.format(
                    name=self.__class__.__name__,
                    format=self.filename
                )

                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)        # Delete the file, since most likely it was not saved fully
            raise

        return self


class FileLock(ObjectContainer):
    """Simple file-based locking class.

    Usual solution for file locking is to use `fcntl` module. This class provides a bit more flexible solution
    as it does not require file to be open to get a lock. This locking system should also work
    with NFS mounts (also prior v3).

    """

    def __init__(self, filename, timeout=60*1, lock_file_extension='lock', **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str
            File path

        timeout : int
            Timeout in seconds

        lock_file_extension : str
            File extension to be used for locking files

        """

        # Run super init to call init of mixins too
        super(FileLock, self).__init__(**kwargs)

        self.timeout = timeout
        self.main_filename = filename
        self.lock_filename = filename + '.' + lock_file_extension

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = super(FileLock, self).to_string(ui=ui, indent=indent)

        output += ui.data(field='main_filename', value=self.main_filename, indent=indent) + '\n'
        output += ui.data(field='lock_filename', value=self.lock_filename, indent=indent) + '\n'
        output += ui.data(field='timeout', value=self.timeout, unit='sec', indent=indent) + '\n'

        return output

    @property
    def expired(self):
        """Check is the locking file older than specified timeout.

        Returns
        -------
        bool

        """

        if self.is_locked:
            if time.time() - os.path.getctime(self.lock_filename) > self.timeout:
                return True

            else:
                return False

        else:
            return False

    @property
    def is_locked(self):
        """Check does the locking file exists.

        Returns
        -------
        bool

        """

        if os.path.isfile(self.lock_filename):
            return True

        else:
            return False

    def touch(self):
        """Create locking file with current time stamp.

        Returns
        -------
        self

        """

        with open(self.lock_filename, 'a'):
            os.utime(self.lock_filename, None)

        return self

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def lock(self):
        """Lock file.

        If lock is already set, method will wait until lock is released or timeout has reached.

        Returns
        -------
        self

        """

        while True:
            if not self.is_locked:
                # File is not locked we can proceed to the locking phase.
                break

            else:
                if self.expired:
                    # Lock has been expired, suspected deadlock case, go on and steal the lock.
                    break

            # File is locked by other, wait until lock is released or timeout has expired.
            time.sleep(1)  # pool only once per second

        # Lock
        self.touch()

        return self

    def release(self):
        """Release file lock.

        Returns
        -------
        self

        """

        if self.is_locked:
            try:
                os.remove(self.lock_filename)

            except OSError as exception:
                pass

        return self


class Package(ObjectContainer, PackageMixin):
    """Generic package class"""
    valid_formats = [FileFormat.ZIP, FileFormat.TAR]

    def __init__(self, *args, **kwargs):
        # Run ContainerMixin init
        PackageMixin.__init__(self, *args, **kwargs)

        self._file_info = None
        self._size_compressed = None
        self._size_uncompressed = None

        super(Package, self).__init__(*args, **kwargs)

    def to_string(self, ui=None, indent=0):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indention used
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = ''
        output += ui.class_name(self.__class__.__name__, indent=indent) + '\n'

        if hasattr(self, 'filename') and self.filename:
            output += ui.data(field='filename', value=self.filename, indent=indent) + '\n'

        if self._file_info is None:
            self.get_info()

        output += ui.line('Size', indent=indent) + '\n'

        output += ui.data(
            field='Uncompressed',
            value=get_byte_string(self._size_uncompressed),
            indent=indent + 2
        ) + '\n'

        if self.format == FileFormat.ZIP:
            output += ui.data(
                field='Compressed',
                value=get_byte_string(self._size_compressed),
                indent=indent + 2
            ) + '\n'

            output += ui.data(
                field='Ratio',
                value=self._size_compressed/float(self._size_uncompressed) * 100,
                unit='%',
                indent=indent + 2
            ) + '\n'

        output += ui.line('Files', indent=indent) + '\n'
        output += ui.data(
            field='Count',
            value=len(self._file_info),
            indent=indent + 2
        ) + '\n'

        return output

    def get_info(self):
        """Get package info

        Returns
        -------
        self
        """

        if self.format == FileFormat.ZIP:
            zip = zipfile.ZipFile(
                file=self.filename,
                mode='r'
            )
            self._file_info = zip.infolist()
            zip.close()

            self._size_compressed = 0
            self._size_uncompressed = 0

            # Go through files and accumulate uncompressed and compressed file sizes
            for file_info in self._file_info:
                self._size_compressed += file_info.compress_size
                self._size_uncompressed += file_info.file_size

        elif self.format == FileFormat.TAR:
            tar = tarfile.open(
                name=self.filename,
                mode='r:gz'
            )
            self._file_info = tar.getmembers()
            tar.close()

            self._size_uncompressed = 0
            # Only uncompressed file size is available
            for file_info in self._file_info:
                self._size_uncompressed += file_info.size

            self._size_compressed = None

        return self
