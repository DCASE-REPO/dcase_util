""" Unit tests for Mixin """

import nose.tools
import dcase_util
from dcase_util.containers import FileMixin
from dcase_util.utils import FileFormat
from nose.tools import *
import tempfile
import os


def test_FileMixin_formats():
    nose.tools.eq_(FileMixin(filename='test.yaml').detect_file_format().format, FileFormat.YAML)
    nose.tools.eq_(FileMixin(filename='test.xml').detect_file_format().format, FileFormat.XML)
    nose.tools.eq_(FileMixin(filename='test.json').detect_file_format().format, FileFormat.JSON)
    nose.tools.eq_(FileMixin(filename='test.cpickle').detect_file_format().format, FileFormat.CPICKLE)
    nose.tools.eq_(FileMixin(filename='test.pickle').detect_file_format().format, FileFormat.CPICKLE)
    nose.tools.eq_(FileMixin(filename='test.pkl').detect_file_format().format, FileFormat.CPICKLE)
    nose.tools.eq_(FileMixin(filename='test.marshal').detect_file_format().format, FileFormat.MARSHAL)
    nose.tools.eq_(FileMixin(filename='test.wav').detect_file_format().format, FileFormat.WAV)
    nose.tools.eq_(FileMixin(filename='test.flac').detect_file_format().format, FileFormat.FLAC)
    nose.tools.eq_(FileMixin(filename='test.mp3').detect_file_format().format, FileFormat.MP3)
    nose.tools.eq_(FileMixin(filename='test.m4a').detect_file_format().format, FileFormat.M4A)
    nose.tools.eq_(FileMixin(filename='test.txt').detect_file_format().format, FileFormat.TXT)
    nose.tools.eq_(FileMixin(filename='test.hash').detect_file_format().format, FileFormat.TXT)
    nose.tools.eq_(FileMixin(filename='test.webm').detect_file_format().format, FileFormat.WEBM)
    nose.tools.eq_(FileMixin(filename='test.tar').detect_file_format().format, FileFormat.TAR)
    nose.tools.eq_(FileMixin(filename='test.tar.gz').detect_file_format().format, FileFormat.TAR)
    nose.tools.eq_(FileMixin(filename='test.zip').detect_file_format().format, FileFormat.ZIP)
    nose.tools.eq_(FileMixin(filename='test.csv').detect_file_format().format, FileFormat.CSV)
    nose.tools.eq_(FileMixin(filename='test.ann').detect_file_format().format, FileFormat.ANN)

    nose.tools.eq_(FileMixin(filename='test.zip').is_package(), True)
    nose.tools.eq_(FileMixin(filename='test.tar').is_package(), True)
    nose.tools.eq_(FileMixin(filename='test.tar.gz').is_package(), True)
    nose.tools.eq_(FileMixin(filename='test.wav').is_package(), False)


def test_FileMixin_delimiters():
    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('0.5' + delimiter + '0.7\n')
            tmp.write('2.5' + delimiter + '2.7\n')
            tmp.close()

            item = FileMixin(filename=tmp.name)
            nose.tools.eq_(item.delimiter(), delimiter)
        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

