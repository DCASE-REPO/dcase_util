""" Unit tests for Mixin """
import dcase_util
from dcase_util.containers import FileMixin
from dcase_util.utils import FileFormat
import tempfile
import os

def test_FileMixin_formats():
    assert FileMixin(filename='test.yaml').detect_file_format().format == FileFormat.YAML
    assert FileMixin(filename='test.xml').detect_file_format().format == FileFormat.XML
    assert FileMixin(filename='test.json').detect_file_format().format == FileFormat.JSON
    assert FileMixin(filename='test.cpickle').detect_file_format().format == FileFormat.CPICKLE
    assert FileMixin(filename='test.pickle').detect_file_format().format == FileFormat.CPICKLE
    assert FileMixin(filename='test.pkl').detect_file_format().format == FileFormat.CPICKLE
    assert FileMixin(filename='test.marshal').detect_file_format().format == FileFormat.MARSHAL
    assert FileMixin(filename='test.wav').detect_file_format().format == FileFormat.WAV
    assert FileMixin(filename='test.flac').detect_file_format().format == FileFormat.FLAC
    assert FileMixin(filename='test.mp3').detect_file_format().format == FileFormat.MP3
    assert FileMixin(filename='test.m4a').detect_file_format().format == FileFormat.M4A
    assert FileMixin(filename='test.txt').detect_file_format().format == FileFormat.TXT
    assert FileMixin(filename='test.hash').detect_file_format().format == FileFormat.TXT
    assert FileMixin(filename='test.webm').detect_file_format().format == FileFormat.WEBM
    assert FileMixin(filename='test.tar').detect_file_format().format == FileFormat.TAR
    assert FileMixin(filename='test.tar.gz').detect_file_format().format == FileFormat.TAR
    assert FileMixin(filename='test.zip').detect_file_format().format == FileFormat.ZIP
    assert FileMixin(filename='test.csv').detect_file_format().format == FileFormat.CSV
    assert FileMixin(filename='test.ann').detect_file_format().format == FileFormat.ANN

    assert FileMixin(filename='test.zip').is_package() == True
    assert FileMixin(filename='test.tar').is_package() == True
    assert FileMixin(filename='test.tar.gz').is_package() == True
    assert FileMixin(filename='test.wav').is_package() == False

def test_FileMixin_delimiters():
    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('0.5' + delimiter + '0.7\n')
            tmp.write('2.5' + delimiter + '2.7\n')
            tmp.close()

            item = FileMixin(filename=tmp.name)
            assert item.delimiter() == delimiter
        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

