""" Unit tests for DictFile """

import nose.tools
import dcase_util
from dcase_util.containers import ListContainer
from nose.tools import *
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

        nose.tools.assert_list_equal(m, ['line1', 'line2', 'line3'])
    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_save():
    ListContainer(['line1', 'line2', 'line3']).save(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    d = ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'saved.txt'))
    nose.tools.assert_list_equal(d, ['line1', 'line2', 'line3'])

    f = open(os.path.join(tempfile.gettempdir(), 'saved.txt'), 'r')
    x = f.readlines()
    nose.tools.assert_list_equal(x, ['line1\n', 'line2\n', 'line3\n'])

    d = ListContainer(
        ['line1', 'line2', 'line3'],
        filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle')
    ).save().load()
    nose.tools.assert_list_equal(d, ['line1', 'line2', 'line3'])


def test_empty():
    # Test #1
    d = ListContainer([])
    nose.tools.eq_(d.empty(), True)

    # Test #2
    d = ListContainer(['line1', 'line2'])
    nose.tools.eq_(d.empty(), False)


def test_log():
    with dcase_util.utils.DisableLogger():
        ListContainer([
            'test1', 'test2'
        ], filename='test.txt').log()


@raises(IOError)
def test_load_not_found2():
    with dcase_util.utils.DisableLogger():
        ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))


@raises(IOError)
def test_load_wrong_type():
    with dcase_util.utils.DisableLogger():
        ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))


@raises(IOError)
def test_load_wrong_type2():
    with dcase_util.utils.DisableLogger():
        ListContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
