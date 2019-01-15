""" Unit tests for ListDictContainer """

import nose.tools
import dcase_util
from dcase_util.containers import OneToOneMappingContainer
from nose.tools import *
import tempfile
import os


def test_OneToOneMappingContainer():
    m = OneToOneMappingContainer(
        {
            'key1': 'mapped1',
            'key2': 'mapped2',
            'key3': 'mapped3',
            'key4': 'mapped4',
        }
    )
    nose.tools.eq_(m.map('key1'), 'mapped1')
    nose.tools.eq_(m.map('key2'), 'mapped2')
    nose.tools.eq_(m.map('key3'), 'mapped3')
    nose.tools.eq_(m.map('key4'), 'mapped4')
    nose.tools.eq_(m.map('key5', 'default'), 'default')

    m_ = m.flipped
    nose.tools.eq_(m_.map('mapped1'), 'key1')
    nose.tools.eq_(m_.map('mapped2'), 'key2')
    nose.tools.eq_(m_.map('mapped3'), 'key3')
    nose.tools.eq_(m_.map('mapped4'), 'key4')
    nose.tools.eq_(m_.map('mapped5', 'default'), 'default')

    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('key1' + delimiter + 'mapped1\n')
            tmp.write('key2' + delimiter + 'mapped2\n')
            tmp.close()

            m = OneToOneMappingContainer(filename=tmp.name).load()
            nose.tools.eq_(m.map('key1'), 'mapped1')
            nose.tools.eq_(m.map('key2'), 'mapped2')
        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        m = OneToOneMappingContainer(
            {
                'key1': 'mapped1',
                'key2': 'mapped2',
                'key3': 'mapped3',
                'key4': 'mapped4',
            }, filename=tmp.name
        ).save()

        m_ = OneToOneMappingContainer(filename=tmp.name).load()
        nose.tools.eq_(m_.map('key1'), 'mapped1')
        nose.tools.eq_(m_.map('key2'), 'mapped2')
        nose.tools.eq_(m_.map('key3'), 'mapped3')
        nose.tools.eq_(m_.map('key4'), 'mapped4')
        nose.tools.eq_(m_.map('key5', 'default'), 'default')
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_save():
    # Empty content
    OneToOneMappingContainer({}).save(filename=os.path.join(tempfile.gettempdir(), 'saved.csv'))
    OneToOneMappingContainer({}).save(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    OneToOneMappingContainer({}).save(filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle'))

    # Content
    data = {
        'key1': 'mapped1',
        'key2': 'mapped2',
        'key3': 'mapped3',
        'key4': 'mapped4'
    }

    OneToOneMappingContainer(data).save(filename=os.path.join(tempfile.gettempdir(), 'saved.csv'))
    d = OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.csv'))
    nose.tools.assert_dict_equal(d, data)

    OneToOneMappingContainer(data).save(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    d = OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    nose.tools.assert_dict_equal(d, data)

    OneToOneMappingContainer(data).save(filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle'))
    d = OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle'))
    nose.tools.assert_dict_equal(d, data)


@raises(IOError)
def test_load_not_found2():
    with dcase_util.utils.DisableLogger():
        OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))


@raises(IOError)
def test_load_wrong_type():
    with dcase_util.utils.DisableLogger():
        OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
