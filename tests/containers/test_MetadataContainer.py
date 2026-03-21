""" Unit tests for MetadataContainer """

import os
import tempfile
import numpy
from dcase_util.containers import MetaDataContainer
from dcase_util.utils import FieldValidator

content = [
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 10.0,
            'identifier': 'A001'
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'mouse clicking',
            'onset': 3.0,
            'offset': 5.0,
            'identifier': 'A001'
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'printer',
            'onset': 7.0,
            'offset': 9.0,
            'identifier': 'A001'
        },
        {
            'filename': 'audio_002.wav',
            'scene_label': 'meeting',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 9.0,
            'identifier': 'A002'
        },
        {
            'filename': 'audio_002.wav',
            'scene_label': 'meeting',
            'event_label': 'printer',
            'onset': 5.0,
            'offset': 7.0,
            'identifier': 'A002'
        },
    ]

content2 = [
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 1.2,
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 1.5,
            'offset': 3.0,
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 4.0,
            'offset': 6.0,
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 7.0,
            'offset': 8.0,
        },
    ]

content3 = [
        {
            'filename': 'audio_001.wav',
            'tags': 'tag1,tag2',
        },
        {
            'filename': 'audio_002.wav',
            'tags': 'tag2',
        },
        {
            'filename': 'audio_003.wav',
            'tags': 'tag2,tag3',
        },
        {
            'filename': 'audio_004.wav',
            'tags': 'tag1,tag3',
        },
    ]

def test_formats():
    delimiters = [',', ';', '\t']
    for delimiter in delimiters:
        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('0.5' + delimiter + '0.7\n')
            tmp.write('2.5' + delimiter + '2.7\n')
            tmp.close()

            item = MetaDataContainer().load(filename=tmp.name)[0]
            assert item.onset == 0.5
            assert item.offset == 0.7

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt',  dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('0.5' + delimiter + '0.7' + delimiter + 'event\n')
            tmp.write('2.5' + delimiter + '2.7' + delimiter + 'event\n')
            tmp.close()

            item = MetaDataContainer().load(filename=tmp.name)[0]
            assert item.onset == 0.5
            assert item.offset == 0.7
            assert item.event_label == 'event'

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('file.wav' + delimiter + 'scene' + delimiter + '0.5' + delimiter + '0.7' + delimiter + 'event\n')
            tmp.write('file.wav' + delimiter + 'scene' + delimiter + '0.5' + delimiter + '0.7' + delimiter + 'event\n')
            tmp.close()

            item = MetaDataContainer().load(filename=tmp.name)[0]
            assert item.onset == 0.5
            assert item.offset == 0.7
            assert item.event_label == 'event'
            assert item.filename == 'file.wav'
            assert item.scene_label == 'scene'

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

        tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
        try:
            tmp.write('file.wav' + delimiter + 'scene' + delimiter + '0.5' + delimiter + '0.7' + delimiter + 'event' + delimiter + 'm' + delimiter + 'a1\n')
            tmp.write('file.wav' + delimiter + 'scene' + delimiter + '0.5' + delimiter + '0.7' + delimiter + 'event' + delimiter + 'm' + delimiter + 'a2\n')
            tmp.close()

            item = MetaDataContainer().load(filename=tmp.name)[0]
            assert item.onset == 0.5
            assert item.offset == 0.7
            assert item.event_label == 'event'
            assert item.filename == 'file.wav'
            assert item.scene_label == 'scene'
            assert item.identifier == 'a1'
            assert item.source_label == 'm'

        finally:
            try:
                tmp.close()
                os.unlink(tmp.name)
            except:
                pass

def test_content():
    meta = MetaDataContainer(content)
    assert len(meta) == 5

    # Test content
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 10.0

    assert meta[4].filename == 'audio_002.wav'
    assert meta[4].scene_label == 'meeting'
    assert meta[4].event_label == 'printer'
    assert meta[4].onset == 5.0
    assert meta[4].offset == 7.0

def test_filter():
    # Test filter by file
    meta = MetaDataContainer(content).filter(filename='audio_002.wav')

    assert len(meta) == 2
    assert meta[0].filename == 'audio_002.wav'
    assert meta[0].scene_label == 'meeting'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 9.0

    assert meta[1].filename == 'audio_002.wav'
    assert meta[1].scene_label == 'meeting'
    assert meta[1].event_label == 'printer'
    assert meta[1].onset == 5.0
    assert meta[1].offset == 7.0

    # Test filter by scene_label
    meta = MetaDataContainer(content).filter(scene_label='office')

    assert len(meta) == 3
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 10.0

    assert meta[1].filename == 'audio_001.wav'
    assert meta[1].scene_label == 'office'
    assert meta[1].event_label == 'mouse clicking'
    assert meta[1].onset == 3.0
    assert meta[1].offset == 5.0

    meta = MetaDataContainer(content).filter(scene_list=['meeting'])
    assert len(meta) == 2

    # Test filter by event_label
    meta = MetaDataContainer(content).filter(event_label='speech')

    assert len(meta) == 2
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 10.0

    assert meta[1].filename == 'audio_002.wav'
    assert meta[1].scene_label == 'meeting'
    assert meta[1].event_label == 'speech'
    assert meta[1].onset == 1.0
    assert meta[1].offset == 9.0

    meta = MetaDataContainer(content).filter(event_list=['speech', 'printer'])
    assert len(meta) == 4

    # Test filter by tags
    meta = MetaDataContainer(content3).filter(tag='tag1')
    assert len(meta) == 2

    meta = MetaDataContainer(content3).filter(tag_list=['tag1', 'tag3'])
    assert len(meta) == 3

def test_filter_time_segment():
    # Case 1
    meta = MetaDataContainer(content).filter_time_segment(
        filename='audio_001.wav',
        start=1.0,
        stop=3.5,
        zero_time=True,
        trim=True,
    )

    assert len(meta) == 2
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 0.0
    assert meta[0].offset == 2.5

    assert meta[1].filename == 'audio_001.wav'
    assert meta[1].scene_label == 'office'
    assert meta[1].event_label == 'mouse clicking'
    assert meta[1].onset == 2.0
    assert meta[1].offset == 2.5

    # Case 2
    meta = MetaDataContainer(content).filter_time_segment(
        filename='audio_001.wav',
        start=1.0,
        stop=3.5,
        zero_time=False,
        trim=True,
    )
    assert len(meta) == 2
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 3.5

    assert meta[1].filename == 'audio_001.wav'
    assert meta[1].scene_label == 'office'
    assert meta[1].event_label == 'mouse clicking'
    assert meta[1].onset == 3.0
    assert meta[1].offset == 3.5

    # Case 3
    meta = MetaDataContainer(content).filter_time_segment(
        filename='audio_001.wav',
        start=1.0,
        stop=3.5,
        zero_time=False,
        trim=False,
    )
    assert len(meta) == 2
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.0
    assert meta[0].offset == 10.0

    assert meta[1].filename == 'audio_001.wav'
    assert meta[1].scene_label == 'office'
    assert meta[1].event_label == 'mouse clicking'
    assert meta[1].onset == 3.0
    assert meta[1].offset == 5.0

def test_process_events():
    meta = MetaDataContainer(content2).process_events(
        minimum_event_gap=0.5,
        minimum_event_length=1.0
    )

    assert len(meta) == 3

    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.5
    assert meta[0].offset == 3.0

    assert meta[1].filename == 'audio_001.wav'
    assert meta[1].scene_label == 'office'
    assert meta[1].event_label == 'speech'
    assert meta[1].onset == 4.0
    assert meta[1].offset == 6.0

    assert meta[2].filename == 'audio_001.wav'
    assert meta[2].scene_label == 'office'
    assert meta[2].event_label == 'speech'
    assert meta[2].onset == 7.0
    assert meta[2].offset == 8.0

    meta = MetaDataContainer(content2).process_events(
        minimum_event_gap=1.0,
        minimum_event_length=1.0
    )

    assert len(meta) == 1
    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 1.5
    assert meta[0].offset == 8.0

    meta = MetaDataContainer(
        [
            {
                'filename': 'audio_001.wav',
                'scene_label': 'office',
                'event_label': 'mouse clicking',
                'onset': 3.0,
                'offset': 5.0,
                'identifier': 'A001'
            },
            {
                'filename': 'audio_001.wav',
                'scene_label': 'office',
                'event_label': 'mouse clicking',
                'onset': 13.0,
                'offset': 13.0,
                'identifier': 'A001'
            },
        ]
    ).process_events(minimum_event_gap=1.0, minimum_event_length=numpy.spacing(1))

    assert len(meta) == 1

def test_add_time_offset():
    meta = MetaDataContainer(content2).add_time(time=2.0)

    assert len(meta) == 4

    assert meta[0].filename == 'audio_001.wav'
    assert meta[0].scene_label == 'office'
    assert meta[0].event_label == 'speech'
    assert meta[0].onset == 3.0
    assert meta[0].offset == 3.2

    assert meta[3].filename == 'audio_001.wav'
    assert meta[3].scene_label == 'office'
    assert meta[3].event_label == 'speech'
    assert meta[3].onset == 9.0
    assert meta[3].offset == 10.0

def test_addition():
    meta = MetaDataContainer(content)
    meta2 = MetaDataContainer(content2)

    meta += meta2

    assert len(meta) == 9
    assert meta[8].filename == 'audio_001.wav'
    assert meta[8].scene_label == 'office'
    assert meta[8].event_label == 'speech'
    assert meta[8].onset == 7.0
    assert meta[8].offset == 8.0

def test_unique_files():
    files = MetaDataContainer(content).unique_files

    assert len(files) == 2
    assert files[0] == 'audio_001.wav'
    assert files[1] == 'audio_002.wav'

def test_event_count():
    assert MetaDataContainer(content).event_count == len(content)

def test_scene_label_count():
    assert MetaDataContainer(content).scene_label_count == 2

def test_event_label_count():
    assert MetaDataContainer(content).event_label_count == 3

def test_unique_event_labels():
    events = MetaDataContainer(content).unique_event_labels
    assert len(events) == 3
    assert events[0] == 'mouse clicking'
    assert events[1] == 'printer'
    assert events[2] == 'speech'

def test_unique_scene_labels():
    scenes = MetaDataContainer(content).unique_scene_labels
    assert len(scenes) == 2
    assert scenes[0] == 'meeting'
    assert scenes[1] == 'office'

def test_max_event_offset():
    assert MetaDataContainer(content).max_offset == 10

def test_intersection():
    data1 = MetaDataContainer(content)

    data2 = MetaDataContainer([
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 10.0,
            'identifier': 'A001'
        }
    ])
    intersection = data1.intersection(data2)
    assert len(intersection) == 1
    assert intersection[0].filename == 'audio_001.wav'

def test_map_events():
    meta = MetaDataContainer(content)
    meta_mapped_1 = meta.map_events(
        target_event_label='activity',
        source_event_labels=['speech', 'printer']
    )
    assert len(meta_mapped_1) == 4

    meta_mapped_2 = meta.map_events(
        target_event_label='activity'
    )
    assert len(meta_mapped_2) == 5

def test_event_inactivity():
    meta = MetaDataContainer(content)
    meta_inactivity = meta.event_inactivity()

    assert len(meta_inactivity) == 3

    meta = MetaDataContainer(
        [
            {
                'filename': 'audio_001.wav',
                'scene_label': 'office',
                'event_label': 'mouse clicking',
                'onset': 3.0,
                'offset': 5.0,
                'identifier': 'A001'
            },
            {
                'filename': 'audio_001.wav',
                'scene_label': 'office',
                'event_label': 'mouse clicking',
                'onset': 13.0,
                'offset': 13.0,
                'identifier': 'A001'
            },
        ]
    )
    meta_inactivity = meta.event_inactivity(duration_list={'audio_001.wav': 20.0})
    assert meta_inactivity[0].onset == 0.00
    assert meta_inactivity[0].offset == 3.00

    assert meta_inactivity[1].onset == 5.00
    assert meta_inactivity[1].offset == 20.00
