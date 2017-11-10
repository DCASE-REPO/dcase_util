#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import copy
import os
import csv
import logging
from dcase_util.utils import posix_path, get_parameter_hash, FieldValidator

from dcase_util.containers import ListDictContainer
from dcase_util.ui import FancyStringifier
from dcase_util.utils import setup_logging, FileFormat


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
        ui = FancyStringifier()
        output = ui.class_name(self.__class__.__name__) + '\n'
        output += ui.line(field='Meta') + '\n'
        if self.filename:
            output += ui.data(indent=4, field='filename', value=self.filename) + '\n'

        if self.label:
            output += ui.data(indent=4, field='label', value=self.label) + '\n'

        if self.probability is not None:
            output += ui.data(indent=4, field='probability', value=self.probability) + '\n'

        output += ui.line(field='Item') + '\n'
        output += ui.data(indent=4, field='id', value=self.id) + '\n'
        return output

    @property
    def logger(self):
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

        return self

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
    valid_formats = [FileFormat.CSV, FileFormat.TXT]  #: Valid file formats

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
    def file_list(self):
        """List of unique files in the container

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

    def filter(self, filename=None, file_list=None, label=None):
        """Filter content

        Parameters
        ----------
        filename : str, optional
            Filename to be matched

        file_list : list, optional
            List of filenames to be matched

        label : str, optional
            Label to be matched

        Returns
        -------
        ProbabilityContainer

        """

        data = []
        for item in self:
            matched = False
            if filename and item.filename == filename:
                matched = True
            if file_list and item.filename in file_list:
                matched = True
            if label and item.label == label:
                matched = True

            if matched:
                data.append(copy.deepcopy(item))

        return ProbabilityContainer(data)

    def load(self, filename=None, **kwargs):
        """Load probability list from delimited text file (csv-formatted)

        Preferred delimiter is tab, however, other delimiters are supported automatically
        (they are sniffed automatically).

        Supported input formats:
            - [file(string)][label(string)][probability(float)]

        Parameters
        ----------
        filename : str
            Path to the probability list in text format (csv). If none given, one given for class constructor is used.
            Default value "None"

        Returns
        -------
        data : list of probability item dicts
            List containing probability item dicts

        """

        if filename:
            self.filename = filename
            self.format = self.detect_file_format(self.filename)

        if not os.path.isfile(self.filename):
            message = '{name}: File not found [{file}]'.format(
                name=self.__class__.__name__,
                file=self.filename
            )
            self.logger.exception(message)
            raise IOError(message)

        data = []
        field_validator = FieldValidator()

        with open(self.filename, 'rt') as f:
            for row in csv.reader(f, delimiter=self.delimiter()):
                if row:
                    row_format = []
                    for item in row:
                        row_format.append(field_validator.process(item))

                    if row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER]:
                        # Format: [file label probability]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'label': row[1],
                                'probability': row[2],
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.ALPHA1, FieldValidator.NUMBER]:
                        # Format: [file label probability]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'label': row[1],
                                'probability': row[2],
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.ALPHA2, FieldValidator.NUMBER]:
                        # Format: [file label probability]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'label': row[1],
                                'probability': row[2],
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

        list.__init__(self, data)
        return self

    def save(self, filename=None, delimiter='\t', **kwargs):
        """Save content to csv file

        Parameters
        ----------
        filename : str
            Filename. If none given, one given for class constructor is used.

        delimiter : str
            Delimiter to be used

        Returns
        -------
        self

        """

        if filename:
            self.filename = filename

        f = open(self.filename, 'wt')
        try:
            writer = csv.writer(f, delimiter=delimiter)
            for item in self:
                writer.writerow(item.get_list())
        finally:
            f.close()

        return self

