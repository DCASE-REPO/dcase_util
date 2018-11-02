""" Unit tests for DictFile """

import nose.tools
import dcase_util
from dcase_util.containers import DictContainer
from nose.tools import *
import os
import tempfile
import pickle
import msgpack
import logging

data = {
    'level1': {
        'field1': 1,
        'field2': 2,
        'field3': 3,
        'level2a': {
            'field1': 1,
            'field2': 2,
            'field3': 3,
            'level3a': {
                'field1': 1,
                'field2': 2,
                'field3': 3,
            },
            'level3b': {
                'field1': 1,
                'field2': 2,
                'field3': 3,
            },
        },
        'level2b': {
            'field1': 1,
            'field2': 2,
            'field3': 3,
            'level3': {
                'field1': 1,
                'field2': 2,
                'field3': 3,
            }
        },
        'level2c': {
            'level3a': {
                'field1': 1,
                'field2': 2,
                'field3': 3,
            },
            'level3b': {
                'field1': 1,
                'field2': 2,
                'field3': 3,
            }
        }
    }
}


def test_container():
    data_container = DictContainer(data)
    nose.tools.eq_(data_container.get_path(path='level1.field1'), 1)
    nose.tools.eq_(data_container.get_path(path='level1.level2a.field2'), 2)
    nose.tools.eq_(data_container.get_path(path='level1.level2b.field3'), 3)
    nose.tools.eq_(data_container.get_path(path='level1.level2a.level3a.field1'), 1)
    nose.tools.eq_(data_container.get_path(path='level1.level2a.level3a'), {'field1': 1, 'field2': 2, 'field3': 3})
    nose.tools.eq_(data_container.get_path(path='level1.level2c.*.field1'), [1, 1])

    nose.tools.eq_(data_container.get_path(path=['level1', 'field1']), 1)
    nose.tools.eq_(data_container.get_path(path=['level1', 'level2a', 'field2']), 2)

    nose.tools.eq_(data_container.get_hash(), '23ffcb8de3af794547779197397ab987')
    nose.tools.eq_(data_container.get_hash_for_path(dotted_path='level1.level2c'), 'a084001c6e49eef233a95f8996d1183c')

    data_container.merge(override={
        'level1': {
            'field1': 10,
            'field2': 20,
            'field3': 30,
            'level2a': {
                'field1': 10,
                'field2': 20,
                'field3': 30,
                'level3a': {
                    'field1': 10,
                    'field2': 20,
                    'field3': 30,
                },
                'level3b': {
                    'field1': 10,
                    'field2': 20,
                    'field3': 30,
                },
            }
        }
    })

    nose.tools.eq_(data_container.get_path(path='level1.field1'), 10)
    nose.tools.eq_(data_container.get_path(path='level1.level2a.field2'), 20)
    nose.tools.eq_(data_container.get_path(path='level1.level2b.field3'), 3)

    data_container.set_path(path='level1.field1', new_value=100)
    nose.tools.eq_(data_container.get_path(path='level1.field1'), 100)

    data_container.set_path(path='level1.level2c.*.field1', new_value=100)
    nose.tools.eq_(data_container.get_path(path='level1.level2c.*.field1'), [100, 100])

    nose.tools.eq_(data_container.get_hash(), '0adb9bf0f7f579e8b297b7186b0570da')
    data_container['_hash'] = 'test'
    nose.tools.eq_(data_container.get_hash(), '0adb9bf0f7f579e8b297b7186b0570da')

    data_container.set_path(path=['level1', 'field2'], new_value=100)
    nose.tools.eq_(data_container.get_path(path='level1.field2'), 100)

    data_container = DictContainer(data)
    nose.tools.eq_(data_container.get_leaf_path_list(),
                   ['level1.field1',
                    'level1.field2',
                    'level1.field3',
                    'level1.level2a.field1',
                    'level1.level2a.field2',
                    'level1.level2a.field3',
                    'level1.level2a.level3a.field1',
                    'level1.level2a.level3a.field2',
                    'level1.level2a.level3a.field3',
                    'level1.level2a.level3b.field1',
                    'level1.level2a.level3b.field2',
                    'level1.level2a.level3b.field3',
                    'level1.level2b.field1',
                    'level1.level2b.field2',
                    'level1.level2b.field3',
                    'level1.level2b.level3.field1',
                    'level1.level2b.level3.field2',
                    'level1.level2b.level3.field3',
                    'level1.level2c.level3a.field1',
                    'level1.level2c.level3a.field2',
                    'level1.level2c.level3a.field3',
                    'level1.level2c.level3b.field1',
                    'level1.level2c.level3b.field2',
                    'level1.level2c.level3b.field3'])

    nose.tools.eq_(data_container.get_leaf_path_list(target_field='field1'),
                   ['level1.field1',
                    'level1.level2a.field1',
                    'level1.level2a.level3a.field1',
                    'level1.level2a.level3b.field1',
                    'level1.level2b.field1',
                    'level1.level2b.level3.field1',
                    'level1.level2c.level3a.field1',
                    'level1.level2c.level3b.field1'])

    nose.tools.eq_(data_container.get_leaf_path_list(target_field_startswith='field'),
                   ['level1.field1',
                    'level1.field2',
                    'level1.field3',
                    'level1.level2a.field1',
                    'level1.level2a.field2',
                    'level1.level2a.field3',
                    'level1.level2a.level3a.field1',
                    'level1.level2a.level3a.field2',
                    'level1.level2a.level3a.field3',
                    'level1.level2a.level3b.field1',
                    'level1.level2a.level3b.field2',
                    'level1.level2a.level3b.field3',
                    'level1.level2b.field1',
                    'level1.level2b.field2',
                    'level1.level2b.field3',
                    'level1.level2b.level3.field1',
                    'level1.level2b.level3.field2',
                    'level1.level2b.level3.field3',
                    'level1.level2c.level3a.field1',
                    'level1.level2c.level3a.field2',
                    'level1.level2c.level3a.field3',
                    'level1.level2c.level3b.field1',
                    'level1.level2c.level3b.field2',
                    'level1.level2c.level3b.field3'])

    nose.tools.eq_(data_container.get_leaf_path_list(target_field_endswith='d1'),
                   ['level1.field1',
                    'level1.level2a.field1',
                    'level1.level2a.level3a.field1',
                    'level1.level2a.level3b.field1',
                    'level1.level2b.field1',
                    'level1.level2b.level3.field1',
                    'level1.level2c.level3a.field1',
                    'level1.level2c.level3b.field1'])


def test_load():
    # YAML
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.yaml',  dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('section:\n')
        tmp.write('  field1: 1\n')
        tmp.write('  field2: 2\n')
        tmp.close()

        m = DictContainer().load(filename=tmp.name)

        nose.tools.assert_dict_equal(m, {'section': {'field1': 1, 'field2': 2}})
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # Json
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.json', dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('{"section":{"field1":1,"field2":2}}\n')
        tmp.close()

        m = DictContainer().load(filename=tmp.name)

        nose.tools.assert_dict_equal(m, {'section': {'field1': 1, 'field2': 2}})
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # pickle
    tmp = tempfile.NamedTemporaryFile('rb+', suffix='.pickle', dir=tempfile.gettempdir(), delete=False)
    try:
        data2 = {
            'section': {
                'field1': 1,
                'field2': 2
            }
        }
        pickle.dump(data2, tmp, protocol=pickle.HIGHEST_PROTOCOL)
        tmp.close()

        m = DictContainer().load(filename=tmp.name)

        nose.tools.assert_dict_equal(m, {'section': {'field1': 1, 'field2': 2}})
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # msgpack
    tmp = tempfile.NamedTemporaryFile('rb+', suffix='.msgpack', dir=tempfile.gettempdir(), delete=False)
    try:
        data2 = {
            'section': {
                'field1': 1,
                'field2': 2
            }
        }
        msgpack.dump(data2, tmp)
        tmp.close()

        m = DictContainer().load(filename=tmp.name)

        nose.tools.assert_dict_equal(m, {'section': {'field1': 1, 'field2': 2}})
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

    # Txt
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('line1\n')
        tmp.write('line2\n')
        tmp.write('line3\n')
        tmp.close()

        m = DictContainer().load(filename=tmp.name)

        nose.tools.assert_dict_equal(m, {0: 'line1\n', 1: 'line2\n', 2: 'line3\n'})
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_save():
    # Empty content
    DictContainer({}).save(filename=os.path.join(tempfile.gettempdir(), 'saved.yaml'))

    # Content
    data2 = {
        'section1': {
            'field1': 1,
            'field2': [1, 2, 3, 4]
        },
        'section2': {
            'field1': {
                'field1': [1, 2, 3, 4]
            },
            'field2': [1, 2, 3, 4]
        }
    }
    DictContainer(data2).save(filename=os.path.join(tempfile.gettempdir(), 'saved.yaml'))
    d = DictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.yaml'))

    nose.tools.assert_dict_equal(d, data2)


def test_empty():
    # Test #1
    d = DictContainer({})
    nose.tools.eq_(d.empty(), True)

    # Test #2
    d = DictContainer({'sec': 1})
    nose.tools.eq_(d.empty(), False)


def test_log():
    with dcase_util.utils.DisableLogger():
        DictContainer(filename='test.yaml').log()


@raises(ValueError)
def test_wrong_path():
    with dcase_util.utils.DisableLogger():
        DictContainer(data).get_path(path=9)


@raises(ValueError)
def test_wrong_path2():
    with dcase_util.utils.DisableLogger():
        DictContainer(data).set_path(path=9, new_value=1)


@raises(IOError)
def test_load_not_found():
    with dcase_util.utils.DisableLogger():
        DictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))


@raises(IOError)
def test_load_wrong_type():
    with dcase_util.utils.DisableLogger():
        DictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.wav'))


@raises(IOError)
def test_load_wrong_type2():
    with dcase_util.utils.DisableLogger():
        DictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
