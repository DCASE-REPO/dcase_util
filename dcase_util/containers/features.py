#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import

from dcase_util.containers import DataMatrix2DContainer, DataRepository
from dcase_util.utils import FileFormat


class FeatureContainer(DataMatrix2DContainer):
    """Feature container class for a single feature matrix, inherited from DataContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, data=None, stats=None, metadata=None, time_resolution=None, processing_chain=None, **kwargs):
        kwargs.update({
            'data': data,
            'stats': stats,
            'metadata': metadata,
            'time_resolution': time_resolution,
            'processing_chain': processing_chain
        })

        # Run DataMatrix2DContainer init
        DataMatrix2DContainer.__init__(self, **kwargs)

        # Run super init
        super(FeatureContainer, self).__init__(**kwargs)

    @property
    def hop_length_seconds(self):
        return self.time_resolution

    @hop_length_seconds.setter
    def hop_length_seconds(self, value):
        self.time_resolution = value


class FeatureRepository(DataRepository):
    """Feature repository container class to store multiple FeatureContainers together.

    Feature containers for each method are stored in a dict. Method label is used as dictionary key.

    """

    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, filename=None, default_stream_id=0, processing_chain=None, **kwargs):
        """Constructor

        Parameters
        ----------
        filename: str or dict
            Either one filename (str) or multiple filenames in a dictionary. Dictionary based parameter is used to
            construct the repository from separate FeatureContainers, two formats for the dictionary is supported:
            1) label as key, and filename as value, and 2) two-level dictionary label as key1, stream as key2
            and filename as value.
            Default value None

        default_stream_id : str or int
            Default stream id used when accessing data
            Default value 0

        processing_chain : ProcessingChain
            Processing chain to be included into repository
            Default value None

        """

        kwargs.update({
            'filename': filename,
            'default_stream_id': default_stream_id,
            'processing_chain': processing_chain
        })

        super(FeatureRepository, self).__init__(**kwargs)

        self.item_class = FeatureContainer

    def detect_file_format(self, filename=None):
        """Detect file format from extension

        Parameters
        ----------
        filename : str or dict
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

        if isinstance(filename, dict):
            file_format = {}
            for key in filename:
                file_format[filename[key]] = FileFormat.detect(filename=filename[key])

        else:
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

            if self.format and isinstance(self.format, dict):
                valid = True
                for filename in self.format:
                    if self.format[filename] not in self.valid_formats:
                        message = '{name}: Unknown format [{format}] for file [{file}]'.format(
                            name=self.__class__.__name__,
                            format=os.path.splitext(self.format[filename])[-1],
                            file=self.format[filename]
                        )
                        if self.logger:
                            self.logger.exception(message)

                        raise IOError(message)

                if valid:
                    return True

            elif self.format and self.format in self.valid_formats:
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