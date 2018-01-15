#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

from .files import FileFormat
import re


class FieldValidator(object):
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    ALPHA1 = 'ALPHA1'
    ALPHA2 = 'ALPHA2'
    FILE   = 'FILE'
    AUDIOFILE = 'AUDIOFILE'
    DATAFILE = 'DATAFILE'
    LIST = 'LIST'
    EMPTY = 'EMPTY'

    audio_file_extensions = [
        FileFormat.WAV,
        FileFormat.FLAC,
        FileFormat.MP3,
        FileFormat.AAC,
        FileFormat.AIFF,
        FileFormat.OGG,
        FileFormat.RAW
    ]

    data_file_extensions = [
        FileFormat.CPICKLE,
        FileFormat.NUMPY,
    ]

    @classmethod
    def process(cls, field):
        """Test field

        Parameters
        ----------
        field : str

        Returns
        -------
        str
            Field label [FieldValidator.AUDIOFILE, FieldValidator.NUMBER, FieldValidator.LIST, FieldValidator.ALPHA1, FieldValidator.ALPHA2, FieldValidator.STRING, FieldValidator.EMPTY]

        """

        field = field.strip()

        if cls.is_audiofile(field):
            return cls.AUDIOFILE

        elif cls.is_datafile(field):
            return cls.DATAFILE

        elif cls.is_number(field):
            return cls.NUMBER

        elif cls.is_list(field):
            return cls.LIST

        elif cls.is_alpha(field, length=1):
            return cls.ALPHA1

        elif cls.is_alpha(field, length=2):
            return cls.ALPHA2

        elif cls.is_empty(field):
            return cls.EMPTY

        else:
            return cls.STRING

    @classmethod
    def is_empty(cls, field):
        """Test for empty field

        Parameters
        ----------
        field : str

        Returns
        -------
        bool

        """

        if field == '' or field is None:
            return True

        else:
            return False

    @classmethod
    def is_number(cls, field):
        """Test for number field

        Parameters
        ----------
        field : str

        Returns
        -------
        bool

        """

        try:
            float(field.replace(',', '.'))  # for int, long and float

        except ValueError:
            try:
                complex(field.replace(',', '.'))  # for complex

            except ValueError:
                return False

        return True

    @classmethod
    def is_audiofile(cls, field):
        """Test for audio file field

        Parameters
        ----------
        field : str

        Returns
        -------
        bool

        """

        detected_format = FileFormat.detect(
            filename=field,
            use_content_for_unknown=False
        )

        if detected_format in cls.audio_file_extensions:
            return True

        else:
            return False

    @classmethod
    def is_datafile(cls, field):
        """Test for data file field

        Parameters
        ----------
        field : str

        Returns
        -------
        bool

        """

        detected_format = FileFormat.detect(
            filename=field,
            use_content_for_unknown=False
        )

        if detected_format in cls.data_file_extensions:
            return True

        else:
            return False


    @classmethod
    def is_list(cls, field):
        """Test for list field, valid delimiters [ : ; #]

        Parameters
        ----------
        field : str

        Returns
        -------
        bool

        """

        if len(re.split(r'[;|:|#"]+', field)) > 1:
            return True

        else:
            return False

    @classmethod
    def is_alpha(cls, field, length=1):
        """Test for alpha field with length 1

        Parameters
        ----------
        field : str
        length : int
            Length of field
            Default value 1

        Returns
        -------
        bool

        """
        if len(field) == length and field.isalpha():
            return True

        else:
            return False
