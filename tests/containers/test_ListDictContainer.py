""" Unit tests for ListDictContainer """

import nose.tools
import dcase_util
from dcase_util.containers import ListDictContainer
from nose.tools import *
import tempfile
import os


def test_container():
    data = ListDictContainer([
        {
            'key1': 100,
            'key2': 400,
        },
        {
            'key1': 200,
            'key2': 300,
        },
        {
            'key1': 300,
            'key2': 200,
        },
        {
            'key1': 400,
            'key2': 100,
        },
    ])

    column = data.get_field(field_name='key1')
    nose.tools.eq_(column, [100, 200, 300, 400])

    column = data.get_field(field_name='key2')
    nose.tools.eq_(column, [400, 300, 200, 100])

    nose.tools.eq_(data.search(key='key1', value=100), {'key1': 100, 'key2': 400})
    nose.tools.eq_(data.search(key='key1', value=123), None)


def test_save():
    # Empty content
    ListDictContainer({}).save(filename=os.path.join(tempfile.gettempdir(), 'saved.yaml'))
    
    # Content
    data = [
        {
            'key1': 100,
            'key2': 402.2,
        },
        {
            'key1': 200,
            'key2': 302.2,
        },
        {
            'key1': 300,
            'key2': 202.3,
        },
        {
            'key1': 400,
            'key2': 101.2,
        },
    ]

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.yaml')).save().load()
    nose.tools.assert_list_equal(d, data)

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.csv')).save().load(
        fields=['key1', 'key2']
    )
    nose.tools.assert_list_equal(d, data)

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.csv')).save(
        fields=['key1', 'key2']
    ).load(
        fields=['key1', 'key2']
    )
    nose.tools.assert_list_equal(d, data)

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle')).save().load()
    nose.tools.assert_list_equal(d, data)


@raises(IOError)
def test_load_not_found2():
    with dcase_util.utils.DisableLogger():
        ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))


@raises(IOError)
def test_load_wrong_type():
    with dcase_util.utils.DisableLogger():
        ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))


@raises(IOError)
def test_load_wrong_type2():
    with dcase_util.utils.DisableLogger():
        ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
