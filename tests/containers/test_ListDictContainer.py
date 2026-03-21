""" Unit tests for ListDictContainer """

import pytest
import dcase_util
from dcase_util.containers import ListDictContainer
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
    assert column == [100, 200, 300, 400]

    column = data.get_field(field_name='key2')
    assert column == [400, 300, 200, 100]

    assert data.search(key='key1', value=100) == {'key1': 100, 'key2': 400}
    assert data.search(key='key1', value=123) == None

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
    assert d == data

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.csv')).save().load(
        fields=['key1', 'key2']
    )
    assert d == data

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.csv')).save(
        fields=['key1', 'key2']
    ).load(
        fields=['key1', 'key2']
    )
    assert d == data

    d = ListDictContainer(data, filename=os.path.join(tempfile.gettempdir(), 'saved.cpickle')).save().load()
    assert d == data

def test_load_not_found2():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.txt'))

def test_load_wrong_type():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.cpickle'))

def test_load_wrong_type2():
    with pytest.raises(IOError):
        with dcase_util.utils.DisableLogger():
            ListDictContainer().load(filename=os.path.join(tempfile.gettempdir(), 'wrong.abc'))
