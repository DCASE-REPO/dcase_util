#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys
import time
import socket
import validators

from dcase_util.utils import get_byte_string, get_file_hash, FileFormat, is_jupyter
from dcase_util.ui import FancyStringifier
from dcase_util.containers import DictContainer, PackageMixin


class RemoteFile(DictContainer):
    """Remote file class"""
    valid_formats = []
    valid_content_types = ['code', 'documentation', 'meta', 'audio', 'features']

    def __init__(self, filename=None, content_type=None, local_md5=None,
                 remote_file=None, remote_md5=None, remote_bytes=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str
            Local filename.

        content_type : str or list of str
            Content type, valid labels ['code', 'documentation', 'meta', 'audio', 'features'].

        local_md5 : str
            Checksum of local file (MD5).

        remote_file : str
            URL to remote filename.

        remote_md5 : str
            Checksum of remote file (MD5).

        remote_bytes : int
            Remote file size in bytes

        """

        self.socket_timeout = 120

        # Local
        self.filename = filename
        self.content_type = content_type

        self._local_md5 = local_md5
        self._local_bytes = None
        self._local_modified = None

        # Remote
        self._remote_file = None
        self.remote_file = remote_file
        self.remote_md5 = remote_md5
        self._remote_bytes = remote_bytes
        self._remote_status = None
        self._remote_modified = None

        # Run DictContainer init
        DictContainer.__init__(self, **kwargs)

        # Check remote url
        if self.remote_file is not None and validators.url(self.remote_file) is not True:
            message = '{name}: Remote file URL not valid [{url}]'.format(
                name=self.__class__.__name__,
                url=self.remote_file,
            )
            self.logger.exception(message)
            raise ValueError(message)

        # Check local filename
        if self.filename is None:
            message = '{name}: Local file not set.'.format(
                name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

        # Check content types
        if self.content_type is not None:
            # Validate content type
            if isinstance(self.content_type, str):
                self.content_type = [self.content_type]

            if isinstance(self.content_type, list):
                for content_type in self.content_type:
                    if content_type not in self.valid_content_types:
                        message = '{name}: Invalid content type given for file [{filename}], type [{content_type}]'.format(
                            name=self.__class__.__name__,
                            content_type=content_type,
                            filename=self.remote_file
                        )
                        self.logger.exception(message)
                        raise ValueError(message)

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
        output += ui.data(field='Content type', value=self.content_type, indent=indent) + '\n'

        output += ui.line(field='Local', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='filename', value=self.filename) + '\n'
        output += ui.data(indent=indent + 2, field='local_md5', value=self.local_md5) + '\n'
        output += ui.data(indent=indent + 2, field='Exists', value='Yes' if self.local_exists() else 'No') + '\n'
        output += ui.data(indent=indent + 2, field='Size', value=self.local_size_string()) + '\n'

        if self._remote_file is not None:
            output += ui.line(field='Remote', indent=indent) + '\n'
            output += ui.data(indent=indent + 2, field='remote_file', value=self.remote_file) + '\n'
            output += ui.data(indent=indent + 2, field='remote_md5', value=self.remote_md5) + '\n'
            output += ui.data(indent=indent + 2, field='Exists', value='Yes' if self.remote_exists() else 'No') + '\n'
            output += ui.data(indent=indent + 2, field='Size', value=self.remote_size_string()) + '\n'

        return output

    @property
    def local_md5(self):
        """Checksum for local file.

        Returns
        -------
        str

        """

        if self.local_exists() and self._local_md5 is None:
            self._local_md5 = get_file_hash(filename=self.filename)

        return self._local_md5

    @property
    def local_modified(self):
        """Modification timestamp for local file.

        Returns
        -------
        float

        """

        if self.local_exists() and self._local_modified is None:
            self._local_modified = os.path.getmtime(self.filename)

        return self._local_modified

    @property
    def local_bytes(self):
        """File size of local file in bytes.

        Returns
        -------
        int

        """

        if self.local_exists() and self._local_bytes is None:
            self._local_bytes = os.path.getsize(self.filename)

        return self._local_bytes

    def local_size_string(self):
        """File size of local file in human readable form.

        Returns
        -------
        str

        """
        if self.local_bytes:
            return get_byte_string(self.local_bytes)

        else:
            return None

    @property
    def remote_file(self):
        """URL to remote file

        Returns
        -------
        str

        """

        return self._remote_file

    @remote_file.setter
    def remote_file(self, value):
        if value is not None and validators.url(value) is not True:
            message = '{name}: URL not valid [{url}]'.format(
                name=self.__class__.__name__,
                url=value
            )

            self.logger.exception(message)
            raise ValueError(message)

        self._remote_file = value

    @property
    def remote_modified(self):
        """Last modification time for remote file.

        Returns
        -------
        float

        """

        if self._remote_modified is None:
            self.remote_info()

        return self._remote_modified

    @remote_modified.setter
    def remote_modified(self, value):
        self._remote_modified = value

    @property
    def remote_bytes(self):
        """File size of remote file.

        Returns
        -------
        int

        """

        if self._remote_bytes is None:
            self.remote_info()

        return self._remote_bytes

    @remote_bytes.setter
    def remote_bytes(self, value):
        self._remote_bytes = value

    @property
    def remote_status(self):
        """Status of remote file.

        Returns
        -------
        int
            HTTP status code

        """

        if self._remote_status is None:
            self.remote_info()

        return self._remote_status

    @remote_status.setter
    def remote_status(self, value):
        self._remote_status = value

    def remote_size_string(self):
        """File size of remote file in human readable form.

        Returns
        -------
        str

        """

        return get_byte_string(self.remote_bytes)

    def remote_info(self):
        """Get information about the remove file (status, size, checksum, last modification time).

        Returns
        -------
        self

        """

        import requests
        resp = requests.head(self.remote_file)
        self.remote_status = resp.status_code
        if resp.status_code == 200:
            if 'Content-Length' in resp.headers:
                if 'Content-Encoding' not in resp.headers or resp.headers['Content-Encoding'] != 'gzip':
                    self.remote_bytes = int(resp.headers['Content-Length'])

            if 'Content-MD5' in resp.headers:
                self.remote_md5 = resp.headers['Content-MD5']

        elif resp.status_code in [301, 302] and 'Location' in resp.headers:
            redirected_url = resp.headers['Location']
            resp = requests.head(redirected_url)
            if resp.status_code == 200:
                self.remote_file = redirected_url
                self.remote_status = resp.status_code

                if 'Content-Length' in resp.headers:
                    if 'Content-Encoding' not in resp.headers or resp.headers['Content-Encoding'] != 'gzip':
                        self.remote_bytes = int(resp.headers['Content-Length'])

                if 'Content-MD5' in resp.headers:
                    self.remote_md5 = resp.headers['Content-MD5']

        if 'Last-Modified' in resp.headers:
            self.remote_modified = time.mktime(time.strptime(resp.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z'))

        elif 'Date' in resp.headers:
            self.remote_modified = time.mktime(time.strptime(resp.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z'))

        return self

    def remote_exists(self):
        """Check does the remote file exists (based on HTTP status code).

        Returns
        -------
        bool

        """

        if self.remote_status in [200, 301, 302]:
            return True

        else:
            return False

    def local_exists(self):
        """Check does the local file exists.

        Returns
        -------
        bool

        """

        return os.path.isfile(self.filename)

    def local_changed(self):
        """Check does the local file corresponds to remote file (based on checksum or modification times and file size).

        Returns
        -------
        bool

        """

        if not self.local_exists():
            # Local does not exists
            return True

        if self.remote_md5 is not None:
            # Remote md5 hash available use md5 hashes to check content
            if self.local_md5 == self.remote_md5:
                return False

            else:
                return True
        else:
            # Use file modification time and size to see if local and remote are the same.
            if self.local_modified > self.remote_modified and self.local_bytes == self.remote_bytes:
                return False

            else:
                return True

    def download(self):
        """Download remote file and save it as local file.

        Returns
        -------
        self

        """

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        try:
            if self.local_changed():
                try:
                    from urllib.request import urlretrieve

                except ImportError:
                    from urllib import urlretrieve

                # Set socket timeout
                socket.setdefaulttimeout(self.socket_timeout)

                def progress_hook(t):
                    """
                    Wraps tqdm instance. Don't forget to close() or __exit__()
                    the tqdm instance once you're done with it (easiest using `with` syntax).
                    """

                    last_b = [0]

                    def inner(b=1, bsize=1, tsize=None):
                        """
                        b  : int, optional
                            Number of blocks just transferred [default: 1].
                        bsize  : int, optional
                            Size of each block (in tqdm units) [default: 1].
                        tsize  : int, optional
                            Total size (in tqdm units). If [default: None] remains unchanged.
                        """
                        if tsize is not None:
                            t.total = tsize

                        t.update((b - last_b[0]) * bsize)
                        last_b[0] = b

                    return inner

                tmp_file = self.filename + '.partial_download'

                with tqdm(desc="{0: >25s}".format(os.path.splitext(self.remote_file.split('/')[-1])[0]),
                          file=sys.stdout,
                          unit='B',
                          unit_scale=True,
                          miniters=1,
                          leave=False,
                          disable=self.disable_progress_bar,
                          ascii=self.use_ascii_progress_bar) as t:

                    try:
                        local_filename, headers = urlretrieve(
                            url=self.remote_file,
                            filename=tmp_file,
                            reporthook=progress_hook(t),
                            data=None
                        )
                    except IOError:
                        # Second attempt by ignoring SSL context.
                        import ssl
                        ssl._create_default_https_context = ssl._create_unverified_context

                        local_filename, headers = urlretrieve(
                            url=self.remote_file,
                            filename=tmp_file,
                            reporthook=progress_hook(t),
                            data=None
                        )

                tmp_md5 = get_file_hash(filename=tmp_file)
                file_valid = True
                if self.remote_md5 is not None:
                    if tmp_md5 == self.remote_md5:
                        file_valid = True

                    else:
                        message = '{name}: Download failed [{filename}] [md5 mismatch]'.format(
                            name=self.__class__.__name__,
                            filename=self.remote_file,
                        )
                        self.logger.exception(message)
                        raise IOError(message)

                if file_valid:
                    self._local_md5 = tmp_md5
                    os.rename(tmp_file, self.filename)

        except Exception as e:
            message = '{name}: Download failed [{filename}] [{error_number}: {strerror}]'.format(
                name=self.__class__.__name__,
                filename=self.remote_file,
                error_number=e.errno if hasattr(e, 'errno') else '',
                strerror=e.strerror if hasattr(e, 'strerror') else '',
            )
            self.logger.exception(message)
            raise

        return self

    def is_content_type(self, content_type):
        """Check that file contains given type of content

        Parameters
        ----------
        content_type : str or list
            Content type

        Returns
        -------
        bool

        """

        if self.content_type:
            if isinstance(content_type, list):
                if 'all' in content_type:
                    return True

                for current_type in content_type:
                    if current_type in self.content_type:
                        return True

                return False

            elif isinstance(content_type, str):
                if content_type == 'all':
                    return True

                if content_type in self.content_type:
                    return True

                else:
                    return False

            else:
                return False

        else:
            return True


class RemotePackage(RemoteFile, PackageMixin):
    """Remote package class"""
    valid_formats = [FileFormat.ZIP, FileFormat.TAR]
