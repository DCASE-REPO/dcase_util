""" Unit tests for FieldValidator """

import nose.tools
import dcase_util


def test_process():
    validator = dcase_util.utils.FieldValidator

    nose.tools.eq_(validator.process(field='text'), validator.STRING)
    nose.tools.eq_(validator.process(field='text123'), validator.STRING)
    nose.tools.eq_(validator.process(field='122text12'), validator.STRING)

    nose.tools.eq_(validator.process(field='t'), validator.ALPHA1)
    nose.tools.eq_(validator.process(field='T'), validator.ALPHA1)

    nose.tools.eq_(validator.process(field='Te'), validator.ALPHA2)
    nose.tools.eq_(validator.process(field='tE'), validator.ALPHA2)

    nose.tools.eq_(validator.process(field='audio.wav'), validator.AUDIOFILE)
    nose.tools.eq_(validator.process(field='path/audio.wav'), validator.AUDIOFILE)
    nose.tools.eq_(validator.process(field='path/path/audio.wav'), validator.AUDIOFILE)
    nose.tools.eq_(validator.process(field='path/path/audio.flac'), validator.AUDIOFILE)
    nose.tools.eq_(validator.process(field='path/path/audio.mp3'), validator.AUDIOFILE)

    nose.tools.eq_(validator.process(field='0'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='1'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='12'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='123'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='12.2'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='0.01'), validator.NUMBER)
    nose.tools.eq_(validator.process(field='-1.2'), validator.NUMBER)

    nose.tools.eq_(validator.process(field='item1;item2'), validator.LIST)
    nose.tools.eq_(validator.process(field='item1:item2'), validator.LIST)
    nose.tools.eq_(validator.process(field='item1#item2'), validator.LIST)

    nose.tools.eq_(validator.process(field=''), validator.EMPTY)


def test_is_number():
    validator = dcase_util.utils.FieldValidator
    # is_number
    nose.tools.eq_(validator.is_number('0.1'), True)
    nose.tools.eq_(validator.is_number('-2.1'), True)
    nose.tools.eq_(validator.is_number('123'), True)
    nose.tools.eq_(validator.is_number('-123'), True)
    nose.tools.eq_(validator.is_number('0'), True)

    nose.tools.eq_(validator.is_number('A'), False)
    nose.tools.eq_(validator.is_number('A123'), False)
    nose.tools.eq_(validator.is_number('A 123'), False)
    nose.tools.eq_(validator.is_number('AabbCc'), False)
    nose.tools.eq_(validator.is_number('A.2'), False)


def test_is_audiofile():
    validator = dcase_util.utils.FieldValidator
    # is_audiofile
    nose.tools.eq_(validator.is_audiofile('audio.wav'), True)
    nose.tools.eq_(validator.is_audiofile('audio.mp3'), True)
    nose.tools.eq_(validator.is_audiofile('audio.flac'), True)
    nose.tools.eq_(validator.is_audiofile('audio.raw'), True)
    nose.tools.eq_(validator.is_audiofile('path/path/audio.flac'), True)

    nose.tools.eq_(validator.is_audiofile('audio'), False)
    nose.tools.eq_(validator.is_audiofile('123'), False)
    nose.tools.eq_(validator.is_audiofile('54534.232'), False)


def test_is_list():
    validator = dcase_util.utils.FieldValidator
    # is_list
    nose.tools.eq_(validator.is_list('test#'), True)
    nose.tools.eq_(validator.is_list('test#test'), True)
    nose.tools.eq_(validator.is_list('test:test'), True)

    nose.tools.eq_(validator.is_list('test'), False)
    nose.tools.eq_(validator.is_list('test-test'), False)
    nose.tools.eq_(validator.is_list('12342.0'), False)


def test_is_alpha():
    validator = dcase_util.utils.FieldValidator
    # is_alpha
    nose.tools.eq_(validator.is_alpha('a', length=1), True)
    nose.tools.eq_(validator.is_alpha('aa', length=2), True)
    nose.tools.eq_(validator.is_alpha('aaa', length=3), True)

    nose.tools.eq_(validator.is_alpha('aaa', length=1), False)
    nose.tools.eq_(validator.is_alpha('aa', length=1), False)
    nose.tools.eq_(validator.is_alpha('aaa', length=2), False)

    nose.tools.eq_(validator.is_alpha('1', length=1), False)
