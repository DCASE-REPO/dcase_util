""" Unit tests for MetaDataItem """

import os
import tempfile
from dcase_util.containers import MetaDataItem

def test_MetaDataItem():
    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'scene_label': 'office',
        'event_label': 'speech',
        'onset': 1.0,
        'offset': 10.0,
        'identifier': 'a001',
        'source_label': 'm',
    })

    assert item.scene_label == 'office'
    assert item.event_label == 'speech'
    assert item.onset == 1.0
    assert item.offset == 10.0
    assert item.identifier == 'a001'
    assert item.source_label == 'm'
    assert item.id == '606198b478e63c2d88af9a5a07471e3d'

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'scene_label': 'office',
    })
    assert item.get_list() == ['audio_001.wav', 'office']

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'tags': 'cat, dog',
    })
    assert item.tags == ['cat', 'dog']

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'tags': ['cat', 'dog']
    })
    assert item.tags == ['cat', 'dog']

    item.tags = ['bird']
    assert item.tags == ['bird']

    item.tags = 'bird, cat'
    assert item.tags == ['bird', 'cat']

    item.tags = 'bird;cat'
    assert item.tags == ['bird', 'cat']

    item.tags = 'bird:cat'
    assert item.tags == ['bird', 'cat']

    item.tags = 'bird#cat'
    assert item.tags == ['bird', 'cat']
