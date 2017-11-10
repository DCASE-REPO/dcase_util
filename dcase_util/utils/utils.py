#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems

import os
import locale
import logging
import logging.config
import pkg_resources
import itertools
import platform
import numpy


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
    if show_bytes:
        output += locale.format("%d", num_bytes, grouping=True) + ' bytes'

    if show_bytes and num_bytes > KB:
        output += ' ('

    if num_bytes > YB:
        output += '%.4g YB' % (num_bytes / YB)

    elif num_bytes > ZB:
        output += '%.4g ZB' % (num_bytes / ZB)

    elif num_bytes > EB:
        output += '%.4g EB' % (num_bytes / EB)

    elif num_bytes > PB:
        output += '%.4g PB' % (num_bytes / PB)

    elif num_bytes > TB:
        output += '%.4g TB' % (num_bytes / TB)

    elif num_bytes > GB:
        output += '%.4g GB' % (num_bytes / GB)

    elif num_bytes > MB:
        output += '%.4g MB' % (num_bytes / MB)

    elif num_bytes > KB:
        output += '%.4g KB' % (num_bytes / KB)

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
    if value is not None:
        try:
            int(value)
            return True

        except ValueError:
            return False

    else:
        return False


def is_float(value):
    if value is not None:
        try:
            float(value)
            return True

        except ValueError:
            return False

    else:
        return False


class SuppressStdoutAndStderr(object):
    """Context manager to suppress STDOUT and STDERR

    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function. This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    After:
    http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions

    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]

        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        """Assign the null pointers to stdout and stderr.
        """

        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        """Re-assign the real stdout/stderr back
        """

        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)

        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


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

        data = []
        labels = recipe.split(self.delimiters['block'])
        for label in labels:
            label = label.strip()
            if label:
                detail_parts = label.split(self.delimiters['detail'])
                label = detail_parts[0].strip()

                # Default values, used when only extractor is defined e.g. [extractor (string)]; [extractor (string)]
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

