# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys
import logging
import csv
import zipfile
import tarfile
from dcase_util.utils import setup_logging, FileFormat, Path, get_file_hash, is_jupyter
from dcase_util.ui import FancyLogger, FancyStringifier, FancyHTMLStringifier


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

    def __str__(self):
        return self.to_string()

    @property
    def logger(self):
        """Logger instance"""

        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def show(self, mode='auto', indent=0, visualize=False):
        """Print container content

        If called inside Jupyter notebook HTML formatted version is shown.

        Parameters
        ----------
        mode : str
            Output type, possible values ['auto', 'print', 'html']. 'html' will work only in Jupyter notebook
            Default value 'auto'

        indent : int
            Amount of indent
            Default value 0

        visualize : bool
            Visualize container data if class has plot method
            Default value False

        Returns
        -------
        Nothing

        """

        if mode == 'auto':
            if is_jupyter():
                mode = 'html'
            else:
                mode = 'print'

        if mode not in ['html', 'print']:
            # Unknown mode given
            message = '{name}: Unknown mode [{mode}]'.format(name=self.__class__.__name__, mode=mode)
            self.logger.exception(message)
            raise ValueError(message)

        if mode == 'html':
            from IPython.core.display import display, HTML
            display(
                HTML(
                    self.to_html(indent=indent)
                )
            )

            if visualize and hasattr(self, 'plot'):
                # If class has plot method use it to visualize the content
                self.plot()

        elif mode == 'print':
            print(self.to_string(indent=indent))

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

        if hasattr(self, 'filename') and self.filename:
            output += ui.data(field='filename', value=self.filename, indent=indent) + '\n'

        return output

    def to_html(self, indent=0):
        """Get container information in a HTML formatted string

        Parameters
        ----------
        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        return self.to_string(ui=FancyHTMLStringifier(), indent=indent)

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

        self.ui.line(self.__str__(), level=level)


class FileMixin(object):
    """File mixin to give class methods to load and store content."""
    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'ui'):
            self.ui = FancyLogger()

        if kwargs.get('valid_formats', None):
            self.valid_formats = kwargs.get('valid_formats', None)

        elif not hasattr(self, 'valid_formats'):
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

    @property
    def md5(self):
        """Checksum for file.

        Returns
        -------
        str

        """

        if self.exists():
            return get_file_hash(filename=self.filename)

        else:
            return None

    @property
    def bytes(self):
        """File size in bytes

        Returns
        -------
        int

        """

        if self.exists():
            return os.path.getsize(self.filename)

        else:
            return None

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
            Default value None

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
            message = '{name}: File format cannot be detected for file [{filename}] '.format(
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

        Parameters
        ----------
        exclude_delimiters : list of str
            List of delimiter to be excluded
            Default value None

        Returns
        -------
        str

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
            Default value None

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

    @property
    def md5(self):
        """Checksum for file.

        Returns
        -------
        str

        """

        if self.exists():
            return get_file_hash(filename=self.filename)

        else:
            return None

    @property
    def bytes(self):
        """File size in bytes

        Returns
        -------
        int

        """

        if self.exists():
            return os.path.getsize(self.filename)

        else:
            return None

    def extract(self, target_path=None, overwrite=False, omit_first_level=False):
        """Extract the package. Supports Zip and Tar packages.

        Parameters
        ----------
        target_path : str
            Path to extract the package content. If none given, package is extracted in the same path than package.
            Default value None

        overwrite : bool
            Overwrite existing files.
            Default value False

        omit_first_level : bool
            Omit first directory level.
            Default value True

        Returns
        -------
        self

        """

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        if target_path is None:
            target_path = os.path.split(self.filename)[0]

        Path(target_path).create()

        offset = 0

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
                progress = tqdm(
                    members,
                    desc="{0: <25s}".format('Extract'),
                    file=sys.stdout,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )

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

                        if not os.path.isfile(os.path.join(target_path, member.filename)) or overwrite:
                            try:
                                if hasattr(self, 'package_password') and self.package_password:
                                    z.extract(
                                        member=member,
                                        path=target_path,
                                        pwd=self.package_password
                                    )

                                else:
                                    z.extract(
                                        member=member,
                                        path=target_path
                                    )

                            except KeyboardInterrupt:
                                # Delete latest file, since most likely it was not extracted fully
                                os.remove(os.path.join(target_path, member.filename))

                                # Quit
                                sys.exit()

                        file_count += 1

        elif self.format == FileFormat.TAR:
            tar = tarfile.open(self.filename, "r:gz")
            progress = tqdm(
                tar,
                desc="{0: <25s}".format('Extract'),
                file=sys.stdout,
                leave=False,
                disable=self.disable_progress_bar,
                ascii=self.use_ascii_progress_bar
            )

            for i, tar_info in enumerate(progress):
                if self.disable_progress_bar:
                    self.logger.info('  {title:<15s} [{item_id:d}/{total:d}] {file:<30s}'.format(
                        title='Extract ',
                        item_id=i,
                        total=len(progress),
                        file=tar_info.name)
                    )

                if not os.path.isfile(os.path.join(target_path, tar_info.name)) or overwrite:
                    tar.extract(tar_info, target_path)

                tar.members = []
            tar.close()

        return self

    def compress(self, filename=None, path=None, file_list=None, size_limit=None):
        """Compress the package. Supports Zip and Tar packages.

        Parameters
        ----------
        filename : str
            Filename for the package. If None given, one given to class initializer is used.
            Default value None

        path : str
            Path get files if file_list is not set. Files are collected recursively.
            Default value None

        file_list : list of dict
            List of files to be included to the package.
            Item format {'source': 'file1.txt', 'target': 'folder1/file1.txt'}.
            Default value None

        size_limit : int
            Size limit in bytes.
            Default value None

        Returns
        -------
        list of str
            Filenames of created packages

        """

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        if filename is not None:
            self.filename = filename
            self.detect_file_format()
            self.validate_format()

        if path is not None and file_list is None:
            files = Path(path=path).file_list(recursive=True)
            file_list = []

            for filename in files:
                file_list.append(
                    {
                        'source': filename,
                        'target': os.path.relpath(filename)
                    }
                )

        package_filenames = []

        total_uncompressed_size = 0
        for item in file_list:
            total_uncompressed_size += os.path.getsize(item['source'])

        if size_limit is None or total_uncompressed_size < size_limit:
            package = None

            if self.format == FileFormat.ZIP:
                package = zipfile.ZipFile(
                    file=self.filename,
                    mode='w'
                )

            elif self.format == FileFormat.TAR:
                package = tarfile.open(
                    name=self.filename,
                    mode='w:gz'
                )

            package_filenames.append(self.filename)

            size_uncompressed = 0
            for item in file_list:
                if os.path.exists(item['source']):
                    if self.format == FileFormat.ZIP:
                        package.write(
                            filename=item['source'],
                            arcname=os.path.relpath(item['target']),
                            compress_type=zipfile.ZIP_DEFLATED
                        )
                        file_info = package.getinfo(os.path.relpath(item['target']))
                        size_uncompressed += file_info.file_size

                    elif self.format == FileFormat.TAR:
                        package.add(
                            name=item['source'],
                            arcname=os.path.relpath(item['target'])
                        )
                        file_info = package.gettarinfo(
                            name=item['source'],
                            arcname=os.path.relpath(item['target'])
                        )
                        size_uncompressed += file_info.size

                else:
                    package.close()
                    message = '{name}: Non-existing file [{filename}] detected while compressing a package [{package}]'.format(
                        name=self.__class__.__name__,
                        filename=item['source'],
                        package=self.filename
                    )
                    if self.logger:
                        self.logger.exception(message)

                    raise IOError(message)

            package.close()

        else:
            base, extension = os.path.splitext(self.filename)
            filename_template = base + '.{package_id}' + extension
            package = None

            # Initialize package
            package_id = 1

            size_uncompressed = 0
            if self.format == FileFormat.ZIP:
                package = zipfile.ZipFile(
                    file=filename_template.format(package_id=package_id),
                    mode='w'
                )

            elif self.format == FileFormat.TAR:
                package = tarfile.open(
                    name=filename_template.format(package_id=package_id),
                    mode='w:gz'
                )

            package_filenames.append(filename_template.format(package_id=package_id))

            progress = tqdm(
                file_list,
                desc="{0: <25s}".format('Compress'),
                file=sys.stdout,
                leave=False,
                disable=self.disable_progress_bar,
                ascii=self.use_ascii_progress_bar
            )

            for item_id, item in enumerate(progress):
                if self.disable_progress_bar:
                    self.logger.info('  {title:<15s} [{item_id:d}/{total:d}] {file:<30s}'.format(
                        title='Compress ',
                        item_id=item_id,
                        total=len(progress),
                        file=item['source'])
                    )

                if os.path.exists(item['source']):
                    current_size_uncompressed = os.path.getsize(item['source'])
                    if size_uncompressed + current_size_uncompressed > size_limit:
                        # Size limit met, close current package and open a new one.
                        package.close()

                        package_id += 1
                        if self.format == FileFormat.ZIP:
                            package = zipfile.ZipFile(
                                file=filename_template.format(package_id=package_id),
                                mode='w'
                            )

                        elif self.format == FileFormat.TAR:
                            package = tarfile.open(
                                name=filename_template.format(package_id=package_id),
                                mode='w:gz'
                            )

                        package_filenames.append(
                            filename_template.format(package_id=package_id)
                        )

                        size_uncompressed = 0

                    if self.format == FileFormat.ZIP:
                        package.write(
                            filename=item['source'],
                            arcname=os.path.relpath(item['target']),
                            compress_type=zipfile.ZIP_DEFLATED
                        )

                        file_info = package.getinfo(os.path.relpath(item['target']))
                        size_uncompressed += file_info.file_size

                    elif self.format == FileFormat.TAR:
                        package.add(
                            name=item['source'],
                            arcname=os.path.relpath(item['target'])
                        )
                        file_info = package.gettarinfo(
                            name=item['source'],
                            arcname=os.path.relpath(item['target'])
                        )
                        size_uncompressed += file_info.size

                else:
                    package.close()
                    message = '{name}: Non-existing file [{filename}] detected while compressing a package [{package}]'.format(
                        name=self.__class__.__name__,
                        filename=item['source'],
                        package=filename_template.format(package_id=package_id)
                    )

                    if self.logger:
                        self.logger.exception(message)

                    raise IOError(message)

            package.close()

        return package_filenames

