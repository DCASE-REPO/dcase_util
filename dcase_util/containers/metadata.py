#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import six
import sys
import os
import copy
import numpy
import csv
import logging
import io
from dcase_util.containers import ListDictContainer
from dcase_util.utils import posix_path, get_parameter_hash, FieldValidator, \
    setup_logging, is_float, is_int, is_jupyter, FileFormat
from dcase_util.ui import FancyStringifier,  FancyHTMLStringifier


class MetaDataItem(dict):
    """Meta data item class, inherited from standard dict class."""
    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
            dict

        """

        dict.__init__(self, *args)

        # Compatibility with old field names used in DCASE baseline system implementations 2016 and 2017
        if 'file' in self and 'filename' not in self:
            self['filename'] = self['file']

        if 'event_onset' in self and 'onset' not in self:
            self['onset'] = self['event_onset']

        if 'event_offset' in self and 'offset' not in self:
            self['offset'] = self['event_offset']

        # Process meta data fields

        # File target for the meta data item
        if 'filename' in self and isinstance(self['filename'], six.string_types):
            if not os.path.isabs(self['filename']):
                # Force relative file paths into unix format even under Windows
                self['filename'] = posix_path(self['filename'])

        if 'filename_original' in self and isinstance(self['filename_original'], six.string_types):
            # Keep file paths in unix format even under Windows
            self['filename_original'] = posix_path(self['filename_original'])

        # Meta data item timestamps: onset and offset
        if 'onset' in self:
            if is_float(self['onset']):
                self['onset'] = float(self['onset'])
            else:
                self['onset'] = None

        if 'offset' in self:
            if is_float(self['offset']):
                self['offset'] = float(self['offset'])
            else:
                self['offset'] = None

        # Event label assigned to the meta data item
        if 'event_label' in self:
            self['event_label'] = self['event_label'].strip()
            if self['event_label'].lower() == 'none' or self['event_label'] == '':
                self['event_label'] = None

        # Acoustic scene label assigned to the meta data item
        if 'scene_label' in self and self.scene_label:
            self['scene_label'] = self['scene_label'].strip()
            if self['scene_label'].lower() == 'none':
                self['scene_label'] = None

        # Tag labels
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
        output += ui.line(field='Target', indent=indent) + '\n'

        if self.filename:
            output += ui.data(indent=indent + 2, field='filename', value=self.filename) + '\n'

        if self.filename_original:
            output += ui.data(indent=indent + 2, field='filename_original', value=self.filename_original) + '\n'

        if self.identifier:
            output += ui.data(indent=indent + 2, field='identifier', value=self.identifier) + '\n'

        if self.source_label:
            output += ui.data(indent=indent + 2, field='source_label', value=self.source_label) + '\n'

        if self.set_label:
            output += ui.data(indent=indent + 2, field='set_label', value=self.set_label) + '\n'

        if self.onset is not None:
            output += ui.data(indent=indent + 2, field='onset', value=self.onset, unit='sec') + '\n'

        if self.offset is not None:
            output += ui.data(indent=indent + 2, field='offset', value=self.offset, unit='sec') + '\n'

        if self.scene_label is not None or self.event_label is not None or self.tags is not None:
            output += ui.line(field='Meta data', indent=indent) + '\n'

        if self.scene_label:
            output += ui.data(indent=indent + 2, field='scene_label', value=self.scene_label) + '\n'

        if self.event_label:
            output += ui.data(indent=indent + 2, field='event_label', value=self.event_label) + '\n'

        if self.tags:
            output += ui.data(indent=indent + 2, field='tags', value=self.tags) + '\n'

        output += ui.line(field='Item', indent=indent) + '\n'
        output += ui.data(indent=indent + 2, field='id', value=self.id) + '\n'
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
            Default value "info"

        Returns
        -------
        self

        """

        from dcase_util.ui import FancyLogger
        FancyLogger().line(self.__str__(), level=level)

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

        if self.set_label:
            string += self.set_label

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

        valid_fields = ['event_label', 'filename', 'offset', 'onset',
                        'scene_label', 'identifier', 'source_label', 'tags']

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
        if not os.path.isabs(value):
            # Force relative file paths into unix format even under Windows
            value = posix_path(value)

        self['filename'] = value

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

        if 'event_onset' in self:
            # Mirror onset to event_onset
            self['event_onset'] = self['onset']

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

        if 'event_offset' in self:
            # Mirror onset to event_onset
            self['event_offset'] = self['offset']

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
    def set_label(self):
        """Set label

        Returns
        -------
        str or None
            set label

        """

        if 'set_label' in self:
            return self['set_label']
        else:
            return None

    @set_label.setter
    def set_label(self, value):
        self['set_label'] = value

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
    valid_formats = [FileFormat.CSV, FileFormat.TXT, FileFormat.ANN, FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        super(MetaDataContainer, self).__init__(*args, **kwargs)
        self.item_class = MetaDataItem

        # Convert all items in the list to MetaDataItems
        for item_id in range(0, len(self)):
            if not isinstance(self[item_id], self.item_class):
                self[item_id] = self.item_class(self[item_id])

        from dcase_util.processors import ProcessingChain
        self.processing_chain = ProcessingChain()

    def __str__(self):
        return self.to_string()

    def to_string(self, ui=None, indent=0, show_info=True, show_data=True, show_stats=True):
        """Get container information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        show_info : bool
            Include basic info about the container
            Default value True

        show_data : bool
            Include data
            Default value True

        show_stats : bool
            Include scene and event statistics
            Default value True

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = ''

        if show_info:
            output += ui.class_name(self.__class__.__name__) + '\n'

            if hasattr(self, 'filename') and self.filename:
                output += ui.data(
                    field='Filename',
                    value=self.filename,
                    indent=indent
                ) + '\n'

            output += ui.data(field='Items', value=len(self), indent=indent) + '\n'
            output += ui.line(field='Unique', indent=indent) + '\n'
            output += ui.data(indent=indent + 2, field='Files', value=len(self.unique_files)) + '\n'
            output += ui.data(indent=indent + 2, field='Scene labels', value=len(self.unique_scene_labels)) + '\n'
            output += ui.data(indent=indent + 2, field='Event labels', value=len(self.unique_event_labels)) + '\n'
            output += ui.data(indent=indent + 2, field='Tags', value=len(self.unique_tags)) + '\n'
            output += ui.data(indent=indent + 2, field='Identifiers', value=len(self.unique_identifiers)) + '\n'
            output += ui.data(indent=indent + 2, field='Source labels', value=len(self.unique_source_labels)) + '\n'
            output += '\n'

        if show_data:
            output += ui.line('Meta data', indent=indent) + '\n'

            cell_data = [[], [], [], [], [], [], []]

            for row_id, item in enumerate(self):
                cell_data[0].append(item.filename)
                cell_data[1].append(item.onset)
                cell_data[2].append(item.offset)
                cell_data[3].append(item.scene_label)
                cell_data[4].append(item.event_label)
                cell_data[5].append(','.join(item.tags) if item.tags else '-')
                cell_data[6].append(item.identifier if item.tags else '-')

            output += ui.table(
                cell_data=cell_data,
                column_headers=['Source', 'Onset', 'Offset', 'Scene', 'Event', 'Tags', 'Identifier'],
                column_types=['str20', 'float2', 'float2', 'str15', 'str15', 'str15', 'str5'],
                indent=indent + 2
            )
            output += '\n'

        if show_stats:
            stats = self.stats()
            if 'scenes' in stats and 'scene_label_list' in stats['scenes'] and stats['scenes']['scene_label_list']:
                output += ui.line('Scene statistics', indent=indent) + '\n'

                cell_data = [[], [], []]

                for scene_id, scene_label in enumerate(stats['scenes']['scene_label_list']):
                    cell_data[0].append(scene_label)
                    cell_data[1].append(int(stats['scenes']['count'][scene_id]))
                    cell_data[2].append(int(stats['scenes']['identifiers'][scene_id]))

                output += ui.table(
                    cell_data=cell_data,
                    column_headers=['Scene label', 'Count', 'Identifiers'],
                    column_types=['str20', 'int', 'int'],
                    indent=indent + 2
                )
                output += '\n'

            if 'events' in stats and 'event_label_list' in stats['events'] and stats['events']['event_label_list']:
                output += ui.line('Event statistics', indent=indent) + '\n'

                cell_data = [[], [], [], []]

                for event_id, event_label in enumerate(stats['events']['event_label_list']):
                    cell_data[0].append(event_label)
                    cell_data[1].append(int(stats['events']['count'][event_id]))
                    cell_data[2].append(stats['events']['length'][event_id])
                    cell_data[3].append(stats['events']['avg_length'][event_id])

                output += ui.table(
                    cell_data=cell_data,
                    column_headers=['Event label', 'Count', 'Tot. Length', 'Avg. Length'],
                    column_types=['str20', 'int', 'float2', 'float2'],
                    indent=indent + 2
                ) + '\n'

            if 'tags' in stats and 'tag_list' in stats['tags'] and stats['tags']['tag_list']:
                output += ui.line('Tag statistics', indent=indent) + '\n'

                cell_data = [[], []]

                for tag_id, tag in enumerate(stats['tags']['tag_list']):
                    cell_data[0].append(tag)
                    cell_data[1].append(int(stats['tags']['count'][tag_id]))

                output += ui.table(
                    cell_data=cell_data,
                    column_headers=['Tag', 'Count'],
                    column_types=['str20', 'int'],
                    indent=indent + 2
                ) + '\n'

        return output

    def to_html(self, indent=0, show_info=True, show_data=True, show_stats=True):
        """Get container information in a HTML formatted string

        Parameters
        ----------
        indent : int
            Amount of indent
            Default value 0

        show_info : bool
            Include basic info about the container
            Default value True

        show_data : bool
            Include data
            Default value True

        show_stats : bool
            Include scene and event statistics
            Default value True

        Returns
        -------
        str

        """

        return self.to_string(ui=FancyHTMLStringifier(), indent=indent, show_info=show_info, show_data=show_data, show_stats=show_stats)

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
    def identifier_count(self):
        """Number of unique identifiers

        Returns
        -------
        identifier_count: float >= 0

        """

        return len(self.unique_identifiers)

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
                files.append(str(item.filename))

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
    def unique_source_labels(self):
        """Unique source labels

        Returns
        -------
        labels: list, shape=(n,)
            Unique labels in alphabetical order

        """

        labels = []
        for item in self:
            if item.source_label and item.source_label not in labels:
                labels.append(item.source_label)

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

        super(MetaDataContainer, self).update(data=data)

        # Convert all items in the list to MetaDataItems
        for item_id in range(0, len(self)):
            if not isinstance(self[item_id], self.item_class):
                self[item_id] = self.item_class(self[item_id])

        return self

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

        self.ui.line(self.to_string(show_data=show_data, show_stats=show_stats), level=level)

    def log_all(self, level='info'):
        """Log container content with all meta data items.
        """

        self.log(level=level, show_data=True, show_stats=True)

    def show(self, mode='auto', indent=0, show_info=True, show_data=False, show_stats=True):
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

        show_info : bool
            Include basic info about the container
            Default value True

        show_data : bool
            Include data
            Default value True

        show_stats : bool
            Include scene and event statistics
            Default value True

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
                    self.to_html(indent=indent, show_info=show_info, show_data=show_data, show_stats=show_stats)
                )
            )

        elif mode == 'print':
            print(self.to_string(indent=indent, show_info=show_info, show_data=show_data, show_stats=show_stats))

    def show_all(self, mode='auto', indent=0):
        """Print container content with all meta data items.

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

        self.show(mode=mode, indent=indent, show_data=True, show_stats=True)

    def load(self, filename=None, fields=None, csv_header=True, file_format=None, delimiter=None, decimal='point'):
        """Load event list from delimited text file (csv-formatted)

        Preferred delimiter is tab, however, other delimiters are supported automatically
        (they are sniffed automatically).

        Supported input formats:
            - [file(string)]
            - [file(string)][scene_label(string)]
            - [file(string)][scene_label(string)][identifier(string)]
            - [event_onset (float)][tab][event_offset (float)]
            - [event_onset (float)][tab][event_offset (float)][tab][event_label (string)]
            - [file(string)][tab][onset (float)][tab][offset (float)][tab][event_label (string)]
            - [file(string)[tab][scene_label(string)][tab][onset (float)][tab][offset (float)]
            - [file(string)[tab][scene_label(string)][tab][onset (float)][tab][offset (float)][tab][event_label (string)]
            - [file(string)[tab][scene_label(string)][tab][onset (float)][tab][offset (float)][tab][event_label (string)][tab][source(single character)]
            - [file(string)[tab][scene_label(string)][tab][onset (float)][tab][offset (float)][tab][event_label (string)][tab][source(string)]
            - [file(string)[tab][tags (list of strings, delimited with ;)]
            - [file(string)[tab][scene_label(string)][tab][tags (list of strings, delimited with ;)]
            - [file(string)[tab][scene_label(string)][tab][tags (list of strings, delimited with ;)][tab][event_onset (float)][tab][event_offset (float)]

        Parameters
        ----------
        filename : str
            Path to the meta data in text format (csv). If none given, one given for class constructor is used.
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
            Forced data delimiter for csv format. If None given, automatic delimiter sniffer used. Use this when sniffer does not work.
            Default value None

        decimal : str
            Decimal 'point' or 'comma'
            Default value 'point'

        Returns
        -------
        data : list of event dicts
            List containing event dicts

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
            if self.format in [FileFormat.TXT, FileFormat.ANN]:
                if delimiter is None:
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
                                            [FieldValidator.AUDIOFILE],
                                            [FieldValidator.DATAFILE],
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.EMPTY],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.EMPTY],
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY],
                                            [FieldValidator.AUDIOFILE,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY],
                                            [FieldValidator.DATAFILE,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY,
                                             FieldValidator.EMPTY]
                                        ]):

                                # Format: [file]
                                data.append(
                                    self.item_class({
                                        'filename': row[0]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.NUMBER,
                                               FieldValidator.NUMBER]
                                          ]):

                                # Format: [onset offset]
                                data.append(
                                    self.item_class({
                                        'onset': row[0],
                                        'offset': row[1]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER]
                                          ]):

                                # Format: [file onset offset]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'onset': row[1],
                                        'offset': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING],
                                          ]):

                                # Format: [file scene_label]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.AUDIOFILE],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.DATAFILE],
                                          ]):

                                # Format: [file scene_label file], filename mapping included
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'filename_original': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING],
                                          ]):

                                # Format: [file scene_label identifier]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'identifier': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING],
                                              [FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.ALPHA2],
                                          ]):

                                # Format: [onset offset event_label]
                                data.append(
                                    self.item_class({
                                        'onset': row[0],
                                        'offset': row[1],
                                        'event_label': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING],
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file onset offset event_label]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'onset': row[1],
                                        'offset': row[2],
                                        'event_label': row[3]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER]
                                          ]):

                                # Format: [file scene_label onset offset]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'onset': row[2],
                                        'offset': row[3],
                                        'scene_label': row[1]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file onset offset event_label identifier]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'onset': row[1],
                                        'offset': row[2],
                                        'event_label': row[3],
                                        'identifier': row[4]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER]
                                          ]):

                                # Format: [file scene_label onset offset]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'onset': row[2],
                                        'offset': row[3]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file scene_label onset offset event_label]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'onset': row[2],
                                        'offset': row[3],
                                        'event_label': row[4]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.ALPHA1],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.ALPHA1]
                                          ]):

                                # Format: [file scene_label onset offset event_label source_label]
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

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file scene_label onset offset event_label source_label]
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

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.ALPHA1,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.ALPHA1,
                                               FieldValidator.STRING]
                                          ]):

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

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING,
                                               FieldValidator.STRING]
                                          ]):

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

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.LIST],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.LIST]
                                          ]):

                                # Format: [file scene_label tags]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'tags': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.LIST,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.LIST,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file scene_label tags identifier]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'scene_label': row[1],
                                        'tags': row[2],
                                        'identifier': row[3]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.LIST],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.LIST]
                                          ]):

                                # Format: [file tags]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'tags': row[1]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.LIST,
                                               FieldValidator.STRING],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.LIST,
                                               FieldValidator.STRING]
                                          ]):

                                # Format: [file tags identifier]
                                data.append(
                                    self.item_class({
                                        'filename': row[0],
                                        'tags': row[1],
                                        'identifier': row[2]
                                    })
                                )

                            elif validate(row_format=row_format,
                                          valid_formats=[
                                              [FieldValidator.AUDIOFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.LIST],
                                              [FieldValidator.DATAFILE,
                                               FieldValidator.STRING,
                                               FieldValidator.NUMBER,
                                               FieldValidator.NUMBER,
                                               FieldValidator.LIST]
                                          ]):

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
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File not found [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
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

        if self.format in [FileFormat.TXT, FileFormat.ANN]:
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

    def filter(self,
               filename=None,
               file_list=None,
               scene_label=None,
               scene_list=None,
               event_label=None,
               event_list=None,
               tag=None,
               tag_list=None,
               identifier=None,
               identifier_list=None,
               source_label=None,
               source_label_list=None,
               **kwargs
               ):
        """Filter content

        Parameters
        ----------
        filename : str, optional
            Filename to be matched
            Default value None

        file_list : list, optional
            List of filenames to be matched
            Default value None

        scene_label : str, optional
            Scene label to be matched
            Default value None

        scene_list : list of str, optional
            List of scene labels to be matched
            Default value None

        event_label : str, optional
            Event label to be matched
            Default value None

        event_list : list of str, optional
            List of event labels to be matched
            Default value None

        tag : str, optional
            Tag to be matched
            Default value None

        tag_list : list of str, optional
            List of tags to be matched
            Default value None

        identifier : str, optional
            Identifier to be matched
            Default value None

        identifier_list : list of str, optional
            List of identifiers to be matched
            Default value None

        source_label : str, optional
            Source label to be matched
            Default value None

        source_label_list : list of str, optional
            List of source labels to be matched
            Default value None

        Returns
        -------
        MetaDataContainer

        """

        # Inject parameters back to kwargs, and use parent filter method
        if filename is not None:
            kwargs['filename'] = filename

        if scene_label is not None:
            kwargs['scene_label'] = scene_label

        if event_label is not None:
            kwargs['event_label'] = event_label

        if identifier is not None:
            kwargs['identifier'] = identifier

        if source_label is not None:
            kwargs['source_label'] = source_label

        if file_list is not None:
            kwargs['filename'] = list(file_list)

        if scene_list is not None:
            kwargs['scene_label'] = list(scene_list)

        if event_list is not None:
            kwargs['event_label'] = list(event_list)

        if identifier_list is not None:
            kwargs['identifier'] = list(identifier_list)

        if source_label_list is not None:
            kwargs['source_label'] = list(source_label_list)

        result = MetaDataContainer(super(MetaDataContainer, self).filter(**kwargs))

        # Handle tags separately
        if tag is not None or tag_list is not None:
            data = []

            if tag_list:
                tag_list = set(tag_list)

            for item in result:
                matched = []
                if tag:
                    if item.tags and tag in item.tags:
                        matched.append(True)
                    else:
                        matched.append(False)

                if tag_list:
                    if item.tags and tag_list.intersection(item.tags):
                        matched.append(True)
                    else:
                        matched.append(False)

                if all(matched):
                    data.append(copy.deepcopy(item))

            return MetaDataContainer(data)

        else:
            return result

    def process_events(self, minimum_event_length=None, minimum_event_gap=None):
        """Process event content

        Makes sure that minimum event length and minimum event gap conditions are met per event label class.

        Parameters
        ----------
        minimum_event_length : float > 0.0
            Minimum event length in seconds, shorten than given are filtered out from the output.
            Default value None

        minimum_event_gap : float > 0.0
            Minimum allowed gap between events in seconds from same event label class.
            Default value None

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

    def map_events(self, target_event_label, source_event_labels=None):
        """Map events with varying event labels into single target event label

        Parameters
        ----------
        target_event_label : str
            Target event label

        source_event_labels : list of str
            Event labels to be processed. If none given, all events are merged
            Default value None

        Returns
        -------
        MetaDataContainer

        """

        processed_events = MetaDataContainer()
        files = self.unique_files
        if not files:
            files = [None]

        if source_event_labels is None:
            source_event_labels = self.unique_event_labels

        for filename in files:
            for event_label in source_event_labels:
                current_events_items = self.filter(filename=filename, event_label=event_label)

                # Sort events
                current_events_items = sorted(current_events_items, key=lambda k: k.onset)

                for item in current_events_items:
                    item.event_label = target_event_label

                processed_events += current_events_items

        return processed_events

    def event_inactivity(self, event_label='inactivity', source_event_labels=None, duration_list=None):
        """Get inactivity segments between events as event list

        Parameters
        ----------
        event_label : str
            Event label used for inactivity

        source_event_labels : list of str
            Event labels to be taken into account. If none given, all events are considered.
            Default value None

        duration_list : dict
            Dictionary where filename is a key and value is the total duration of the file.
            If none given, max event offset is used to get file length.
            Default value None

        Returns
        -------
        MetaDataContainer

        """

        meta_flatten = self.map_events(target_event_label='activity', source_event_labels=source_event_labels)
        meta_flatten = meta_flatten.process_events(
            minimum_event_gap=numpy.spacing(1),
            minimum_event_length=numpy.spacing(1)
        )

        inactivity_events = MetaDataContainer()
        files = meta_flatten.unique_files
        if not files:
            files = [None]

        if duration_list is None:
            duration_list = {}

        for filename in files:
            current_events_items = meta_flatten.filter(filename=filename)
            current_inactivity_events = MetaDataContainer()
            onset = 0.0
            for item in current_events_items:
                current_onset = onset
                current_offset = item.onset

                current_inactivity_events.append(
                    {
                        'filename': filename,
                        'onset': current_onset,
                        'offset': current_offset,
                        'event_label': event_label
                    }
                )

                onset = item.offset

            if filename in duration_list:
                file_duration = duration_list[filename]
            else:
                file_duration = current_events_items.max_offset

            current_inactivity_events.append(
                {
                    'filename': filename,
                    'onset': onset,
                    'offset': file_duration,
                    'event_label': event_label
                }
            )

            current_inactivity_events = current_inactivity_events.process_events(
                minimum_event_gap=numpy.spacing(1),
                minimum_event_length=numpy.spacing(1)
            )

            current_inactivity_events = sorted(current_inactivity_events, key=lambda k: k.onset)

            inactivity_events += current_inactivity_events

        return inactivity_events

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
            Default value None

        stop : float > 0.0
            Segment end, seconds
            Default value None

        duration : float
            Segment duration, seconds
            Default value None

        filename : str
            Filename to filter
            Default value None

        zero_time : bool
            Convert timestamps in respect to the segment start
            Default value True

        trim : bool
            Trim event onsets and offset according to segment start and stop times.
            Default value True

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
            Default value None

        scene_label_list : list of str
            List of scene labels to be included in the statistics. If none given, all unique labels used
            Default value None

        tag_list : list of str
            List of tags to be included in the statistics. If none given, all unique tags used
            Default value None

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
        scene_unique_identifiers = numpy.zeros(len(scene_label_list))
        for scene_id, scene_label in enumerate(scene_label_list):
            scene_data = self.filter(scene_label=scene_label)
            scene_counts[scene_id] = len(scene_data)
            scene_unique_identifiers[scene_id] = len(scene_data.unique_identifiers)

        event_lengths = numpy.zeros(len(event_label_list))
        event_counts = numpy.zeros(len(event_label_list))

        for event_id, event_label in enumerate(event_label_list):
            for item in self:
                if item.onset is not None and item.offset is not None and item.event_label == event_label:
                    event_lengths[event_id] += item.offset - item.onset
                if item.event_label == event_label:
                    event_counts[event_id] += 1

        tag_counts = numpy.zeros(len(tag_list))
        for tag_id, tag in enumerate(tag_list):
            for item in self:
                if item.tags and tag in item.tags:
                    tag_counts[tag_id] += 1

        return {
            'scenes': {
                'scene_label_list': scene_label_list,
                'count': scene_counts,
                'identifiers': scene_unique_identifiers
            },
            'events': {
                'event_label_list': event_label_list,
                'length': event_lengths,
                'count': event_counts,
                'avg_length': event_lengths/(event_counts + numpy.spacing(1))
            },
            'tags': {
                'tag_list': tag_list,
                'count': tag_counts
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
            Default value None

        time_resolution : float > 0.0
            Time resolution used when converting event into event roll.
            Default value 0.01

        label : str
            Meta data field used to create event roll
            Default value 'event_label'

        length_seconds : float
            Event roll length in seconds
            Default value None

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

    def intersection(self, second_metadata):
        """Intersection of two meta containers

        Parameters
        ----------

        second_metadata : MetaDataContainer
            Second meta data container

        Returns
        -------
        MetaDataContainer
            Container with intersecting items

        """

        # Get unique IDs for current meta data container
        id1 = []
        for item1 in self:
            id1.append(item1.id)

        # Get unique IDs for second meta data container
        id2 = []
        for item2 in second_metadata:
            id2.append(item2.id)

        # Find intersection of IDs
        id_intersect = list(set(id1).intersection(set(id2)))

        # Collect intersecting items
        intersection = MetaDataContainer()
        for id in id_intersect:
            intersection.append(self[id1.index(id)])

        return intersection

    def intersection_report(self, second_metadata):
        """Intersection report for two meta containers

        Parameters
        ----------

        second_metadata : MetaDataContainer
            Second meta data container

        Returns
        -------
        dict
            Dict with intersection data ['items', 'files', 'identifiers', 'scene_labels', 'event_labels' ,'tags']

        """

        return {
            'items': self.intersection(second_metadata=second_metadata),
            'files': list(set(self.unique_files).intersection(set(second_metadata.unique_files))),
            'identifiers': list(set(self.unique_identifiers).intersection(set(second_metadata.unique_identifiers))),
            'scene_labels': list(set(self.unique_scene_labels).intersection(set(second_metadata.unique_scene_labels))),
            'event_labels': list(set(self.unique_event_labels).intersection(set(second_metadata.unique_event_labels))),
            'tags': list(set(self.unique_tags).intersection(set(second_metadata.unique_tags)))
        }

    def difference(self, second_metadata):
        """Difference of two meta containers

        Parameters
        ----------

        second_metadata : MetaDataContainer
            Second meta data container

        Returns
        -------
        MetaDataContainer
            Container with difference items

        """

        # Get unique IDs for current meta data container
        id1 = []
        for item1 in self:
            id1.append(item1.id)

        # Get unique IDs for second meta data container
        id2 = []
        for item2 in second_metadata:
            id2.append(item2.id)

        # Find difference of IDs
        id_difference = list(set(id1).symmetric_difference(set(id2)))

        # Collect difference items
        difference = MetaDataContainer()
        for id in id_difference:
            difference.append(self[id1.index(id)])

        return difference

    def push_processing_chain_item(self, processor_name, init_parameters=None, process_parameters=None,
                                   preprocessing_callbacks=None,
                                   input_type=None, output_type=None):
        """Push processing chain item

        Parameters
        ----------
        processor_name : str
            Processor name

        init_parameters : dict, optional
            Initialization parameters for the processors
            Default value None

        process_parameters : dict, optional
            Parameters for the process method of the Processor
            Default value None

        preprocessing_callbacks : list of dicts
            Callbacks used for preprocessing
            Default value None

        input_type : ProcessingChainItemType
            Input data type
            Default value None

        output_type : ProcessingChainItemType
            Output data type
            Default value None

        Returns
        -------
        self

        """

        self.processing_chain.push_processor(
            processor_name=processor_name,
            init_parameters=init_parameters,
            process_parameters=process_parameters,
            preprocessing_callbacks=preprocessing_callbacks,
            input_type=input_type,
            output_type=output_type,
        )

        return self
