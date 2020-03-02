#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from six import iteritems
from builtins import str as text

import os
import sys
import numpy
import copy
import csv
import json
import hashlib

from dcase_util.containers import ContainerMixin, FileMixin
from dcase_util.ui import FancyStringifier, FancyHTMLStringifier
from dcase_util.utils import is_float, is_int, FileFormat


class ObjectContainer(ContainerMixin, FileMixin):
    """Container class for object inherited from standard object class."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        # Run ContainerMixin init
        ContainerMixin.__init__(self, *args, **kwargs)

        # Run FileMixin init
        FileMixin.__init__(self, *args, **kwargs)

        super(ObjectContainer, self).__init__(*args, **kwargs)

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

        if self.exists():
            from dcase_util.files import Serializer
            if self.format == FileFormat.CPICKLE:
                self.__dict__.update(Serializer.load_cpickle(filename=self.filename))

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
            data = self.__dict__

            # Check if before save function is defined, call if found
            if hasattr(self, '_before_save'):
                data = self._before_save(data)

            if self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=data)

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)  # Delete the file, since most likely it was not saved fully
            raise

        # Check if after save function is defined, call if found
        if hasattr(self, '_after_save'):
            self._after_save()

        return self


class DictContainer(dict, ContainerMixin, FileMixin):
    """Dictionary container class inherited from standard dict class."""
    valid_formats = [FileFormat.YAML, FileFormat.JSON, FileFormat.CPICKLE, FileFormat.MARSHAL, FileFormat.MSGPACK,
                     FileFormat.TXT, FileFormat.CSV, FileFormat.META]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        # Run ContainerMixin init
        ContainerMixin.__init__(self, *args, **kwargs)

        # Run FileMixin init
        FileMixin.__init__(self, *args, **kwargs)

        super(DictContainer, self).__init__(*args)

        self.non_hashable_fields = [
            '_hash',
            'verbose',
        ]

        if kwargs.get('non_hashable_fields'):
            self.non_hashable_fields.update(kwargs.get('non_hashable_fields'))

    def __getstate__(self):
        d = super(DictContainer, self).__getstate__()
        return d

    def __setstate__(self, d):
        super(DictContainer, self).__setstate__(d)

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

        output += self._walk_and_show(self, depth=0, ui=ui, indent=indent)

        return output

    def get_path(self, path, default=None, data=None):
        """Get value from nested dict with dotted path

        Parameters
        ----------
        path : str or list of str
            String in form of "field1.field2.field3"

        default : str, int, float
            Default value returned if path does not exists
            Default value None

        data : dict, optional
            Dict for which path search is done, if None given self is used. Used for recursive path search.
            Default value None

        Returns
        -------

        """

        if data is None:
            data = self

        if isinstance(path, list):
            fields = path

        elif isinstance(path, str):
            fields = path.split('.')

        else:
            message = '{name}: Unknown type of dotted_path [{path}].'.format(
                name=self.__class__.__name__,
                path=path
            )

            self.logger.exception(message)
            raise ValueError(message)

        if '*' == fields[0]:
            # Magic field to return all childes in a list
            sub_list = []
            for key, value in iteritems(data):
                if len(fields) > 1:
                    sub_list.append(
                        self.get_path(
                            data=value,
                            path='.'.join(fields[1:]),
                            default=default
                        )
                    )

                else:
                    sub_list.append(value)

            return sub_list

        else:
            if len(fields) > 1 and fields[0] in data:
                # Go deeper
                return self.get_path(
                    data=data[fields[0]],
                    path='.'.join(fields[1:]),
                    default=default
                )

            elif len(fields) == 1 and fields[0] in data:
                # We reached to the node
                if isinstance(data[fields[0]], dict):
                    # Return DictContainer in case of dict
                    return DictContainer(data[fields[0]])

                else:
                    return data[fields[0]]

            else:
                return default

    def set_path(self, path, new_value, data=None):
        """Set value in nested dict with dotted path

        Parameters
        ----------
        path : str or list of str
            String in form of "field1.field2.field3"

        new_value :
            new value to be placed

        data : dict, optional
            Dict for which path search is done, if None given self is used. Used for recursive path search.
            Default value None

        Returns
        -------
        None

        """

        if data is None:
            data = self

        if isinstance(path, list):
            fields = path

        elif isinstance(path, str):
            fields = path.split('.')

        else:
            message = '{name}: Unknown type of dotted_path [{path}].'.format(
                name=self.__class__.__name__,
                path=path
            )

            self.logger.exception(message)
            raise ValueError(message)

        if '*' == fields[0]:
            # Magic field to set all childes in a list
            for key, value in iteritems(data):
                if len(fields) > 1:
                    self.set_path(new_value=new_value, data=value, path='.'.join(fields[1:]))

                else:
                    data[key] = new_value

        else:
            if len(fields) == 1:
                # We reached to the node
                data[fields[0]] = new_value
            else:
                if fields[0] not in data:
                    data[fields[0]] = {}

                elif not isinstance(data[fields[0]], dict):
                    # Overwrite path
                    data[fields[0]] = {}

                self.set_path(new_value=new_value, data=data[fields[0]], path='.'.join(fields[1:]))

    def get_leaf_path_list(self, target_field=None, target_field_startswith=None, target_field_endswith=None):
        """Get path list to all leaf node in the nested dict.

        Parameters
        ----------
        target_field : str
            Field name to filter paths.
            Default value None

        target_field_startswith : str
            Start of field name to filter paths.
            Default value None

        target_field_endswith : str
            End of field name to filter paths.
            Default value None

        Returns
        -------
        list
            Path list

        """

        path_list = list(self._path_generator())
        dotted_paths = []
        for path in path_list:
            if target_field is not None and path[-1] == target_field:
                dotted_paths.append('.'.join(path))

            elif target_field_startswith is not None and path[-1].startswith(target_field_startswith):
                dotted_paths.append('.'.join(path))

            elif target_field_endswith is not None and path[-1].endswith(target_field_endswith):
                dotted_paths.append('.'.join(path))

            elif target_field is None and target_field_startswith is None and target_field_endswith is None:
                dotted_paths.append('.'.join(path))

        return sorted(dotted_paths)

    def merge(self, override, target=None):
        """ Recursive dict merge

        Parameters
        ----------
        override : dict
            override parameter dict

        target : dict
            target parameter dict
            Default value None

        Returns
        -------
        self

        """

        if not target:
            target = self

        for k, v in iteritems(override):
            if k in target and isinstance(target[k], dict) and isinstance(override[k], dict):
                self.merge(target=target[k], override=override[k])

            else:
                target[k] = override[k]

        return self

    def get_hash_for_path(self, dotted_path=None):
        """ Get unique hash string for the data under given path.

        Parameters
        ----------
        dotted_path : str or list
            target path
            Default value None

        Returns
        -------
        str
            Unique hash for parameter dict

        """

        if dotted_path:
            data = self.get_path(path=dotted_path)
            if data is not None:
                return self.get_hash(data)

            else:
                return None

        else:
            return self.get_hash(self)

    def get_hash(self, data=None):
        """Get unique hash string (md5) for given parameter dict.

        Parameters
        ----------
        data : dict or list
            Input parameters
            Default value None

        Returns
        -------
        str
            Unique hash for parameter dict

        """

        if data is None:
            data = dict(self)

        md5 = hashlib.md5()
        md5.update(str(json.dumps(self._clean_for_hashing(copy.deepcopy(data)), sort_keys=True)).encode('utf-8'))

        return md5.hexdigest()

    def load(self, filename=None, file_format=None):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path, if None given, filename given to class constructor is used.
            Default value None

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

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
            if not file_format:
                self.detect_file_format()
                self.validate_format()

        if file_format and FileFormat.validate_label(label=file_format):
            self.format = file_format

        if self.exists():
            # File exits
            from dcase_util.files import Serializer
            dict.clear(self)

            if self.format == FileFormat.YAML or self.format == FileFormat.META:
                data = Serializer.load_yaml(filename=self.filename)
                dict.update(self, data)

            elif self.format == FileFormat.CPICKLE:
                dict.update(self, Serializer.load_cpickle(filename=self.filename))

            elif self.format == FileFormat.MARSHAL:
                dict.update(self, Serializer.load_marshal(filename=self.filename))

            elif self.format == FileFormat.MSGPACK:
                dict.update(self, Serializer.load_msgpack(filename=self.filename))

            elif self.format == FileFormat.JSON:
                dict.update(self, Serializer.load_json(filename=self.filename))

            elif self.format == FileFormat.TXT:
                with open(self.filename, 'r') as f:
                    lines = f.readlines()
                    dict.update(self, dict(zip(range(0, len(lines)), lines)))

            elif self.format == FileFormat.CSV:
                data = {}
                delimiter = self.delimiter()
                with open(self.filename, 'r') as f:
                    csv_reader = csv.reader(f, delimiter=delimiter)
                    for row in csv_reader:
                        if len(row) == 2:
                            data[row[0]] = row[1]

                dict.update(self, data)

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        else:
            message = '{name}: File does not exists [{file}]'.format(name=self.__class__.__name__, file=self.filename)
            self.logger.exception(message)
            raise IOError(message)

        # Call __setstate__ to handle internal variables of the class
        self.__setstate__(d=self)

        # Check if after load function is defined, call if found
        if hasattr(self, '_after_load'):
            self._after_load()

        return self

    def save(self, filename=None, file_format=None):
        """Save file

        Parameters
        ----------
        filename : str, optional
            File path, if None given, filename given to class constructor is used.
            Default value None

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

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
            if not file_format:
                self.detect_file_format()
                self.validate_format()

        if file_format and FileFormat.validate_label(label=file_format):
            self.format = file_format

        if self.filename is None or self.filename == '':
            message = '{name}: Filename is empty [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        try:
            from dcase_util.files import Serializer
            data = dict(self)
            if hasattr(self, '__getstate__'):
                data.update(dict(self.__getstate__()))

            # Check if before save function is defined, call if found
            if hasattr(self, '_before_save'):
                data = self._before_save(data)

            if self.format == FileFormat.YAML:
                Serializer.save_yaml(filename=self.filename, data=self.get_dump_content(data=data))

            elif self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=data)

            elif self.format == FileFormat.MARSHAL:
                Serializer.save_marshal(filename=self.filename, data=data)

            elif self.format == FileFormat.MSGPACK:
                Serializer.save_msgpack(filename=self.filename, data=data)

            elif self.format == FileFormat.JSON:
                Serializer.save_json(filename=self.filename, data=data)

            elif self.format == FileFormat.TXT:
                with open(self.filename, "w") as text_file:
                    for line_id in self:
                        text_file.write(self[line_id])

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

    def get_dump_content(self, data):
        """Clean internal content for saving

        Numpy, DictContainer content is converted to standard types

        Parameters
        ----------
        data : dict

        Returns
        -------
        dict

        """

        if data:
            data = dict(data)
            for k, v in iteritems(data):
                if isinstance(v, numpy.generic):
                    data[k] = numpy.asscalar(v)

                elif isinstance(v, DictContainer):
                    data[k] = self.get_dump_content(data=dict(data[k]))

                elif isinstance(v, dict):
                    data[k] = self.get_dump_content(data=data[k])

            return data

    def _path_generator(self, data=None, current_path_list=None):
        if data is None:
            data = self

        current_path_list = current_path_list[:] if current_path_list else []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    # We have dict, let's go deeper
                    for d in self._path_generator(value, current_path_list + [key]):
                        yield d

                else:
                    # We have reached leaf
                    yield current_path_list + [key]

    def _walk_and_show(self, d, depth=0, ui=None, indent=0):
        """Recursive dict walk to get string of the content nicely formatted

        Parameters
        ----------
        d : dict
            Dict for walking

        depth : int
            Depth of walk, string is indented with this
            Default value 0

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

        output = u''
        indent_increase = 2

        for k, v in sorted(d.items(), key=lambda x: x[0]):
            k = text(k)
            if isinstance(v, dict):
                output += ui.data(field=k, value="dict (%d)" % len(v.keys()), indent=indent + depth * indent_increase) + '\n'
                output += self._walk_and_show(d=v, depth=depth + 1, ui=ui, indent=indent)

            else:
                if isinstance(v, numpy.ndarray):
                    # Numpy array or matrix
                    shape = v.shape
                    if len(shape) == 1:
                        output += ui.data(
                            field=k,
                            value="array (%d)" % (v.shape[0]),
                            indent=indent + depth * indent_increase
                        ) + '\n'

                    elif len(shape) == 2:
                        output += ui.data(
                            field=k,
                            value="matrix (%d, %d)" % (v.shape[0], v.shape[1]),
                            indent=indent + depth * indent_increase
                        ) + '\n'

                    elif len(shape) == 3:
                        output += ui.data(
                            field=k,
                            value="matrix (%d, %d, %d)" % (v.shape[0], v.shape[1], v.shape[2]),
                            indent=indent + depth * indent_increase
                        ) + '\n'

                    elif len(shape) == 4:
                        output += ui.data(
                            field=k,
                            value="matrix (%d, %d, %d, %d)" % (v.shape[0], v.shape[1], v.shape[2], v.shape[3]),
                            indent=indent + depth * indent_increase
                        ) + '\n'

                elif isinstance(v, list) and len(v) and isinstance(v[0], str):
                    output += ui.data(
                        field=k,
                        value="list (%d)" % len(v),
                        indent=indent + depth * indent_increase
                    ) + '\n'

                    for item_id, item in enumerate(v):
                        output += ui.data(
                            field='[' + text(item_id) + ']',
                            value=item,
                            indent=indent + (depth+1) * indent_increase
                        ) + '\n'

                elif isinstance(v, list) and len(v) and isinstance(v[0], numpy.ndarray):
                    # List of arrays
                    output += ui.data(
                        field=k,
                        value="list (%d)" % len(v),
                        indent=indent + depth * indent_increase
                    ) + '\n'

                    for item_id, item in enumerate(v):
                        if len(item.shape) == 1:
                            output += ui.data(
                                field='[' + text(item_id) + ']',
                                value="array (%d)" % (item.shape[0]),
                                indent=indent + (depth + 1) * indent_increase
                            ) + '\n'

                        elif len(item.shape) == 2:
                            output += ui.data(
                                field='[' + text(item_id) + ']',
                                value="matrix (%d, %d)" % (item.shape[0], item.shape[1]),
                                indent=indent + (depth + 1) * indent_increase
                            ) + '\n'

                        elif len(item.shape) == 3:
                            output += ui.data(
                                field='[' + text(item_id) + ']',
                                value="matrix (%d, %d, %d)" % (item.shape[0], item.shape[1], item.shape[2]),
                                indent=indent + (depth + 1) * indent_increase
                            ) + '\n'

                        elif len(item.shape) == 4:
                            output += ui.data(
                                field='[' + text(item_id) + ']',
                                value="matrix (%d, %d, %d, %d)" % (item.shape[0], item.shape[1], item.shape[2], item.shape[3]),
                                indent=indent + (depth + 1) * indent_increase
                            ) + '\n'

                elif isinstance(v, list) and len(v) and isinstance(v[0], dict):
                    output += ui.data(
                        field=k,
                        value="list (%d)" % len(v),
                        indent=indent + depth * indent_increase
                    ) + '\n'

                    for item_id, item in enumerate(v):
                        output += ui.data(
                            field='[' + text(item_id) + ']',
                            value='',
                            indent=indent + (depth + 1) * indent_increase
                        ) + '\n'

                        output += self._walk_and_show(d=item, depth=depth + 2, ui=ui, indent=indent)

                else:
                    output += ui.data(field=k, value=v, indent=indent + depth*indent_increase) + '\n'

        return output

    def _clean_for_hashing(self, data, non_hashable_fields=None):
        """Recursively remove keys with value set to False, or non hashable fields

        Parameters
        ----------
        data : dict
            Data to be processed

        non_hashable_fields : list
            List of fields to be removed.
            Default value None

        Returns
        -------
        str

        """

        if non_hashable_fields is None and hasattr(self, 'non_hashable_fields'):
            non_hashable_fields = self.non_hashable_fields

        elif non_hashable_fields is None:
            non_hashable_fields = []

        if data:
            if 'enable' in data and not data['enable']:
                return {
                    'enable': False,
                }

            else:
                if isinstance(data, dict):
                    for key in list(data.keys()):
                        value = data[key]
                        if isinstance(value, bool) and value is False:
                            # Remove fields marked False
                            del data[key]

                        elif key in non_hashable_fields:
                            # Remove fields marked in non_hashable_fields list
                            del data[key]

                        elif isinstance(value, dict):
                            if 'enable' in value and not value['enable']:
                                # Remove dict block which is disabled
                                del data[key]

                            else:
                                # Proceed recursively
                                data[key] = self._clean_for_hashing(value)

                        elif hasattr(value, 'get_config'):
                            data[key] = value.get_config()

                    return data

                else:
                    return data

        else:
            return data

    def filter(self, data=None, excluded_key_prefix='_'):
        """Filter nested dict

        Parameters
        ----------
        data : dict, optional
            Dict to filter, if None given self is used.
            Default value None

        excluded_key_prefix : str
            Key prefix to be excluded
            Default value '_'

        Returns
        -------
        DictContainer

        """

        if data is None:
            data = copy.deepcopy(self)

        for key in list(data.keys()):
            if isinstance(data[key], dict):
                data[key] = self.filter(
                    data=data[key],
                    excluded_key_prefix=excluded_key_prefix
                )

            else:
                if excluded_key_prefix and key.startswith(excluded_key_prefix):
                    del data[key]

        return data


class ListContainer(list, ContainerMixin, FileMixin):
    """List container class inherited from standard list class."""
    valid_formats = [FileFormat.TXT, FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path

        """

        # Run ContainerMixin init
        ContainerMixin.__init__(self, *args, **kwargs)

        # Run FileMixin init
        FileMixin.__init__(self, *args, **kwargs)

        # Run list init
        list.__init__(self, *args)

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

        for item_id, item in enumerate(self):
            output += ui.data(field='[' + str(item_id) + ']', value=str(item), indent=indent) + '\n'

        return output

    def __getstate__(self):
        return super(ListContainer, self).__getstate__()

    def __setstate__(self, d):
        super(ListContainer, self).__setstate__(d)

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

        list.__init__(self, data)

        return self

    def load(self, filename=None, headers=None, file_format=None):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path
            Default value filename given to class constructor.
            Default value None

        headers : list of str, optional
            List of column names.
            Default value None

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

        Raises
        ------
        IOError:
            File does not exists or has unknown file format

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

        if self.exists():
            from dcase_util.files import Serializer

            if self.format == FileFormat.TXT:
                with open(self.filename, 'r') as f:
                    lines = f.readlines()
                    # Remove line breaks
                    for i in range(0, len(lines)):
                        lines[i] = lines[i].replace('\r\n', '').replace('\n', '')

                    list.__init__(self, lines)

            elif self.format == FileFormat.CPICKLE:
                list.__init__(self, Serializer.load_cpickle(filename=self.filename))

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

    def save(self, filename=None, file_format=None):
        """Save file

        Parameters
        ----------
        filename : str, optional
            File path, if None given, filename given to class constructor is used.
            Default value None

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

        Raises
        ------
        IOError:
            File has unknown file format

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

        if self.filename is None or self.filename == '':
            message = '{name}: Filename is empty [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        try:
            from dcase_util.files import Serializer
            if self.format == FileFormat.TXT:
                with open(self.filename, "w") as text_file:
                    for line in self:
                        text_file.write(str(line)+'\n')

            elif self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=self)

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)            # Delete the file, since most likely it was not saved fully
            raise

        # Check if after save function is defined, call if found
        if hasattr(self, '_after_save'):
            self._after_save()

        return self

    def get_dump_content(self, data):
        """Clean internal content for saving

        Numpy, DictContainer content is converted to standard types

        Parameters
        ----------
        data : dict

        Returns
        -------
        dict

        """

        if data:
            data = dict(data)
            for k, v in iteritems(data):
                if isinstance(v, numpy.generic):
                    data[k] = numpy.asscalar(v)

                elif isinstance(v, DictContainer):
                    data[k] = self.get_dump_content(data=dict(data[k]))

                elif isinstance(v, dict):
                    data[k] = self.get_dump_content(data=data[k])

            return data


class ListDictContainer(ListContainer):
    """List of dictionaries container class inherited from standard list class."""
    valid_formats = [FileFormat.CSV, FileFormat.YAML, FileFormat.CPICKLE]  #: Valid file formats

    def __init__(self, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        filename : str, optional
            File path

        """

        # Run ContainerMixin init
        ContainerMixin.__init__(self, *args, **kwargs)

        # Run FileMixin init
        FileMixin.__init__(self, *args, **kwargs)

        # Run list init
        list.__init__(self, *args)

        # Convert list items to DictContainers
        for item_id, item in enumerate(self):
            self[item_id] = DictContainer(item)

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
            output += ui.data(field='filename', value=self.filename) + '\n'

        for item_id, item in enumerate(self):
            output += ui.line(field='[' + str(item_id) + ']', indent=indent) + '\n'
            output += DictContainer(item).to_string(ui=ui, indent=indent + 1) + '\n'

        return output

    def search(self, key, value):
        """Search in the list of dictionaries

        Parameters
        ----------
        key : str
            Dict key for the search

        value :
            Value for the key to match

        Returns
        -------
        dict or None

        """

        for element in self:
            if element.get(key) == value:
                return element

        return None

    def load(self, filename=None, fields=None, csv_header=True, file_format=None,
             delimiter=None, convert_numeric_fields=True):
        """Load file

        Parameters
        ----------
        filename : str, optional
            File path, if None given, filename given to class constructor is used.
            Default value None

        fields : list of str, optional
            List of column names
            Default value None

        csv_header : bool, optional
            Read field names from first line (header). Used only for CSV formatted files.
            Default value True

        file_format : FileFormat, optional
            Forced file format, use this when there is
            a miss-match between file extension and file format.
            Default value None

        delimiter : str, optional
            Forced data delimiter for csv format. If None given,
            automatic delimiter sniffer used. Use this when sniffer does not work.
            Default value None

        convert_numeric_fields : bool, optional
            Convert int and float fields to correct type.
            Default value True

        Raises
        ------
        IOError:
            File does not exists or has unknown file format

        ValueError:
            No fields or csv_header set for CSV formatted file.

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

        if self.exists():
            from dcase_util.files import Serializer

            if self.format == FileFormat.CSV:
                if fields is None and csv_header is None:
                    message = '{name}: Parameters fields or csv_header has to be set for CSV files.'.format(
                        name=self.__class__.__name__
                    )
                    self.logger.exception(message)
                    raise ValueError(message)

                data = []

                if not delimiter:
                    delimiter = self.delimiter()

                with open(self.filename, 'r') as f:
                    csv_reader = csv.reader(f, delimiter=delimiter)
                    if csv_header:
                        csv_fields = next(csv_reader)
                        if fields is None:
                            fields = csv_fields

                    for row in csv_reader:
                        if row:
                            if convert_numeric_fields:
                                for cell_id, cell_data in enumerate(row):
                                    if is_int(cell_data):
                                        row[cell_id] = int(cell_data)

                                    elif is_float(cell_data):
                                        row[cell_id] = float(cell_data)

                            data.append(dict(zip(fields, row)))

                list.__init__(self, data)

            elif self.format == FileFormat.YAML:
                data = Serializer.load_yaml(filename=self.filename)
                if isinstance(data, list):
                    list.__init__(self, data)

                else:
                    message = '{name}: YAML data is not in list format.'.format(name=self.__class__.__name__)
                    self.logger.exception(message)
                    raise ImportError(message)

            elif self.format == FileFormat.CPICKLE:
                list.__init__(self, Serializer.load_cpickle(filename=self.filename))

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

    def save(self, filename=None, fields=None, csv_header=True, file_format=None, delimiter=','):
        """Save file

        Parameters
        ----------
        filename : str, optional
            File path, if None given, filename given to class constructor is used.
            Default value None

        fields : list of str
            Fields in correct order, if none given all field in alphabetical order will be outputted
            Default value None

        csv_header : bool
            In case of CSV formatted file, first line will contain field names. Names are taken from fields parameter.
            Default value True

        file_format : FileFormat, optional
            Forced file format, use this when there is a miss-match between file extension and file format.
            Default value None

        delimiter : str
            Delimiter to be used when saving data
            Default value ','

        Raises
        ------
        IOError:
            File has unknown file format

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

        if self.filename is None or self.filename == '':
            message = '{name}: Filename is empty [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        try:
            from dcase_util.files import Serializer

            if self.format == FileFormat.YAML:
                data = copy.deepcopy(list(self))
                for item_id, item in enumerate(data):
                    data[item_id] = self.get_dump_content(data=item)

                    Serializer.save_yaml(filename=self.filename, data=data)

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
                            item_values.append(item[field])

                        csv_writer.writerow(item_values)

                finally:
                    csv_file.close()

            elif self.format == FileFormat.CPICKLE:
                Serializer.save_cpickle(filename=self.filename, data=self)

            else:
                message = '{name}: Unknown format [{format}]'.format(name=self.__class__.__name__, format=self.filename)
                self.logger.exception(message)
                raise IOError(message)

        except KeyboardInterrupt:
            os.remove(self.filename)            # Delete the file, since most likely it was not saved fully
            raise

        # Check if after save function is defined, call if found
        if hasattr(self, '_after_save'):
            self._after_save()

        return self

    def get_field(self, field_name, skip_items_without_field=True):
        """Get all data from field.

        Parameters
        ----------
        field_name : str
            Dict key for the search

        skip_items_without_field : bool
            Skip items without field, if true None inserted to the output.
            Default value True

        Returns
        -------
        list

        """

        data = []
        for item in self:
            if field_name in item:
                data.append(item[field_name])

            elif not skip_items_without_field:
                data.append(None)

        return data

    def get_field_unique(self, field_name):
        """Get unique data from field.

        Parameters
        ----------
        field_name : str
            Dict key for the search

        Returns
        -------
        list

        """

        all_values = self.get_field(field_name=field_name)

        return sorted(list(set(all_values)))

    def remove_field(self, field_name):
        """Remove field from data items

        Parameters
        ----------
        field_name : str
            Field name

        Returns
        -------
        self

        """

        for item in self:
            if field_name in item:
                del item[field_name]

        return self

    def filter(self, case_insensitive_fields=True, **kwargs):
        """Filter content based on field values.

        Parameters
        ----------
        case_insensitive_fields : bool
            Use case insensitive fields for filtering
            Default value True

        kwargs
            Use filtered field name and parameter name, and target value for the field as parameter value.
            Underscore is parameter name is replace with whitespace when matching with field names.
            If value can be a single value or list of values.

        Returns
        -------
        ListDictContainer

        """

        filter_fields = {}
        for field in kwargs:
            if case_insensitive_fields:
                filter_fields[field.lower()] = kwargs[field]

            else:
                filter_fields[field] = kwargs[field]

        data = []

        for item in self:
            matched = []
            item_field_list = list(item.keys())
            item_field_map = {}
            for field in item_field_list:
                if case_insensitive_fields:
                    item_field_map[field.lower()] = field

                else:
                    item_field_map[field] = field

            for condition_field in filter_fields:
                condition_field_alternative = condition_field.replace('_', ' ')
                if condition_field in item_field_map:
                    if isinstance(filter_fields[condition_field], list):
                        if item[item_field_map[condition_field]] in filter_fields[condition_field]:
                            matched.append(True)

                        else:
                            matched.append(False)

                    else:
                        if item[item_field_map[condition_field]] == filter_fields[condition_field]:
                            matched.append(True)

                        else:
                            matched.append(False)

                elif condition_field_alternative in item_field_map:
                    if isinstance(filter_fields[condition_field], list):
                        if item[item_field_map[condition_field_alternative]] in filter_fields[condition_field]:
                            matched.append(True)

                        else:
                            matched.append(False)

                    else:
                        if item[item_field_map[condition_field_alternative]] == filter_fields[condition_field]:
                            matched.append(True)

                        else:
                            matched.append(False)

            if all(matched):
                data.append(copy.deepcopy(item))

        return ListDictContainer(data)


class RepositoryContainer(DictContainer):
    """Container class for repository, inherited from DictContainer."""
    valid_formats = [FileFormat.CPICKLE]  #: Valid file formats


class TextContainer(ListContainer):
    """Container class for text, inherited from ListContainer."""
    valid_formats = [FileFormat.TXT]  #: Valid file formats


