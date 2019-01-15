""" Unit tests for ProbabilityContainer """

import os
import tempfile
from nose.tools import *
import nose.tools

import dcase_util
from dcase_util.containers import ProbabilityContainer, ProbabilityItem


def test_item():
    item = ProbabilityItem(
        {
            'filename': 'file1.wav',
            'label': 'cat',
            'probability': 0.123456789
        }
    )
    with dcase_util.utils.DisableLogger():
        item.log()

    item = ProbabilityItem(
        {
            'filename': 'file1.wav',
            'label': 'none',
            'probability': 0.123456789
        }
    )
    with dcase_util.utils.DisableLogger():
        item.log()

    item.filename = 'file2.wav'
    item.label = 'cat'
    item.probability = 0.1

    nose.tools.eq_(item.filename, 'file2.wav')
    nose.tools.eq_(item.label, 'cat')
    nose.tools.eq_(item.probability, 0.1)


def test_container():
    item_list = ProbabilityContainer(
        [
            {
                'filename': 'file1.wav',
                'label': 'cat',
                'probability': 0.123456789
            },
            {
                'filename': 'file1.wav',
                'label': 'dog',
                'probability': 0.234
            },
            {
                'filename': 'file2.wav',
                'label': 'cat',
                'probability': 0.123456789
            },
            {
                'filename': 'file2.wav',
                'label': 'dog',
                'probability': 0.234
            },
        ]
    )

    nose.tools.eq_(item_list.unique_labels, ['cat', 'dog'])
    nose.tools.eq_(item_list.unique_files, ['file1.wav', 'file2.wav'])
    nose.tools.eq_(len(item_list.filter(label='dog')), 2)
    nose.tools.eq_(len(item_list.filter(filename='file1.wav')), 2)
    nose.tools.eq_(len(item_list.filter(file_list=['file1.wav', 'file2.wav'])), 4)
    nose.tools.eq_(len(item_list.filter(filename='file1.wav', label='cat')), 1)

    item_list1 = ProbabilityContainer(
        [
            {
                'filename': 'file1.wav',
                'label': 'cat',
                'probability': 0.123456789
            },
            {
                'filename': 'file1.wav',
                'label': 'dog',
                'probability': 0.234
            }
        ]
    )
    item_list2 = ProbabilityContainer(
        [
            {
                'filename': 'file2.wav',
                'label': 'cat',
                'probability': 0.123456789
            },
            {
                'filename': 'file2.wav',
                'label': 'dog',
                'probability': 0.234
            },
        ]
    )

    item_list = item_list1 + item_list2
    nose.tools.eq_(item_list.unique_labels, ['cat', 'dog'])
    nose.tools.eq_(item_list.unique_files, ['file1.wav', 'file2.wav'])
    nose.tools.eq_(len(item_list.filter(label='dog')), 2)
    nose.tools.eq_(len(item_list.filter(filename='file1.wav')), 2)
    nose.tools.eq_(len(item_list.filter(file_list=['file1.wav', 'file2.wav'])), 4)


def test_formats():
    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('file1.wav' + delimiter + 'cat' + delimiter + '0.7\n')
            tmp.write('file1.wav' + delimiter + 'dog' + delimiter + '0.3\n')
            tmp.write('file1.wav' + delimiter + 'bird' + delimiter + '0.4\n')
            tmp.write('file2.wav' + delimiter + 'c' + delimiter + '0.2\n')
            tmp.write('file2.wav' + delimiter + 'd' + delimiter + '0.3\n')
            tmp.write('file2.wav' + delimiter + 'b' + delimiter + '0.6\n')
            tmp.close()

            item_list = ProbabilityContainer().load(filename=tmp.name)

            nose.tools.eq_(item_list[0].filename, 'file1.wav')
            nose.tools.eq_(item_list[0].label, 'cat')
            nose.tools.eq_(item_list[0].probability, 0.7)

            nose.tools.eq_(item_list[1].filename, 'file1.wav')
            nose.tools.eq_(item_list[1].label, 'dog')
            nose.tools.eq_(item_list[1].probability, 0.3)

            nose.tools.eq_(item_list[3].filename, 'file2.wav')
            nose.tools.eq_(item_list[3].label, 'c')
            nose.tools.eq_(item_list[3].probability, 0.2)

            with dcase_util.utils.DisableLogger():
                item_list.log()

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass


@raises(IOError)
def test_unknown_formats():
    with dcase_util.utils.DisableLogger():
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('file1.wav' + ',' + 'cat\n')
            tmp.close()
            item_list = ProbabilityContainer().load(filename=tmp.name)

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass


def test_save():
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        item_list = ProbabilityContainer(
            [
                {
                    'filename': 'file1.wav',
                    'label': 'cat',
                    'probability': 0.123456789
                },
                {
                    'filename': 'file1.wav',
                    'label': 'dog',
                    'probability': 0.234
                },
                {
                    'filename': 'file2.wav',
                    'label': 'cat',
                    'probability': 0.123456789
                },
                {
                    'filename': 'file2.wav',
                    'label': 'dog',
                    'probability': 0.234
                },
            ],
            filename=tmp.name
        ).save().load()

        nose.tools.eq_(item_list[0].filename, 'file1.wav')
        nose.tools.eq_(item_list[0].label, 'cat')
        nose.tools.eq_(item_list[0].probability, 0.123456789)

        nose.tools.eq_(item_list[1].filename, 'file1.wav')
        nose.tools.eq_(item_list[1].label, 'dog')
        nose.tools.eq_(item_list[1].probability, 0.234)
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        item_list = ProbabilityContainer(
            [
                {
                    'filename': 'file1.wav',
                    'label': 'c',
                    'probability': 0.123456789
                },
                {
                    'filename': 'file1.wav',
                    'label': 'd',
                    'probability': 0.234
                },
                {
                    'filename': 'file2.wav',
                    'label': 'ca',
                    'probability': 0.123456789
                },
                {
                    'filename': 'file2.wav',
                    'label': 'do',
                    'probability': 0.234
                },
            ],
            filename=tmp.name
        ).save().load()

        nose.tools.eq_(item_list[0].filename, 'file1.wav')
        nose.tools.eq_(item_list[0].label, 'c')
        nose.tools.eq_(item_list[0].probability, 0.123456789)

        nose.tools.eq_(item_list[2].filename, 'file2.wav')
        nose.tools.eq_(item_list[2].label, 'ca')
        nose.tools.eq_(item_list[2].probability, 0.123456789)
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


@raises(IOError)
def test_load_not_found():
    with dcase_util.utils.DisableLogger():
        ProbabilityContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))


@raises(IOError)
def test_load_wrong_type():
    with dcase_util.utils.DisableLogger():
        ProbabilityContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.wav'))


@raises(IOError)
def test_load_wrong_type2():
    with dcase_util.utils.DisableLogger():
        ProbabilityContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
