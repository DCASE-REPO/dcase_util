""" Unit tests for DictFile """

import pytest
import dcase_util
from dcase_util.containers import ListContainer
import tempfile
import os

def test_load():
    # Txt
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', prefix='prefix_', dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('line1\n')
        tmp.write('line2\n')
        tmp.write('line3\n')
        tmp.close()

        m = ListContainer().load(filename=tmp.name)

        assert m == ['line1', 'line2', 'line3']
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

def test_save():
    ListContainer(['line1', 'line2', 'line3']).save(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    d = ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    assert d == ['line1', 'line2', 'line3']

    f = open(os.path.join(tempfile.gettempdir(), 'saved.txt'), 'r')
    x = f.readlines()
    assert x == ['line1\n', 'line2\n', 'line3\n']

    d = ListContainer(
        ['line1', 'line2', 'line3'],
        filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle')
    ).save().load()
    assert d == ['line1', 'line2', 'line3']

def test_empty():
    # Test #1
    d = ListContainer([])
    assert d.empty() == True

    # Test #2
    d = ListContainer(['line1', 'line2'])
    assert d.empty() == False

def test_log():
    with dcase_util.utils.DisableLogger():
        ListContainer([
            'test1', 'test2'
        ], filename='test.txt').log()

def test_load_not_found2():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))

def test_load_wrong_type():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))

def test_load_wrong_type2():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
