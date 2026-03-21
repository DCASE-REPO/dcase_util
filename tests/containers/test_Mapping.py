""" Unit tests for ListDictContainer """

import pytest
import dcase_util
from dcase_util.containers import OneToOneMappingContainer
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
    assert m.map('key1') == 'mapped1'
    assert m.map('key2') == 'mapped2'
    assert m.map('key3') == 'mapped3'
    assert m.map('key4') == 'mapped4'
    assert m.map('key5', 'default') == 'default'

    m_ = m.flipped
    assert m_.map('mapped1') == 'key1'
    assert m_.map('mapped2') == 'key2'
    assert m_.map('mapped3') == 'key3'
    assert m_.map('mapped4') == 'key4'
    assert m_.map('mapped5', 'default') == 'default'

    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('key1' + delimiter + 'mapped1\n')
            tmp.write('key2' + delimiter + 'mapped2\n')
            tmp.close()

            m = OneToOneMappingContainer(filename=tmp.name).load()
            assert m.map('key1') == 'mapped1'
            assert m.map('key2') == 'mapped2'
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
        assert m_.map('key1') == 'mapped1'
        assert m_.map('key2') == 'mapped2'
        assert m_.map('key3') == 'mapped3'
        assert m_.map('key4') == 'mapped4'
        assert m_.map('key5', 'default') == 'default'
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
    assert d == data

    OneToOneMappingContainer(data).save(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    d = OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    assert d == data

    OneToOneMappingContainer(data).save(filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle'))
    d = OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle'))
    assert d == data

def test_load_not_found2():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))

def test_load_wrong_type():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            OneToOneMappingContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
