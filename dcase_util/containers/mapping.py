#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from six import iteritems
import os
import csv
from dcase_util.containers import DictContainer
from dcase_util.utils import FileFormat


class OneToOneMappingContainer(DictContainer):
    """Mapping container class for 1:1 data mapping, inherited from DictContainer class."""
    valid_formats = [FileFormat.CSV, FileFormat.TXT, FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        # Run DictContainer init
        DictContainer.__init__(self, *args, **kwargs)

        super(OneToOneMappingContainer, self).__init__(*args, **kwargs)

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

        dict.clear(self)
        if self.exists():
            from dcase_util.files import Serializer

            if self.format == FileFormat.TXT or self.format == FileFormat.CSV:
                map_data = {}
                with open(self.filename, 'rtU') as f:
                    for row in csv.reader(f, delimiter=self.delimiter()):
                        if len(row) == 2:
                            map_data[row[0]] = row[1]

                dict.update(self, map_data)

            elif self.format == FileFormat.CPICKLE:
                dict.update(self, Serializer.load_cpickle(filename=self.filename))

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File does not exists [{file}]'.format(name=self.__class__.__name__, file=self.filename)
            self.logger.exception(message)
            raise IOError(message)

        # Check if after load function is defined, call if found
        if hasattr(self, '_after_load'):
            self._after_load()

        return self

    def save(self, filename=None):
        """Save file

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

            if self.format == FileFormat.CSV or self.format == FileFormat.TXT:
                delimiter = ','
                with open(self.filename, 'w') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=delimiter)
                    for key, value in iteritems(self):
                        if key not in ['filename']:
                            csv_writer.writerow((key, value))

            elif self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=dict(self))

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)        # Delete the file, since most likely it was not saved fully
            raise

        # Check if after save function is defined, call if found
        if hasattr(self, '_after_save'):
            self._after_save()

        return self

    @property
    def flipped(self):
        """Exchange map key and value pairs.

        Returns
        -------
        OneToOneMappingContainer
            flipped map

        """

        return OneToOneMappingContainer(dict((v, k) for k, v in iteritems(self)))

    def map(self, key, default=None):
        """Map with a key.

        Parameters
        ----------
        key : str or number
            Mapping key

        default : str or number
            Default value to be returned if key does not exists in the mapping container.

        Returns
        -------
        OneToOneMappingContainer
            flipped map

        """

        if key in self:
            return self[key]

        else:
            return default
