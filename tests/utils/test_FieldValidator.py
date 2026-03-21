""" Unit tests for FieldValidator """
import dcase_util

def test_process():
    validator = dcase_util.utils.FieldValidator

    assert validator.process(field='text') == validator.STRING
    assert validator.process(field='text123') == validator.STRING
    assert validator.process(field='122text12') == validator.STRING

    assert validator.process(field='t') == validator.ALPHA1
    assert validator.process(field='T') == validator.ALPHA1

    assert validator.process(field='Te') == validator.ALPHA2
    assert validator.process(field='tE') == validator.ALPHA2

    assert validator.process(field='audio.wav') == validator.AUDIOFILE
    assert validator.process(field='path/audio.wav') == validator.AUDIOFILE
    assert validator.process(field='path/path/audio.wav') == validator.AUDIOFILE
    assert validator.process(field='path/path/audio.flac') == validator.AUDIOFILE
    assert validator.process(field='path/path/audio.mp3') == validator.AUDIOFILE

    assert validator.process(field='0') == validator.NUMBER
    assert validator.process(field='1') == validator.NUMBER
    assert validator.process(field='12') == validator.NUMBER
    assert validator.process(field='123') == validator.NUMBER
    assert validator.process(field='12.2') == validator.NUMBER
    assert validator.process(field='0.01') == validator.NUMBER
    assert validator.process(field='-1.2') == validator.NUMBER

    assert validator.process(field='item1;item2') == validator.LIST
    assert validator.process(field='item1:item2') == validator.LIST
    assert validator.process(field='item1#item2') == validator.LIST

    assert validator.process(field='') == validator.EMPTY

def test_is_number():
    validator = dcase_util.utils.FieldValidator
    # is_number
    assert validator.is_number('0.1') == True
    assert validator.is_number('-2.1') == True
    assert validator.is_number('123') == True
    assert validator.is_number('-123') == True
    assert validator.is_number('0') == True

    assert validator.is_number('A') == False
    assert validator.is_number('A123') == False
    assert validator.is_number('A 123') == False
    assert validator.is_number('AabbCc') == False
    assert validator.is_number('A.2') == False

def test_is_audiofile():
    validator = dcase_util.utils.FieldValidator
    # is_audiofile
    assert validator.is_audiofile('audio.wav') == True
    assert validator.is_audiofile('audio.mp3') == True
    assert validator.is_audiofile('audio.flac') == True
    assert validator.is_audiofile('audio.raw') == True
    assert validator.is_audiofile('path/path/audio.flac') == True

    assert validator.is_audiofile('audio') == False
    assert validator.is_audiofile('123') == False
    assert validator.is_audiofile('54534.232') == False

def test_is_list():
    validator = dcase_util.utils.FieldValidator
    # is_list
    assert validator.is_list('test#') == True
    assert validator.is_list('test#test') == True
    assert validator.is_list('test:test') == True

    assert validator.is_list('test') == False
    assert validator.is_list('test-test') == False
    assert validator.is_list('12342.0') == False

def test_is_alpha():
    validator = dcase_util.utils.FieldValidator
    # is_alpha
    assert validator.is_alpha('a', length=1) == True
    assert validator.is_alpha('aa', length=2) == True
    assert validator.is_alpha('aaa', length=3) == True

    assert validator.is_alpha('aaa', length=1) == False
    assert validator.is_alpha('aa', length=1) == False
    assert validator.is_alpha('aaa', length=2) == False

    assert validator.is_alpha('1', length=1) == False
