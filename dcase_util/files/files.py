#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os
import csv
import time

from dcase_util.containers import FileMixin, ObjectContainer
from dcase_util.utils import FileFormat
from dcase_util.ui import FancyStringifier


class File(FileMixin):
    """Generic file class"""
    valid_formats = [FileFormat.YAML, FileFormat.JSON, FileFormat.CPICKLE, FileFormat.MARSHAL, FileFormat.MSGPACK,
                     FileFormat.TXT, FileFormat.CSV]

    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path

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
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)        # Delete the file, since most likely it was not saved fully
            raise

        return self


class FileLock(ObjectContainer):
    """Simple file-based locking class.

    Usual solution for file locking is to use `fcntl` module. This class provides a bit more flexible solution
    as it does not require file to be open to get a lock. This locking system should also work also
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

    def __str__(self):
        ui = FancyStringifier()

        output = super(FileLock, self).__str__()

        output += ui.data(field='main_filename', value=self.main_filename) + '\n'
        output += ui.data(field='lock_filename', value=self.lock_filename) + '\n'
        output += ui.data(field='timeout', value=self.timeout, unit='sec') + '\n'

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
