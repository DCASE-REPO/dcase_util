#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os
import logging
from dcase_util.utils import setup_logging


class Serializer(object):
    """Data serialization class"""
    @classmethod
    def logger(cls):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        return logger

    @classmethod
    def file_exists(cls, filename):
        """File exists

        Parameters
        ----------
        filename : str
            Filename path

        Raises
        ------
        IOError
            File does not exists.

        """

        if not os.path.isfile(filename):
            message = '{name}: File does not exists [{filename}].'.format(
                name=cls.__class__.__name__,
                filename=filename
            )

            cls.logger().exception(message)
            raise IOError(message)

    @classmethod
    def load_yaml(cls, filename):
        """Load YAML file

        Parameters
        ----------
        filename : str
            Filename path

        Returns
        -------
        data

        """

        cls.file_exists(filename=filename)

        try:
            import yaml

        except ImportError:
            message = '{name}: Unable to import YAML module. You can install it with `pip install pyyaml`.'.format(name=cls.__class__.__name__)
            cls.logger().exception(message)
            raise ImportError(message)

        try:
            with open(filename, 'r') as infile:
                return yaml.load(infile, Loader=yaml.FullLoader)

        except yaml.YAMLError as exc:
            cls.logger().error("Error while parsing YAML file [{file}]".format(file=filename))
            if hasattr(exc, 'problem_mark'):
                if exc.context is not None:
                    cls.logger().error(str(exc.problem_mark) + '\n  ' + str(exc.problem) + ' ' + str(exc.context))
                    cls.logger().error('  Please correct data and retry.')

                else:
                    cls.logger().error(str(exc.problem_mark) + '\n  ' + str(exc.problem))
                    cls.logger().error('  Please correct data and retry.')

            else:
                cls.logger().error("Something went wrong while parsing yaml file [{file}]".format(file=filename))

            return

    @classmethod
    def load_cpickle(cls, filename):
        """Load CPICKLE file

        Parameters
        ----------
        filename : str
            Filename path

        Returns
        -------
        data

        """

        cls.file_exists(filename=filename)

        try:
            import cPickle as pickle

        except ImportError:
            try:
                import pickle

            except ImportError:
                message = '{name}: Unable to import pickle module.'.format(
                    name=cls.__class__.__name__
                )

                cls.logger().exception(message)
                raise ImportError(message)

        return pickle.load(open(filename, "rb"))

    @classmethod
    def load_json(cls, filename):
        """Load JSON file

        Parameters
        ----------
        filename : str
            Filename path

        Returns
        -------
        data

        """

        cls.file_exists(filename=filename)

        try:
            import ujson as json

        except ImportError:
            try:
                import json

            except ImportError:
                message = '{name}: Unable to import json module. You can install it with `pip install ujson`.'.format(
                    name=cls.__class__.__name__
                )

                cls.logger().exception(message)
                raise ImportError(message)

        return json.load(open(filename, "r"))

    @classmethod
    def load_msgpack(cls, filename):
        """Load MSGPACK file

        Parameters
        ----------
        filename : str
            Filename path

        Returns
        -------
        data

        """

        cls.file_exists(filename=filename)

        try:
            import msgpack

        except ImportError:
            message = '{name}: Unable to import msgpack module. You can install it with `pip install msgpack-python`.'.format(
                name=cls.__class__.__name__
            )

            cls.logger().exception(message)
            raise ImportError(message)

        return msgpack.load(open(filename, "rb"), encoding='utf-8')

    @classmethod
    def load_marshal(cls, filename):
        """Load MARSHAL file

        Parameters
        ----------
        filename : str
            Filename path

        Returns
        -------
        data

        """

        cls.file_exists(filename=filename)

        try:
            import marshal

        except ImportError:
            message = '{name}: Unable to import marshal module. You can install it with `pip install pymarshal`.'.format(
                name=cls.__class__.__name__
            )

            cls.logger().exception(message)
            raise ImportError(message)

        return marshal.load(open(filename, "rb"))

    @classmethod
    def save_yaml(cls, filename, data):
        """Save data into YAML file

        Parameters
        ----------
        filename : str
            Filename path

        data :
            Data to be stored

        Returns
        -------
        None

        """

        try:
            import yaml

        except ImportError:
            message = '{name}: Unable to import yaml module. You can install it with `pip install pyyaml`.'.format(
                name=cls.__class__.__name__
            )

            cls.logger().exception(message)
            raise ImportError(message)

        with open(filename, 'w') as outfile:
            outfile.write(yaml.dump(data, default_flow_style=False))

    @classmethod
    def save_cpickle(cls, filename, data):
        """Save data into CPICKLE file

        Parameters
        ----------
        filename : str
            Filename path

        data :
            Data to be stored

        Returns
        -------
        None

        """

        try:
            import cPickle as pickle

        except ImportError:
            try:
                import pickle

            except ImportError:
                message = '{name}: Unable to import pickle module.'.format(
                    name=cls.__class__.__name__
                )

                cls.logger().exception(message)
                raise ImportError(message)

        pickle.dump(data, open(filename, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def save_json(cls, filename, data):
        """Save data into JSON file

        Parameters
        ----------
        filename : str
            Filename path

        data :
            Data to be stored

        Returns
        -------
        None

        """

        try:
            import ujson as json

        except ImportError:
            try:
                import json

            except ImportError:
                message = '{name}: Unable to import json module. You can install it with `pip install ujson`.'.format(
                    name=cls.__class__.__name__
                )

                cls.logger().exception(message)
                raise ImportError(message)

        json.dump(data, open(filename, 'w'))

    @classmethod
    def save_msgpack(cls, filename, data):
        """Save data into MSGPACK file

        Parameters
        ----------
        filename : str
            Filename path

        data :
            Data to be stored

        Returns
        -------
        None

        """

        try:
            import msgpack

        except ImportError:
            message = '{name}: Unable to import msgpack module. You can install it with `pip install msgpack-python`.'.format(
                name=cls.__class__.__name__
            )

            cls.logger().exception(message)
            raise ImportError(message)

        msgpack.dump(data, open(filename, 'wb'), use_bin_type=True)

    @classmethod
    def save_marshal(cls, filename, data):
        """Save data into MARSHAL file

        Parameters
        ----------
        filename : str
            Filename path

        data :
            Data to be stored

        Returns
        -------
        None

        """

        try:
            import marshal

        except ImportError:
            message = '{name}: Unable to import marshal module. You can install it with `pip install pymarshal`.'.format(
                name=cls.__class__.__name__
            )

            cls.logger().exception(message)
            raise ImportError(message)

        marshal.dump(data, open(filename, 'wb'))
