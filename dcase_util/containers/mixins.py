# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems

import os
import sys
import numpy
import logging
import csv
import zipfile
import tarfile
from tqdm import tqdm
from dcase_util.utils import setup_logging, FileFormat
from dcase_util.ui import FancyLogger


class ContainerMixin(object):
    """Container mixin to give class basic container methods."""
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'ui'):
            self.ui = FancyLogger()

        # Setup progress bar
        if not hasattr(self, 'log_progress'):
            self.log_progress = kwargs.get('log_progress', True)

        if not hasattr(self, 'disable_progress_bar'):
            self.disable_progress_bar = kwargs.get('disable_progress_bar', False)

        if not hasattr(self, 'use_ascii_progress_bar'):
            self.use_ascii_progress_bar = kwargs.get('use_ascii_progress_bar', True)

    def __getstate__(self):
        return {}

    def __setstate__(self, d):
        self.ui = FancyLogger()

    @property
    def logger(self):
        """Logger instance"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def show(self):
        """Print container content

        Returns
        -------
        Nothing

        """
        print(self)

    def log(self, level='info'):
        """Log container content

        Parameters
        ----------
        level : str
            Logging level, possible values [info, debug, warn, warning, error, critical]

        Returns
        -------
        Nothing

        """

        self.ui.line(str(self), level=level)


class FileMixin(object):
    """File mixin to give class methods to load and store content."""
    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'ui'):
            self.ui = FancyLogger()

        if not hasattr(self, 'valid_formats'):
            self.valid_formats = []

        if not hasattr(self, 'filename'):
            if kwargs.get('filename', None):
                # Set variables
                self.filename = kwargs.get('filename', None)
            else:
                self.filename = None

        if not hasattr(self, 'format'):
            self.format = None

        if hasattr(self, 'filename') and self.filename is not None:
            self.detect_file_format()
            self.validate_format()

        # Setup progress bar
        if not hasattr(self, 'log_progress'):
            self.log_progress = kwargs.get('log_progress', True)

        if not hasattr(self, 'disable_progress_bar'):
            self.disable_progress_bar = kwargs.get('disable_progress_bar', False)

        if not hasattr(self, 'use_ascii_progress_bar'):
            self.use_ascii_progress_bar = kwargs.get('use_ascii_progress_bar', True)

    def __getstate__(self):
        return {}

    def __setstate__(self, d):
        self.ui = FancyLogger()

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def get_file_information(self):
        """Get file information, filename

        Returns
        -------
        str

        """

        if self.filename:
            return 'Filename: ['+self.filename+']'
        else:
            return ''

    def detect_file_format(self, filename=None):
        """Detect file format from extension

        Parameters
        ----------
        filename : str
            filename

        Raises
        ------
        IOError:
            Unknown file format

        Returns
        -------
        str
            format tag

        """

        if filename is None:
            filename = self.filename

        file_format = FileFormat.detect(filename=filename)

        if file_format is None:
            # Unknown format
            message = '{name}: File format can be detected for file [{filename}] '.format(
                name=self.__class__.__name__,
                filename=filename
            )
            if self.logger:
                self.logger.exception(message)

            raise IOError(message)

        self.format = file_format
        return self

    def validate_format(self):
        """Validate file format

        Raises
        ------
        IOError:
            Unknown file format

        Returns
        -------
        bool

        """

        if self.valid_formats:
            # Validate only if valid format has been given

            if not hasattr(self, 'format') or not self.format:
                # Detect format if defined yet
                self.detect_file_format()

            if self.format and self.format in self.valid_formats:
                # Format found and valid formats defined, validate format
                return True

            else:
                message = '{name}: Unknown format [{format}] for file [{file}]'.format(
                    name=self.__class__.__name__,
                    format=os.path.splitext(self.filename)[-1],
                    file=self.filename
                )
                if self.logger:
                    self.logger.exception(message)

                raise IOError(message)

        else:
            return True

    def exists(self):
        """Checks that file exists

        Returns
        -------
        bool

        """

        return os.path.isfile(self.filename)

    def empty(self):
        """Check if file is empty

        Returns
        -------
        bool

        """

        if len(self) == 0:
            return True
        else:
            return False

    def delimiter(self, exclude_delimiters=None):
        """Use csv.sniffer to guess delimiter for CSV file

        Returns
        -------
        str
            Delimiter character

        """

        if exclude_delimiters is None:
            exclude_delimiters = []

        sniffer = csv.Sniffer()
        valid_delimiters = ['\t', ',', ';', ' ']

        if exclude_delimiters:
            # Remove excluded delimiters from the list
            valid_delimiters = list(set(valid_delimiters) - set(exclude_delimiters))

        delimiter = '\t'
        with open(self.filename, 'rt') as f1:
            try:
                example_content = f1.read(1024)
                dialect = sniffer.sniff(example_content)
                if hasattr(dialect, '_delimiter'):
                    if dialect._delimiter in valid_delimiters:
                        delimiter = dialect._delimiter
                elif hasattr(dialect, 'delimiter'):
                    if dialect.delimiter in valid_delimiters:
                        delimiter = dialect.delimiter
                else:
                    # Fall back to default
                    delimiter = '\t'
            except csv.Error:
                # Fall back to default
                delimiter = '\t'
        return delimiter

    def is_package(self, filename=None):
        """Determine if the file is compressed package.

        Parameters
        ----------
        filename : str
            filename

        Returns
        -------
        bool

        """

        if filename is None and hasattr(self, 'filename'):
            filename = self.filename

        if filename:
            self.detect_file_format(filename)

        if self.format == FileFormat.ZIP or self.format == FileFormat.TAR:
            return True
        else:
            return False


class PackageMixin(object):
    """Package mixin to give class basic methods to handle compressed file packages."""
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'ui'):
            self.ui = FancyLogger()

        # Setup progress bar
        if not hasattr(self, 'log_progress'):
            self.log_progress = kwargs.get('log_progress', True)

        if not hasattr(self, 'disable_progress_bar'):
            self.disable_progress_bar = kwargs.get('disable_progress_bar', False)

        if not hasattr(self, 'use_ascii_progress_bar'):
            self.use_ascii_progress_bar = kwargs.get('use_ascii_progress_bar', True)

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    @property
    def package_password(self):
        """Package password

        Returns
        -------
        str or None

        """

        if 'package_password' in self:
            return self['package_password']
        else:
            return None

    @package_password.setter
    def package_password(self, value):
        self['package_password'] = value

    def extract(self, overwrite=False, omit_first_level=True):
        """Extract the package

        Parameters
        ----------
        overwrite : bool
            Overwrite existing files.

        omit_first_level : bool
            Omit first directory level.

        Returns
        -------
        self

        """

        local_path = os.path.split(self.filename)[0]

        if self.format == FileFormat.ZIP:
            with zipfile.ZipFile(self.filename, "r") as z:
                if omit_first_level:
                    parts = []
                    for name in z.namelist():
                        if not name.endswith('/'):
                            parts.append(name.split('/')[:-1])
                    prefix = os.path.commonprefix(parts) or ''

                    if prefix:
                        if len(prefix) > 1:
                            prefix_ = list()
                            prefix_.append(prefix[0])
                            prefix = prefix_

                        prefix = '/'.join(prefix) + '/'
                    offset = len(prefix)

                # Start extraction
                members = z.infolist()
                file_count = 1
                progress = tqdm(members,
                                desc="{0: <25s}".format('Extract'),
                                file=sys.stdout,
                                leave=False,
                                disable=self.disable_progress_bar,
                                ascii=self.use_ascii_progress_bar)

                for i, member in enumerate(progress):
                    if self.disable_progress_bar:
                        self.logger.info('  {title:<15s} [{item_id:d}/{total:d}] {file:<30s}'.format(
                            title='Extract ',
                            item_id=i,
                            total=len(progress),
                            file=member.filename)
                        )

                    if not omit_first_level or len(member.filename) > offset:
                        if omit_first_level:
                            member.filename = member.filename[offset:]
                        progress.set_description("{0: >35s}".format(member.filename.split('/')[-1]))
                        progress.update()
                        if not os.path.isfile(os.path.join(local_path, member.filename)) or overwrite:
                            try:
                                if hasattr(self, 'package_password') and self.package_password:
                                    z.extract(member=member, path=local_path, pwd=self.package_password)
                                else:
                                    z.extract(member=member, path=local_path)

                            except KeyboardInterrupt:
                                # Delete latest file, since most likely it was not extracted fully
                                os.remove(os.path.join(local_path, member.filename))

                                # Quit
                                sys.exit()

                        file_count += 1

        elif self.format == FileFormat.TAR:
            tar = tarfile.open(self.filename, "r:gz")
            progress = tqdm(tar,
                            desc="{0: <25s}".format('Extract'),
                            file=sys.stdout,
                            leave=False,
                            disable=self.disable_progress_bar,
                            ascii=self.use_ascii_progress_bar)

            for i, tar_info in enumerate(progress):
                if self.disable_progress_bar:
                    self.logger.info('  {title:<15s} [{item_id:d}/{total:d}] {file:<30s}'.format(
                        title='Extract ',
                        item_id=i,
                        total=len(progress),
                        file=tar_info.name)
                    )

                if not os.path.isfile(os.path.join(local_path, tar_info.name)) or overwrite:
                    tar.extract(tar_info, local_path)
                tar.members = []
            tar.close()

        return self

