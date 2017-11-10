""" Unit tests for MetaDataItem """

import os
import tempfile

import nose.tools

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

    nose.tools.eq_(item.scene_label, 'office')
    nose.tools.eq_(item.event_label, 'speech')
    nose.tools.eq_(item.onset, 1.0)
    nose.tools.eq_(item.offset, 10.0)
    nose.tools.eq_(item.identifier, 'a001')
    nose.tools.eq_(item.source_label, 'm')
    nose.tools.eq_(item.id, '606198b478e63c2d88af9a5a07471e3d')

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'scene_label': 'office',
    })
    nose.tools.eq_(item.get_list(), ['audio_001.wav', 'office'])

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'tags': 'cat, dog',
    })
    nose.tools.eq_(item.tags, ['cat', 'dog'])

    item = MetaDataItem({
        'filename': 'audio_001.wav',
        'tags': ['cat', 'dog']
    })
    nose.tools.eq_(item.tags, ['cat', 'dog'])

    item.tags = ['bird']
    nose.tools.eq_(item.tags, ['bird'])

    item.tags = 'bird, cat'
    nose.tools.eq_(item.tags, ['bird', 'cat'])

    item.tags = 'bird;cat'
    nose.tools.eq_(item.tags, ['bird', 'cat'])

    item.tags = 'bird:cat'
    nose.tools.eq_(item.tags, ['bird', 'cat'])

    item.tags = 'bird#cat'
    nose.tools.eq_(item.tags, ['bird', 'cat'])
