#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import copy
import numpy
import os
import csv
import logging
from dcase_util.containers import ListDictContainer
from dcase_util.utils import posix_path, get_parameter_hash, FieldValidator, setup_logging, FileFormat
from dcase_util.ui import FancyStringifier


class MetaDataItem(dict):
    """Meta data item class, inherited from standard dict class."""
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

        if 'filename_original' in self:
            # Keep file paths in unix format even under Windows
            self['filename_original'] = posix_path(self['filename_original'])

        if 'onset' in self:
            self['onset'] = float(self['onset'])

        if 'offset' in self:
            self['offset'] = float(self['offset'])

        if 'event_label' in self and self.event_label:
            self['event_label'] = self['event_label'].strip()
            if self['event_label'].lower() == 'none':
                self['event_label'] = None

        if 'scene_label' in self and self.scene_label:
            self['scene_label'] = self['scene_label'].strip()
            if self['scene_label'].lower() == 'none':
                self['scene_label'] = None

        if 'tags' in self and self.tags:
            if isinstance(self['tags'], str):
                self['tags'] = self['tags'].strip()
                if self['tags'].lower() == 'none':
                    self['tags'] = None

                if self['tags'] and '#' in self['tags']:
                    self['tags'] = [x.strip() for x in self['tags'].split('#')]

                elif self['tags'] and ',' in self['tags']:
                    self['tags'] = [x.strip() for x in self['tags'].split(',')]

                elif self['tags'] and ';' in self['tags']:
                    self['tags'] = [x.strip() for x in self['tags'].split(';')]

                elif self['tags'] and ':' in self['tags']:
                    self['tags'] = [x.strip() for x in self['tags'].split(':')]

                else:
                    self['tags'] = [self['tags']]

                    # Remove empty tags
            self['tags'] = list(filter(None, self['tags']))

            # Sort tags
            self['tags'].sort()

    def __str__(self):
        ui = FancyStringifier()
        output = ui.title(text=self.__class__.__name__) + '\n'

        output += ui.line(field='Target') + '\n'

        if self.filename:
            output += ui.data(indent=4, field='filename', value=self.filename) + '\n'

        if self.filename_original:
            output += ui.data(indent=4, field='filename_original', value=self.filename_original) + '\n'

        if self.identifier:
            output += ui.data(indent=4, field='identifier', value=self.identifier) + '\n'

        if self.source_label:
            output += ui.data(indent=4, field='source_label', value=self.source_label) + '\n'

        if self.onset is not None:
            output += ui.data(indent=4, field='onset', value=self.onset, unit='sec') + '\n'

        if self.offset is not None:
            output += ui.data(indent=4, field='offset', value=self.offset, unit='sec') + '\n'

        if self.scene_label is not None or self.event_label is not None or self.tags is not None:
            output += ui.line(field='Meta data') + '\n'

        if self.scene_label:
            output += ui.data(indent=4, field='scene_label', value=self.scene_label) + '\n'

        if self.event_label:
            output += ui.data(indent=4, field='event_label', value=self.event_label) + '\n'

        if self.tags:
            output += ui.data(indent=4, field='tags', value=self.tags) + '\n'

        output += ui.line(field='Item') + '\n'
        output += ui.data(indent=4, field='id', value=self.id) + '\n'
        return output

    def show(self):
        """Print container content

        Returns
        -------
        self

        """

        print(self)

        return self

    def log(self, level='info'):
        """Log container content

        Parameters
        ----------
        level : str
            Logging level, possible values [info, debug, warn, warning, error, critical]
            Default value "info"

        Returns
        -------
        self

        """

        from dcase_util.ui import FancyLogger
        FancyLogger().line(str(self), level=level)

        return self

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    @property
    def id(self):
        """Unique item identifier

        ID is formed by taking MD5 hash of the item data.

        Returns
        -------
        str
            Unique item id

        """

        string = ''
        if self.filename:
            string += self.filename
        if self.scene_label:
            string += self.scene_label
        if self.event_label:
            string += self.event_label
        if self.identifier:
            string += self.identifier
        if self.source_label:
            string += self.source_label
        if self.tags:
            string += ','.join(self.tags)
        if self.onset:
            string += '{:8.4f}'.format(self.onset)
        if self.offset:
            string += '{:8.4f}'.format(self.offset)

        return get_parameter_hash(string)

    def get_list(self):
        """Return item values in a list with specified order.

        Returns
        -------
        list

        """

        fields = list(self.keys())

        # Select only valid fields
        valid_fields = ['event_label', 'filename', 'offset', 'onset', 'scene_label', 'identifier', 'source_label', 'tags']
        fields = list(set(fields).intersection(valid_fields))
        fields.sort()

        if fields == ['filename']:
            return [self.filename]

        elif fields == ['event_label', 'filename', 'offset', 'onset', 'scene_label']:
            return [self.filename, self.scene_label, self.onset, self.offset, self.event_label]

        elif fields == ['offset', 'onset']:
            return [self.onset, self.offset]

        elif fields == ['event_label', 'offset', 'onset']:
            return [self.onset, self.offset, self.event_label]

        elif fields == ['filename', 'scene_label']:
            return [self.filename, self.scene_label]

        elif fields == ['filename', 'identifier', 'scene_label']:
            return [self.filename, self.scene_label, self.identifier]

        elif fields == ['event_label', 'filename']:
            return [self.filename, self.event_label]

        elif fields == ['event_label', 'filename', 'offset', 'onset']:
            return [self.filename, self.onset, self.offset, self.event_label]

        elif fields == ['event_label', 'filename', 'offset', 'onset', 'identifier', 'scene_label']:
            return [self.filename, self.scene_label, self.onset, self.offset, self.event_label, self.identifier]

        elif fields == ['event_label', 'filename', 'offset', 'onset', 'scene_label', 'source_label']:
            return [self.filename, self.scene_label, self.onset, self.offset, self.event_label, self.source_label]

        elif fields == ['event_label', 'filename', 'offset', 'onset', 'identifier', 'scene_label', 'source_label']:
            return [self.filename, self.scene_label, self.onset, self.offset, self.event_label,
                    self.source_label, self.identifier]

        elif fields == ['filename', 'tags']:
            return [self.filename, ";".join(self.tags)+";"]

        elif fields == ['filename', 'identifier', 'tags']:
            return [self.filename, ";".join(self.tags)+";", self.identifier]

        elif fields == ['filename', 'scene_label', 'tags']:
            return [self.filename, self.scene_label, ";".join(self.tags)+";"]

        elif fields == ['filename', 'identifier', 'scene_label', 'tags']:
            return [self.filename, self.scene_label, ";".join(self.tags)+";", self.identifier]

        elif fields == ['filename', 'offset', 'onset', 'scene_label', 'tags']:
            return [self.filename, self.scene_label, self.onset, self.offset, ";".join(self.tags)+";"]

        else:
            message = '{name}: Invalid meta data format [{format}]'.format(
                name=self.__class__.__name__,
                format=str(fields)
            )
            self.logger.exception(message)
            raise ValueError(message)

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
    def filename_original(self):
        """Filename

        Returns
        -------
        str or None
            filename

        """

        if 'filename_original' in self:
            return self['filename_original']
        else:
            return None

    @filename_original.setter
    def filename_original(self, value):
        # Keep paths in unix format even under Windows
        self['filename_original'] = posix_path(value)

    @property
    def scene_label(self):
        """Scene label

        Returns
        -------
        str or None
            scene label

        """

        if 'scene_label' in self:
            return self['scene_label']
        else:
            return None

    @scene_label.setter
    def scene_label(self, value):
        self['scene_label'] = value

    @property
    def event_label(self):
        """Event label

        Returns
        -------
        str or None
            event label

        """

        if 'event_label' in self:
            return self['event_label']
        else:
            return None

    @event_label.setter
    def event_label(self, value):
        self['event_label'] = value

    @property
    def onset(self):
        """Onset

        Returns
        -------
        float or None
            onset

        """

        if 'onset' in self:
            return self['onset']
        else:
            return None

    @onset.setter
    def onset(self, value):
        self['onset'] = float(value)

    @property
    def offset(self):
        """Offset

        Returns
        -------
        float or None
            offset

        """

        if 'offset' in self:
            return self['offset']
        else:
            return None

    @offset.setter
    def offset(self, value):
        self['offset'] = float(value)

    @property
    def identifier(self):
        """Identifier

        Returns
        -------
        str or None
            location identifier

        """

        if 'identifier' in self:
            return self['identifier']
        else:
            return None

    @identifier.setter
    def identifier(self, value):
        self['identifier'] = value

    @property
    def source_label(self):
        """Source label

        Returns
        -------
        str or None
            source label

        """

        if 'source_label' in self:
            return self['source_label']
        else:
            return None

    @source_label.setter
    def source_label(self, value):
        self['source_label'] = value

    @property
    def tags(self):
        """Tags

        Returns
        -------
        list or None
            tags

        """

        if 'tags' in self:
            return self['tags']
        else:
            return None

    @tags.setter
    def tags(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value.lower() == 'none':
                value = None

            if value and '#' in value:
                value = [x.strip() for x in value.split('#')]
            elif value and ',' in value:
                value = [x.strip() for x in value.split(',')]
            elif value and ':' in value:
                value = [x.strip() for x in value.split(':')]
            elif value and ';' in value:
                value = [x.strip() for x in value.split(';')]

        self['tags'] = value

        # Remove empty tags
        self['tags'] = list(filter(None, self['tags']))

        # Sort tags
        self['tags'].sort()

    def active_within_segment(self, start, stop):
        """Item active withing given segment.

        Parameters
        ----------
        start : float
            Segment start time

        stop : float
            Segment stop time

        Returns
        -------
        bool
            item activity

        """

        if self.onset is not None and start <= self.onset <= stop:
            # item has onset within segment
            return True

        elif self.offset is not None and start <= self.offset <= stop:
            # item has offset within segment
            return True

        elif self.onset is not None and self.offset is not None and self.onset <= start and self.offset >= stop:
            # item starts and ends outside segment
            return True

        else:
            return False


class MetaDataContainer(ListDictContainer):
    """Meta data container class, inherited from ListDictContainer."""
    valid_formats = [FileFormat.CSV, FileFormat.TXT, FileFormat.ANN]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        super(MetaDataContainer, self).__init__(*args, **kwargs)
        self.item_class = MetaDataItem

        # Convert all items in the list to MetaDataItems
        for item_id in range(0, len(self)):
            if not isinstance(self[item_id], self.item_class):
                self[item_id] = self.item_class(self[item_id])

    def __str__(self):
        return self.get_string()

    def __add__(self, other):
        return self.update(super(MetaDataContainer, self).__add__(other))

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

        if not isinstance(item, MetaDataItem) and not isinstance(item, dict):
            message = '{name}: Appending only MetaDataItem or dict allowed.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if isinstance(item, dict):
            item = MetaDataItem(item)

        super(MetaDataContainer, self).append(item)

    @property
    def file_count(self):
        """Number of files

        Returns
        -------
        file_count: int > 0

        """

        return len(self.unique_files)

    @property
    def event_count(self):
        """Number of events

        Returns
        -------
        event_count: int > 0

        """

        return len(self)

    @property
    def scene_label_count(self):
        """Number of unique scene labels

        Returns
        -------
        scene_label_count: int >= 0

        """

        return len(self.unique_scene_labels)

    @property
    def event_label_count(self):
        """Number of unique event labels

        Returns
        -------
        event_label_count: float >= 0

        """

        return len(self.unique_event_labels)

    @property
    def tag_count(self):
        """Number of unique tags

        Returns
        -------
        tag_count: int >= 0

        """

        return len(self.unique_tags)

    @property
    def unique_files(self):
        """Unique files

        Returns
        -------
        labels: list, shape=(n,)
            Unique labels in alphabetical order

        """

        files = []
        for item in self:
            if item.filename and item.filename not in files:
                files.append(item.filename)

        files.sort()
        return files

    @property
    def unique_event_labels(self):
        """Unique event labels

        Returns
        -------
        labels: list, shape=(n,)
            Unique labels in alphabetical order

        """

        labels = []
        for item in self:
            if item.event_label and item.event_label not in labels:
                labels.append(item.event_label)

        labels.sort()
        return labels

    @property
    def unique_scene_labels(self):
        """Unique scene labels

        Returns
        -------
        labels: list, shape=(n,)
            Unique labels in alphabetical order

        """

        labels = []
        for item in self:
            if item.scene_label and item.scene_label not in labels:
                labels.append(item.scene_label)

        labels.sort()
        return labels

    @property
    def unique_tags(self):
        """Unique tags

        Returns
        -------
        tags: list, shape=(n,)
            Unique tags in alphabetical order

        """

        tags = []
        for item in self:
            if item.tags:
                for tag in item.tags:
                    if tag not in tags:
                        tags.append(tag)

        tags.sort()
        return tags

    @property
    def unique_identifiers(self):
        """Unique identifiers

        Returns
        -------
        labels: list, shape=(n,)
            Unique identifier labels in alphabetical order

        """

        labels = []
        for item in self:
            if item.identifier and item.identifier not in labels:
                labels.append(item.identifier)

        labels.sort()
        return labels

    @property
    def max_offset(self):
        """Find the offset (end-time) of last event

        Returns
        -------
        max_offset: float > 0
            maximum offset

        """

        max_offset = 0
        for item in self:
            if 'offset' in item and item.offset > max_offset:
                max_offset = item.offset
        return max_offset

    def log(self, level='info', show_data=False, show_stats=True):
        """Log container content

        Parameters
        ----------
        level : str
            Logging level, possible values [info, debug, warn, warning, error, critical]

        show_data : bool
            Include data

        show_stats : bool
            Include scene and event statistics

        Returns
        -------
        None

        """

        self.ui.line(self.get_string(show_data=show_data, show_stats=show_stats), level=level)

    def log_all(self, level='info'):
        """Log container content with all meta data items.
        """

        self.log(level=level, show_data=True, show_stats=True)

    def show(self, show_data=False, show_stats=True):
        """Print container content

        Parameters
        ----------
        show_data : bool
            Include data
            Default value "True"
        show_stats : bool
            Include scene and event statistics
            Default value "True"

        Returns
        -------
            Nothing

        """

        print(self.get_string(show_data=show_data, show_stats=show_stats))

    def show_all(self):
        """Print container content with all meta data items.
        """

        self.show(show_data=True, show_stats=True)

    def load(self, filename=None, decimal='point'):
        """Load event list from delimited text file (csv-formatted)

        Preferred delimiter is tab, however, other delimiters are supported automatically (they are sniffed automatically).

        Supported input formats:
            - [file(string)]
            - [file(string)][scene_label(string)]
            - [file(string)][scene_label(string)][identifier(string)]
            - [event_onset (float)][tab][event_offset (float)]
            - [event_onset (float)][tab][event_offset (float)][tab][event_label (string)]
            - [file(string)][event_onset (float)][tab][event_offset (float)][tab][event_label (string)]
            - [file(string)[tab][scene_label(string)][tab][event_onset (float)][tab][event_offset (float)][tab][event_label (string)]
            - [file(string)[tab][scene_label(string)][tab][event_onset (float)][tab][event_offset (float)][tab][event_label (string)][tab][source(single character)]
            - [file(string)[tab][scene_label(string)][tab][event_onset (float)][tab][event_offset (float)][tab][event_label (string)][tab][source(string)]
            - [file(string)[tab][tags (list of strings, delimited with ;)]
            - [file(string)[tab][scene_label(string)][tab][tags (list of strings, delimited with ;)]
            - [file(string)[tab][scene_label(string)][tab][tags (list of strings, delimited with ;)][tab][event_onset (float)][tab][event_offset (float)]

        Parameters
        ----------
        filename : str
            Path to the event list in text format (csv). If none given, one given for class constructor is used.

        decimal : str
            Decimal 'point' or 'comma'

        Returns
        -------
        data : list of event dicts
            List containing event dicts

        """

        if filename:
            self.filename = filename
            self.format = self.detect_file_format(self.filename)

        if not os.path.isfile(self.filename):
            message = '{name}: File not found [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
            )
            self.logger.exception(message)
            raise IOError(message)

        if decimal == 'comma':
            delimiter = self.delimiter(exclude_delimiters=[','])

        else:
            delimiter = self.delimiter()

        data = []
        field_validator = FieldValidator()
        with open(self.filename, 'rtU') as f:
            for row in csv.reader(f, delimiter=delimiter):
                if row:
                    row_format = []
                    for item in row:
                        row_format.append(field_validator.process(item))

                    for item_id, item in enumerate(row):
                        if row_format[item_id] == FieldValidator.NUMBER:
                            # Translate decimal comma into decimal point
                            row[item_id] = float(row[item_id].replace(',', '.'))

                        elif row_format[item_id] in [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.ALPHA1, FieldValidator.ALPHA2, FieldValidator.LIST]:
                            row[item_id] = row[item_id].strip()

                    if row_format == [FieldValidator.AUDIOFILE] or row_format == [FieldValidator.AUDIOFILE, FieldValidator.EMPTY]:
                        # Format: [file]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                            })
                        )

                    elif row_format == [FieldValidator.NUMBER, FieldValidator.NUMBER]:
                        # Format: [event_onset  event_offset]
                        data.append(
                            self.item_class({
                                'onset': row[0],
                                'offset': row[1]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING]:
                        # Format: [file scene_label]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.AUDIOFILE]:
                        # Format: [file scene_label file], filename mapping included
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'filename_original': row[2],
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.STRING]:
                        # Format: [file scene_label identifier]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'identifier': row[2],
                            })
                        )

                    elif row_format == [FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING]:
                        # Format: [onset  offset    event_label]
                        data.append(
                            self.item_class({
                                'onset': row[0],
                                'offset': row[1],
                                'event_label': row[2]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING] or row_format == [FieldValidator.AUDIOFILE, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.EMPTY]:
                        # Format: [file onset  offset event_label]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'onset': row[1],
                                'offset': row[2],
                                'event_label': row[3]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER]:
                        # Format: [file event_label onset  offset]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[1]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.STRING]:
                        # Format: [file onset  offset    event_label identifier]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'onset': row[1],
                                'offset': row[2],
                                'event_label': row[3],
                                'identifier': row[4],
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING]:
                        # Format: [file scene_label onset  offset    event_label]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[4]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.ALPHA1]:
                        # Format: [file scene_label onset  offset   event_label source_label]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[4],
                                'source_label': row[5]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.STRING]:
                        # Format: [file scene_label onset  offset   event_label source_label]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[4],
                                'source_label': row[5]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.ALPHA1, FieldValidator.STRING]:
                        # Format: [file scene_label onset offset event_label source_label identifier]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[4],
                                'source_label': row[5],
                                'identifier': row[6]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.STRING, FieldValidator.STRING, FieldValidator.STRING]:
                        # Format: [file scene_label onset offset event_label source_label identifier]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'event_label': row[4],
                                'source_label': row[5],
                                'identifier': row[6]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.LIST]:
                        # Format: [file scene_label tags]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'tags': row[2]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.LIST, FieldValidator.STRING]:
                        # Format: [file scene_label tags identifier]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'tags': row[2],
                                'identifier': row[3]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.LIST, FieldValidator.STRING]:
                        # Format: [file tags]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'tags': row[1],
                                'identifier': row[2]
                            })
                        )

                    elif row_format == [FieldValidator.AUDIOFILE, FieldValidator.STRING, FieldValidator.NUMBER, FieldValidator.NUMBER, FieldValidator.LIST]:
                        # Format: [file scene_label onset offset tags]
                        data.append(
                            self.item_class({
                                'filename': row[0],
                                'scene_label': row[1],
                                'onset': row[2],
                                'offset': row[3],
                                'tags': row[4]
                            })
                        )

                    else:
                        message = '{name}: Unknown row format [{format}], row [{row}]'.format(
                            name=self.__class__.__name__,
                            format=row_format,
                            row=row
                        )
                        self.logger.exception(message)
                        raise IOError(message)

        self.update(data=data)
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

    def get_string(self, show_data=True, show_stats=True):
        """Get content in string format

        Parameters
        ----------
        show_data : bool
            Include data

        show_stats : bool
            Include scene and event statistics

        Returns
        -------
        str
            Multi-line string

        """
        ui = FancyStringifier()

        string_data = ''
        string_data += ui.class_name(self.__class__.__name__) + '\n'
        if self.filename:
            string_data += ui.data(field='Filename', value=self.filename) + '\n'

        string_data += ui.data(field='Items', value=len(self)) + '\n'
        string_data += ui.line(field='Unique') + '\n'
        string_data += ui.data(indent=4, field='Files', value=len(self.unique_files)) + '\n'
        string_data += ui.data(indent=4, field='Scene labels', value=len(self.unique_scene_labels)) + '\n'
        string_data += ui.data(indent=4, field='Event labels', value=len(self.unique_event_labels)) + '\n'
        string_data += ui.data(indent=4, field='Tags', value=len(self.unique_tags)) + '\n'
        string_data += '\n'

        if show_data:
            string_data += ui.line('Meta data', indent=2) + '\n'

            cell_data = [[], [], [], [], [], [], []]

            for row_id, item in enumerate(self):
                cell_data[0].append(item.filename)
                cell_data[1].append(item.onset)
                cell_data[2].append(item.offset)
                cell_data[3].append(item.scene_label)
                cell_data[4].append(item.event_label)
                cell_data[5].append(','.join(item.tags) if item.tags else '-')
                cell_data[6].append(item.identifier if item.tags else '-')

            string_data += ui.table(
                cell_data=cell_data,
                column_headers=['Source', 'Onset', 'Offset', 'Scene', 'Event', 'Tags', 'Identifier'],
                column_types=['str20', 'float2', 'float2', 'str15', 'str15', 'str15', 'str5'],
                indent=8
            )
            string_data += '\n'

        if show_stats:
            stats = self.stats()
            if 'scenes' in stats and 'scene_label_list' in stats['scenes'] and stats['scenes']['scene_label_list']:
                string_data += ui.line('Scene statistics', indent=2) + '\n'

                cell_data = [[], []]

                for scene_id, scene_label in enumerate(stats['scenes']['scene_label_list']):
                    cell_data[0].append(scene_label)
                    cell_data[1].append(int(stats['scenes']['count'][scene_id]))

                string_data += ui.table(
                    cell_data=cell_data,
                    column_headers=['Scene label', 'Count'],
                    column_types=['str20', 'int'],
                    indent=8
                )
                string_data += '\n'

            if 'events' in stats and 'event_label_list' in stats['events'] and stats['events']['event_label_list']:
                string_data += ui.line('Event statistics', indent=2) + '\n'

                cell_data = [[], [], [], []]

                for event_id, event_label in enumerate(stats['events']['event_label_list']):
                    cell_data[0].append(event_label)
                    cell_data[1].append(int(stats['events']['count'][event_id]))
                    cell_data[2].append(stats['events']['length'][event_id])
                    cell_data[3].append(stats['events']['avg_length'][event_id])

                string_data += ui.table(
                    cell_data=cell_data,
                    column_headers=['Event label', 'Count', 'Tot. Length', 'Avg. Length'],
                    column_types=['str20', 'int', 'float2', 'float2'],
                    indent=8
                ) + '\n'

            if 'tags' in stats and 'tag_list' in stats['tags'] and stats['tags']['tag_list']:
                string_data += ui.line('Tag statistics', indent=2) + '\n'

                cell_data = [[], []]

                for tag_id, tag in enumerate(stats['tags']['tag_list']):
                    cell_data[0].append(tag)
                    cell_data[1].append(int(stats['tags']['count'][tag_id]))

                string_data += ui.table(
                    cell_data=cell_data,
                    column_headers=['Tag', 'Count'],
                    column_types=['str20', 'int'],
                    indent=8
                ) + '\n'

        return string_data

    def filter(self, filename=None, file_list=None, scene_label=None, event_label=None, tag=None, identifier=None):
        """Filter content

        Parameters
        ----------
        filename : str, optional
            Filename to be matched

        file_list : list, optional
            List of filenames to be matched

        scene_label : str, optional
            Scene label to be matched

        event_label : str, optional
            Event label to be matched

        tag : str, optional
            Tag to be matched

        identifier : str, optional
            Identifier to be matched

        Returns
        -------
        MetaDataContainer

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

            if scene_label:
                if item.scene_label == scene_label:
                    matched.append(True)
                else:
                    matched.append(False)

            if event_label:
                if item.event_label == event_label:
                    matched.append(True)
                else:
                    matched.append(False)

            if tag:
                if item.tags and tag in item.tags:
                    matched.append(True)
                else:
                    matched.append(False)

            if identifier:
                if item.identifier == identifier:
                    matched.append(True)
                else:
                    matched.append(False)

            if all(matched):
                data.append(copy.deepcopy(item))

        return MetaDataContainer(data)

    def process_events(self, minimum_event_length=None, minimum_event_gap=None):
        """Process event content

        Makes sure that minimum event length and minimum event gap conditions are met per event label class.

        Parameters
        ----------
        minimum_event_length : float > 0.0
            Minimum event length in seconds, shorten than given are filtered out from the output.

        minimum_event_gap : float > 0.0
            Minimum allowed gap between events in seconds from same event label class.

        Returns
        -------
        MetaDataContainer

        """

        processed_events = []
        files = self.unique_files
        if not files:
            files = [None]

        for filename in files:

            for event_label in self.unique_event_labels:
                current_events_items = self.filter(filename=filename, event_label=event_label)

                # Sort events
                current_events_items = sorted(current_events_items, key=lambda k: k.onset)

                # 1. remove short events
                event_results_1 = []
                for event in current_events_items:
                    if minimum_event_length is not None:
                        if event.offset - event.onset >= minimum_event_length:
                            event_results_1.append(event)
                    else:
                        event_results_1.append(event)

                if len(event_results_1) and minimum_event_gap is not None:
                    # 2. remove small gaps between events
                    event_results_2 = []

                    # Load first event into event buffer
                    buffered_event_onset = event_results_1[0].onset
                    buffered_event_offset = event_results_1[0].offset
                    for i in range(1, len(event_results_1)):
                        if event_results_1[i].onset - buffered_event_offset > minimum_event_gap:
                            # The gap between current event and the buffered is bigger than minimum event gap,
                            # store event, and replace buffered event
                            current_event = copy.deepcopy(event_results_1[i])
                            current_event.onset = buffered_event_onset
                            current_event.offset = buffered_event_offset
                            event_results_2.append(current_event)

                            buffered_event_onset = event_results_1[i].onset
                            buffered_event_offset = event_results_1[i].offset
                        else:
                            # The gap between current event and the buffered is smaller than minimum event gap,
                            # extend the buffered event until the current offset
                            buffered_event_offset = event_results_1[i].offset

                    # Store last event from buffer
                    current_event = copy.copy(event_results_1[len(event_results_1) - 1])
                    current_event.onset = buffered_event_onset
                    current_event.offset = buffered_event_offset
                    event_results_2.append(current_event)

                    processed_events += event_results_2

                else:
                    processed_events += event_results_1

        return MetaDataContainer(processed_events)

    def add_time(self, time):
        """Add time offset to event onset and offset timestamps

        Parameters
        ----------
        time : float
            Offset to be added to the onset and offsets

        Returns
        -------
        self

        """

        for item in self:
            if item.onset:
                item.onset += time

            if item.offset:
                item.offset += time

        return self

    def filter_time_segment(self, start=None, stop=None, duration=None, filename=None, zero_time=True, trim=True):
        """Filter time segment

        Parameters
        ----------
        start : float > 0.0
            Segment start, seconds

        stop : float > 0.0
            Segment end, seconds

        duration : float
            Segment duration, seconds

        filename : str
            Filename to filter

        zero_time : bool
            Convert timestamps in respect to the segment start

        trim : bool
            Trim event onsets and offset according to segment start and stop times.

        Returns
        -------
        MetaDataContainer

        """

        if len(self.unique_files) > 1 and filename is None:
            message = '{name}: Meta data contains items for multiple files. Please specify filename parameter.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        elif filename is not None and filename not in self.unique_files:
            message = '{name}: Filename is not used in meta data items.'.format(
                name=self.__class__.__name__
            )
            self.logger.exception(message)
            raise ValueError(message)

        if filename is not None and filename in self.unique_files:
            data = self.filter(filename=filename)

        else:
            data = copy.deepcopy(self)

        if stop is None and duration is not None:
            stop = start + duration

        filtered_data = MetaDataContainer()
        for item in data:
            if item.active_within_segment(start=start, stop=stop):
                item_ = copy.deepcopy(item)

                if zero_time:
                    # Slice start time is new zero time
                    item_.onset -= start
                    item_.offset -= start

                    if trim:
                        # Trim negative onsets to 0 and trim offsets going over slice stop to slice stop.
                        if item_.onset < 0:
                            item_.onset = 0
                        if item_.offset > stop-start:
                            item_.offset = stop - start
                elif trim:
                    if item_.onset < start:
                        item_.onset = start
                    if item_.offset > stop:
                        item_.offset = stop

                if item_.onset != item_.offset:
                    filtered_data.append(item_)

        return filtered_data

    def stats(self, event_label_list=None, scene_label_list=None, tag_list=None):
        """Statistics of the container content

        Parameters
        ----------
        event_label_list : list of str
            List of event labels to be included in the statistics. If none given, all unique labels used

        scene_label_list : list of str
            List of scene labels to be included in the statistics. If none given, all unique labels used

        tag_list : list of str
            List of tags to be included in the statistics. If none given, all unique tags used

        Returns
        -------
        dict

        """

        if event_label_list is None:
            event_label_list = self.unique_event_labels

        if scene_label_list is None:
            scene_label_list = self.unique_scene_labels

        if tag_list is None:
            tag_list = self.unique_tags

        scene_counts = numpy.zeros(len(scene_label_list))

        for scene_id, scene_label in enumerate(scene_label_list):
            for item in self:
                if item.scene_label and item.scene_label == scene_label:
                    scene_counts[scene_id] += 1

        event_lengths = numpy.zeros(len(event_label_list))
        event_counts = numpy.zeros(len(event_label_list))

        for event_id, event_label in enumerate(event_label_list):
            for item in self:
                if item.onset is not None and item.offset is not None and item.event_label == event_label:
                    event_lengths[event_id] += item.offset - item.onset
                    event_counts[event_id] += 1

        tag_counts = numpy.zeros(len(tag_list))
        for tag_id, tag in enumerate(tag_list):
            for item in self:
                if item.tags and tag in item.tags:
                    tag_counts[tag_id] += 1

        return {
            'scenes': {
                'count': scene_counts,
                'scene_label_list': scene_label_list,
            },
            'events': {
                'length': event_lengths,
                'count': event_counts,
                'avg_length': event_lengths/event_counts,
                'event_label_list': event_label_list
            },
            'tags': {
                'count': tag_counts,
                'tag_list': tag_list,
            }
        }

    def scene_stat_counts(self):
        """Scene count statistics

        Returns
        -------
        dict

        """

        stats = {}
        for scene_label in self.unique_scene_labels:
            stats[scene_label] = len(self.filter(scene_label=scene_label))

        return stats

    def event_stat_counts(self):
        """Event count statistics

        Returns
        -------
        dict

        """

        stats = {}
        for event_label in self.unique_event_labels:
            stats[event_label] = len(self.filter(event_label=event_label))

        return stats

    def tag_stat_counts(self):
        """Tag count statistics

        Returns
        -------
        dict

        """

        stats = {}
        for tag in self.unique_tags:
            stats[tag] = len(self.filter(tag=tag))

        return stats

    def to_event_roll(self, label_list=None, time_resolution=0.01, label='event_label', length_seconds=None):
        """Event roll

        Event roll is binary matrix indicating event activity withing time segment defined by time_resolution.

        Parameters
        ----------
        label_list : list
            List of labels in correct order

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.

        label : str
            Meta data field used to create event roll

        length_seconds : float
            Event roll length in seconds

        Returns
        -------
        numpy.ndarray [shape=(math.ceil(data_length * 1 / time_resolution), amount of classes)]

        """

        if label_list is None:
            label_list = self.unique_event_labels

        if len(self.unique_files) <= 1:
            from dcase_util.data import EventRollEncoder
            event_roll = EventRollEncoder(
                label_list=label_list,
                time_resolution=time_resolution,
            ).encode(
                metadata_container=self,
                label=label,
                length_seconds=length_seconds
            )
            return event_roll

        else:
            message = '{name}: Meta data contains items for multiple files.'.format(name=self.__class__.__name__)
            self.logger.exception(message)
            raise ValueError(message)

