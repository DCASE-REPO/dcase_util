""" Unit tests for FileFormat """

import nose.tools
from dcase_util.utils import FileFormat


def test_FileMixin_formats():
    nose.tools.eq_(FileFormat.detect(filename='test.yaml'), FileFormat.YAML)
    nose.tools.eq_(FileFormat.detect(filename='test.YAML'), FileFormat.YAML)
    nose.tools.eq_(FileFormat.detect(filename='test.Yaml'), FileFormat.YAML)
    nose.tools.eq_(FileFormat.detect(filename='test.xml'), FileFormat.XML)
    nose.tools.eq_(FileFormat.detect(filename='test.json'), FileFormat.JSON)
    nose.tools.eq_(FileFormat.detect(filename='test.cpickle'), FileFormat.CPICKLE)
    nose.tools.eq_(FileFormat.detect(filename='test.pickle'), FileFormat.CPICKLE)
    nose.tools.eq_(FileFormat.detect(filename='test.pkl'), FileFormat.CPICKLE)
    nose.tools.eq_(FileFormat.detect(filename='test.marshal'), FileFormat.MARSHAL)
    nose.tools.eq_(FileFormat.detect(filename='test.wav'), FileFormat.WAV)
    nose.tools.eq_(FileFormat.detect(filename='test.flac'), FileFormat.FLAC)
    nose.tools.eq_(FileFormat.detect(filename='test.mp3'), FileFormat.MP3)
    nose.tools.eq_(FileFormat.detect(filename='test.m4a'), FileFormat.M4A)
    nose.tools.eq_(FileFormat.detect(filename='test.txt'), FileFormat.TXT)
    nose.tools.eq_(FileFormat.detect(filename='test.hash'), FileFormat.TXT)
    nose.tools.eq_(FileFormat.detect(filename='test.webm'), FileFormat.WEBM)
    nose.tools.eq_(FileFormat.detect(filename='test.tar'), FileFormat.TAR)
    nose.tools.eq_(FileFormat.detect(filename='test.tar.gz'), FileFormat.TAR)
    nose.tools.eq_(FileFormat.detect(filename='test.zip'), FileFormat.ZIP)
    nose.tools.eq_(FileFormat.detect(filename='test.csv'), FileFormat.CSV)
    nose.tools.eq_(FileFormat.detect(filename='test.ann'), FileFormat.ANN)
