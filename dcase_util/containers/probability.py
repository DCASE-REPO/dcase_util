#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import copy
import os
import sys
import csv
import logging
import io
import numpy
from dcase_util.utils import posix_path, get_parameter_hash, FieldValidator, setup_logging, \
    is_float, is_int, is_jupyter, FileFormat
from dcase_util.containers import ListDictContainer
from dcase_util.ui import FancyStringifier, FancyHTMLStringifier


class ProbabilityItem(dict):
    """Probability data item class, inherited from standard dict class."""

    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
            dict

        """

        dict.__init__(self, *args)

        # Process fields
        if 'filename' in self:
            # Keep file paths in unix format even under Windows
            self['filename'] = posix_path(self['filename'])

        if 'label' in self and self.label:
            self['label'] = self['label'].strip()
            if self['label'].lower() == 'none':
                self['label'] = None

        if 'probability' in self:
            self['probability'] = float(self['probability'])

    def __str__(self):
        return self.to_string()

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
        output += ui.line(field='Meta', indent=indent) + '\n'
        if self.filename:
            output += ui.data(indent=indent+2, field='filename', value=self.filename) + '\n'

        if self.label:
            output += ui.data(indent=indent+2, field='label', value=self.label) + '\n'

        if self.probability is not None:
            output += ui.data(indent=indent+2, field='probability', value=self.probability) + '\n'

        output += ui.line(field='Item', indent=indent) + '\n'
        output += ui.data(indent=indent+2, field='id', value=self.id) + '\n'
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

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        return logger

    def show(self, mode='auto', indent=0):
        """Print container content

        If called inside Jupyter notebook, HTML formatted version is shown.

        Parameters
        ----------
        mode : str
            Output type, possible values ['auto', 'print', 'html']. 'html' will work in Jupyter notebook only.
            Default value 'auto'

        indent : int
            Amount of indent
            Default value 0

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

        elif mode == 'print':
            print(self.to_string(indent=indent))

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

        from dcase_util.ui import FancyLogger
        FancyLogger().line(str(self), level=level)

        return self

    @property
    def filename(self):
        """Filename

        Returns
        -------
        str or None
            filename

        """

        if 'filename' in self:
            return self['filename']
        else:
            return None

    @filename.setter
    def filename(self, value):
        # Keep file paths in unix format even under Windows
        self['filename'] = posix_path(value)

    @property
    def label(self):
        """Label

        Returns
        -------
        str or None
            label

        """

        if 'label' in self:
            return self['label']
        else:
            return None

    @label.setter
    def label(self, value):
        self['label'] = value

    @property
    def probability(self):
        """probability

        Returns
        -------
        float or None
            probability

        """

        if 'probability' in self:
            return self['probability']
        else:
            return None

    @probability.setter
    def probability(self, value):
        self['probability'] = float(value)

    @property
    def index(self):
        """item index

        Returns
        -------
        int or None
            index

        """

        if 'index' in self:
            return self['index']
        else:
            return None

    @index.setter
    def index(self, value):
        self['index'] = int(value)

    @property
    def id(self):
        """Unique item identifier

        ID is formed by taking MD5 hash of the item data.

        Returns
        -------
        id : str
            Unique item id

        """

        string = ''
        if self.filename:
            string += self.filename
        if self.label:
            string += self.label
        if self.probability:
            string += '{:8.4f}'.format(self.probability)

        return get_parameter_hash(string)

    def get_list(self):
        """Return item values in a list with specified order.

        Returns
        -------
        list

        """

        fields = list(self.keys())

        # Select only valid fields
        valid_fields = ['filename', 'label', 'probability']
        fields = list(set(fields).intersection(valid_fields))
        fields.sort()

        if fields == ['filename', 'label', 'probability']:
            return [self.filename, self.label, self.probability]

        else:
            message = '{name}: Invalid meta data format [{format}]'.format(
                name=self.__class__.__name__,
                format=str(fields)
            )

            self.logger.exception(message)
            raise ValueError(message)


class ProbabilityContainer(ListDictContainer):
    """Probability data container class, inherited from ListDictContainer."""
    valid_formats = [FileFormat.CSV, FileFormat.TXT, FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        super(ProbabilityContainer, self).__init__(*args, **kwargs)
        self.item_class = ProbabilityItem

        # Convert all items in the list to ProbabilityItem
        for item_id in range(0, len(self)):
            if not isinstance(self[item_id], self.item_class):
                self[item_id] = self.item_class(self[item_id])

    def __add__(self, other):
        return self.update(super(ProbabilityContainer, self).__add__(other))

    def append(self, item):
        """Append item to the meta data list

        Parameters
        ----------

        item : MetaDataItem or dict
            Item to be appended.

        Raises
        ------
        ValueError
            Item not correct type.

        """

        if not isinstance(item, ProbabilityItem) and not isinstance(item, dict):
            message = '{name}: Appending only ProbabilityItem or dict allowed.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if isinstance(item, dict):
            item = ProbabilityItem(item)

        super(ProbabilityContainer, self).append(item)

    @property
    def unique_files(self):
        """Unique files

        Returns
        -------
        list

        """

        files = {}
        for item in self:
            files[item.filename] = item.filename

        return sorted(list(files.values()))

    @property
    def unique_labels(self):
        """Unique labels

        Returns
        -------
        labels: list, shape=(n,)
            Unique labels in alphabetical order

        """

        labels = []
        for item in self:
            if 'label' in item and item['label'] not in labels:
                labels.append(item.label)

        labels.sort()
        return labels

    @property
    def unique_indices(self):
        """Unique indices

        Returns
        -------
        indices: list, shape=(n,)
            Unique indices in numerical order

        """

        indices = []
        for item in self:
            if 'index' in item and item['index'] not in indices:
                indices.append(item.index)

        indices.sort()
        return indices

    def update(self, data):
        """Replace content with given list

        Parameters
        ----------
        data : list
            New content

        Returns
        -------
        self

        """

        super(ProbabilityContainer, self).update(data=data)

        # Convert all items in the list to ProbabilityItem
        for item_id in range(0, len(self)):
            if not isinstance(self[item_id], self.item_class):
                self[item_id] = self.item_class(self[item_id])

        return self

    def filter(self, filename=None, file_list=None, label=None, index=None):
        """Filter content

        Parameters
        ----------
        filename : str, optional
            Filename to be matched

        file_list : list, optional
            List of filenames to be matched

        label : str, optional
            Label to be matched

        index : int, optional
            Index to be matched

        Returns
        -------
        ProbabilityContainer

        """

        data = []
        for item in self:
            matched = []
            if filename:
                if item.filename == filename:
                    matched.append(True)

                else:
                    matched.append(False)

            if file_list:
                if item.filename in file_list:
                    matched.append(True)

                else:
                    matched.append(False)

            if label:
                if item.label == label:
                    matched.append(True)

                else:
                    matched.append(False)

            if index is not None:
                if item.index == index:
                    matched.append(True)

                else:
                    matched.append(False)

            if all(matched):
                data.append(copy.deepcopy(item))

        return ProbabilityContainer(data)

    def load(self, filename=None, fields=None, csv_header=True, file_format=None, delimiter=None, decimal='point'):
        """Load probability list from file

        Preferred delimiter is tab, however, other delimiters are supported automatically
        (they are sniffed automatically).

        Supported input formats:
            - [file(string)][label(string)][probability(float)]

        Parameters
        ----------
        filename : str
            Path to the probability list in text format (csv). If none given, one given for class constructor is used.
            Default value None

        fields : list of str, optional
            List of column names. Used only for CSV formatted files.
            Default value None

        csv_header : bool, optional
            Read field names from first line (header). Used only for CSV formatted files.
            Default value True

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

        delimiter : str, optional
            Forced data delimiter for csv format. If None given, automatic delimiter sniffer used.
            Use this when sniffer does not work.
            Default value None

        decimal : str
            Decimal 'point' or 'comma'
            Default value 'point'


        Returns
        -------
        data : list of probability item dicts
            List containing probability item dicts

        """

        def validate(row_format, valid_formats):
            for valid_format in valid_formats:
                if row_format == valid_format:
                    return True

            return False

        if filename:
            self.filename = filename
            if not file_format:
                self.detect_file_format()
                self.validate_format()

        if file_format and FileFormat.validate_label(label=file_format):
            self.format = file_format

        if self.exists():
            if self.format in [FileFormat.TXT]:
                if decimal == 'comma':
                    delimiter = self.delimiter(exclude_delimiters=[','])

                else:
                    delimiter = self.delimiter()

                data = []
                field_validator = FieldValidator()
                f = io.open(self.filename, 'rt')
                try:
                    for row in csv.reader(f, delimiter=delimiter):
                        if row:
                            row_format = []
                            for item in row:
                                row_format.append(field_validator.process(item))

                            for item_id, item in enumerate(row):

                                if row_format[item_id] == FieldValidator.NUMBER:
                                    # Translate decimal comma into decimal point
                                    row[item_id] = float(row[item_id].replace(',', '.'))

                                elif row_format[item_id] in [FieldValidator.AUDIOFILE,
                                                             FieldValidator.DATAFILE,
                                                             FieldValidator.STRING,
                                                             FieldValidator.ALPHA1,
                                                             FieldValidator.ALPHA2,
                                                             FieldValidator.LIST]:

                                    row[item_id] = row[item_id].strip()

                            if validate(row_format=row_format,
                                        valid_formats=[
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.STRING,
                                             FieldValidator.NUMBER],
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.ALPHA1,
                                             FieldValidator.NUMBER],
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.ALPHA2,
                                             FieldValidator.NUMBER],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.STRING,
                                             FieldValidator.NUMBER],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.ALPHA1,
                                             FieldValidator.NUMBER],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.ALPHA2,
                                             FieldValidator.NUMBER]
                                        ]):
                                # Format: [file label probability]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'label': row[1],
                                        'probability': row[2],
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.ALPHA1,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.ALPHA2,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.ALPHA1,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.ALPHA2,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER]
                                          ]):
                                # Format: [file label probability index]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'label': row[1],
                                        'probability': row[2],
                                        'index': row[3]
                                    })
                                )

                            else:
                                message = '{name}: Unknown row format [{row}] [{row_format}]'.format(
                                    name=self.__class__.__name__,
                                    row=row,
                                    row_format=row_format
                                )
                                self.logger.exception(message)
                                raise IOError(message)

                finally:
                    f.close()

                self.update(data=data)

            elif self.format == FileFormat.CSV:
                if fields is None and csv_header is None:
                    message = '{name}: Parameters fields or csv_header has to be set for CSV files.'.format(
                        name=self.__class__.__name__
                    )
                    self.logger.exception(message)
                    raise ValueError(message)

                if not delimiter:
                    if decimal == 'comma':
                        delimiter = self.delimiter(exclude_delimiters=[','])

                    else:
                        delimiter = self.delimiter()

                data = []
                with open(self.filename, 'r') as f:
                    csv_reader = csv.reader(f, delimiter=delimiter)
                    if csv_header:
                        csv_fields = next(csv_reader)
                        if fields is None:
                            fields = csv_fields

                    for row in csv_reader:
                        if row:
                            for cell_id, cell_data in enumerate(row):
                                if decimal == 'comma':
                                    # Translate decimal comma into decimal point
                                    cell_data = float(cell_data.replace(',', '.'))

                                if is_int(cell_data):
                                    row[cell_id] = int(cell_data)

                                elif is_float(cell_data):
                                    row[cell_id] = float(cell_data)

                            data.append(dict(zip(fields, row)))

                self.update(data=data)

            elif self.format == FileFormat.CPICKLE:
                from dcase_util.files import Serializer
                self.update(
                    data=Serializer.load_cpickle(filename=self.filename)
                )

        else:
            message = '{name}: File not found [{file}]'.format(
                name=self.__class__.__name__,
                file=self.filename
            )
            self.logger.exception(message)
            raise IOError(message)

        return self

    def save(self, filename=None, fields=None, csv_header=True, file_format=None, delimiter='\t',  **kwargs):
        """Save content to csv file

        Parameters
        ----------
        filename : str
            Filename. If none given, one given for class constructor is used.
            Default value None

        fields : list of str
            Fields in correct order, if none given all field in alphabetical order will be outputted.
            Used only for CSV formatted files.
            Default value None

        csv_header : bool
            In case of CSV formatted file, first line will contain field names. Names are taken from fields parameter.
            Default value True

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

        delimiter : str
            Delimiter to be used when saving data.
            Default value '\t'

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename
            if not file_format:
                self.detect_file_format()
                self.validate_format()

        if file_format and FileFormat.validate_label(label=file_format):
            self.format = file_format

        if self.format in [FileFormat.TXT]:
            # Make sure writing is using correct line endings to avoid extra empty lines
            if sys.version_info[0] == 2:
                f = open(self.filename, 'wbt')

            elif sys.version_info[0] >= 3:
                f = open(self.filename, 'wt', newline='')

            try:
                writer = csv.writer(f, delimiter=delimiter)
                for item in self:
                    writer.writerow(item.get_list())

            finally:
                f.close()

        elif self.format == FileFormat.CSV:
            if fields is None:
                fields = set()
                for item in self:
                    fields.update(list(item.keys()))

                fields = sorted(list(fields))

            # Make sure writing is using correct line endings to avoid extra empty lines
            if sys.version_info[0] == 2:
                csv_file = open(self.filename, 'wb')

            elif sys.version_info[0] >= 3:
                csv_file = open(self.filename, 'w', newline='')

            try:
                csv_writer = csv.writer(csv_file, delimiter=delimiter)
                if csv_header:
                    csv_writer.writerow(fields)

                for item in self:
                    item_values = []
                    for field in fields:
                        value = item[field]
                        if isinstance(value, list):
                            value = ";".join(value)+";"

                        item_values.append(value)

                    csv_writer.writerow(item_values)

            finally:
                csv_file.close()

        elif self.format == FileFormat.CPICKLE:
            from dcase_util.files import Serializer
            Serializer.save_cpickle(filename=self.filename, data=self)

        else:
            message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
            self.logger.exception(message)
            raise IOError(message)

        return self

    def as_matrix(self, label_list=None, filename=None, file_list=None, default_value=0):
        """Get probabilities as data matrix.
        If items has index defined, index is used to order columns.
        If items has filename, filename is used to order columns.

        Parameters
        ----------
        label_list : list of str
            List of labels. If none given, labels in the container are used in alphabetical order.
            Default value None

        filename : str
            Filename to filter content. If none given, one given for class constructor is used.
            Default value None

        file_list : list of str
            List of filenames to included in the matrix.
            Default value None

        default_value : numerical
            Default value of the element in the matrix. Used in case there is no data for the element in the container.

        Returns
        -------
        DataMatrix2DContainer

        """

        data = self.filter(
            filename=filename,
            file_list=file_list
        )

        if label_list is None:
            label_list = data.unique_labels

        indices = data.unique_indices

        if file_list is None:
            file_list = data.unique_files

        if indices:
            matrix = numpy.ones((len(label_list), len(indices))) * default_value
            for index in indices:
                current_column = data.filter(index=index)
                for item in current_column:
                    if item.label in label_list:
                        matrix[label_list.index(item.label), index] = item.probability

            from dcase_util.containers import DataMatrix2DContainer
            return DataMatrix2DContainer(data=matrix)

        elif file_list:
            matrix = numpy.ones((len(label_list), len(file_list))) * default_value

            for file_id, filename in enumerate(file_list):
                current_column = data.filter(filename=filename)
                for item in current_column:
                    if item.label in label_list:
                        matrix[label_list.index(item.label), file_id] = item.probability

            from dcase_util.containers import DataMatrix2DContainer
            return DataMatrix2DContainer(data=matrix)

