# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Files
=====

Utility classes for handling local and remote files.

File
----

*dcase_util.files.File*

Generic file class.

.. autosummary::
    :toctree: generated/

    File
    File.load
    File.save
    File.get_file_information
    File.detect_file_format
    File.validate_format
    File.exists
    File.empty
    File.delimiter
    File.is_package

Package
-------

*dcase_util.files.Package*

Generic package class.

.. autosummary::
    :toctree: generated/

    Package
    Package.extract
    Package.compress
    Package.detect_file_format
    Package.validate_format
    Package.exists

FileLock
--------

*dcase_util.files.FileLock*

Simple file-based locking class.

.. autosummary::
    :toctree: generated/

    FileLock
    FileLock.lock
    FileLock.release
    FileLock.expired
    FileLock.is_locked
    FileLock.touch

RemoteFile
----------

*dcase_util.files.RemoteFile*

Remote file handling class.

.. autosummary::
    :toctree: generated/

    RemoteFile
    RemoteFile.download
    RemoteFile.is_content_type
    RemoteFile.local_md5
    RemoteFile.local_modified
    RemoteFile.local_bytes
    RemoteFile.local_size_string
    RemoteFile.local_exists
    RemoteFile.local_changed
    RemoteFile.remote_file
    RemoteFile.remote_modified
    RemoteFile.remote_bytes
    RemoteFile.remote_status
    RemoteFile.remote_size_string
    RemoteFile.remote_info
    RemoteFile.remote_exists

RemotePackage
-------------

*dcase_util.files.RemotePackage*

Remote package handling class.

.. autosummary::
    :toctree: generated/

    RemotePackage

    RemotePackage.download
    RemotePackage.extract

    RemotePackage.package_password

    RemotePackage.is_content_type
    RemotePackage.local_md5
    RemotePackage.local_modified
    RemotePackage.local_bytes
    RemotePackage.local_size_string
    RemotePackage.local_exists
    RemotePackage.local_changed
    RemotePackage.remote_file
    RemotePackage.remote_modified
    RemotePackage.remote_bytes
    RemotePackage.remote_status
    RemotePackage.remote_size_string
    RemotePackage.remote_info
    RemotePackage.remote_exists

Serializer
----------

*dcase_utils.files.Serializer*

Data serialization class.

.. autosummary::
    :toctree: generated/

    Serializer
    Serializer.load_yaml
    Serializer.load_cpickle
    Serializer.load_json
    Serializer.load_msgpack
    Serializer.load_marshal
    Serializer.save_yaml
    Serializer.save_cpickle
    Serializer.save_json
    Serializer.save_msgpack
    Serializer.save_marshal

"""

from .files import *
from .remote import *
from .serialization import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
