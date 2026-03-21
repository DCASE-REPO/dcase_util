""" Unit tests for FIFOBuffer """
import numpy
import dcase_util

from dcase_util.containers import MetaDataContainer
from dcase_util.data import DataBuffer

def test_DataBuffer():
    buf = DataBuffer(size=2)
    assert buf.count == 0
    assert buf.full == False
    buf.set(key='key1', data=[1, 2, 3], meta='metadata1')
    assert buf.count == 1
    assert buf.full == False
    buf.set(key='key2', data=[2, 3, 4], meta='metadata2')
    assert buf.count == 2
    assert buf.full == True

    item_data, item_meta = buf.get(key='key1')
    assert item_data == [1, 2, 3]
    assert item_meta == 'metadata1'

    item_data, item_meta = buf.get(key='key2')
    assert item_data == [2, 3, 4]
    assert item_meta == 'metadata2'

    buf.set(key='key3', data=[3, 4, 5], meta='metadata3')
    item_data, item_meta = buf.get(key='key3')
    assert item_data == [3, 4, 5]
    assert item_meta == 'metadata3'

    assert buf.get(key='key4') == (None, None)

    assert buf.count == 2

    buf.clear()
    assert buf.count == 0

def test_log():
    with dcase_util.utils.DisableLogger():
        DataBuffer(
            size=2,
            filename='event_roller.cpickle'
        ).log()

