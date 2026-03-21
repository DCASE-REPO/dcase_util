""" Unit tests for FileFormat """
from dcase_util.utils import FileFormat

def test_FileMixin_formats():
    assert FileFormat.detect(filename='test.yaml') == FileFormat.YAML
    assert FileFormat.detect(filename='test.YAML') == FileFormat.YAML
    assert FileFormat.detect(filename='test.Yaml') == FileFormat.YAML
    assert FileFormat.detect(filename='test.xml') == FileFormat.XML
    assert FileFormat.detect(filename='test.json') == FileFormat.JSON
    assert FileFormat.detect(filename='test.cpickle') == FileFormat.CPICKLE
    assert FileFormat.detect(filename='test.pickle') == FileFormat.CPICKLE
    assert FileFormat.detect(filename='test.pkl') == FileFormat.CPICKLE
    assert FileFormat.detect(filename='test.marshal') == FileFormat.MARSHAL
    assert FileFormat.detect(filename='test.wav') == FileFormat.WAV
    assert FileFormat.detect(filename='test.flac') == FileFormat.FLAC
    assert FileFormat.detect(filename='test.mp3') == FileFormat.MP3
    assert FileFormat.detect(filename='test.m4a') == FileFormat.M4A
    assert FileFormat.detect(filename='test.txt') == FileFormat.TXT
    assert FileFormat.detect(filename='test.hash') == FileFormat.TXT
    assert FileFormat.detect(filename='test.webm') == FileFormat.WEBM
    assert FileFormat.detect(filename='test.tar') == FileFormat.TAR
    assert FileFormat.detect(filename='test.tar.gz') == FileFormat.TAR
    assert FileFormat.detect(filename='test.zip') == FileFormat.ZIP
    assert FileFormat.detect(filename='test.csv') == FileFormat.CSV
    assert FileFormat.detect(filename='test.ann') == FileFormat.ANN
