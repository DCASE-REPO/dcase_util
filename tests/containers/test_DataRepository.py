""" Unit tests for DataMatrix2DContainer """

import nose.tools
import dcase_util
import tempfile
import os
import numpy


def test_container():
    # 1
    data_repository = dcase_util.containers.DataRepository(
        data={
            'label1': {
                'stream0': {
                    'data': 100
                },
                'stream1': {
                    'data': 200
                }
            },
            'label2': {
                'stream0': {
                    'data': 300
                },
                'stream1': {
                    'data': 400
                }
            }
        }
    )
    nose.tools.eq_(data_repository.labels, ['label1', 'label2'])
    nose.tools.eq_(data_repository.stream_ids('label1'), ['stream0', 'stream1'])
    nose.tools.eq_(data_repository.stream_ids('label2'), ['stream0', 'stream1'])

    nose.tools.eq_(data_repository.get_container(label='label1', stream_id='stream0'), {'data': 100})

    data_repository.set_container(container={'data': 123}, label='label1', stream_id='stream0')
    nose.tools.eq_(data_repository.get_container(label='label1', stream_id='stream0'), {'data': 123})


def test_save_load():
    data_repository = dcase_util.containers.DataRepository(
        data={
            'label1': {
                'stream0': {
                    'data': 100
                },
                'stream1': {
                    'data': 200
                }
            },
            'label2': {
                'stream0': {
                    'data': 300
                },
                'stream1': {
                    'data': 400
                }
            }
        }
    )

    # PICKLE
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle',  dir=tempfile.gettempdir(), delete=False)
    try:
        data_repository.save(filename=tmp.name)
        data_repository_loaded = dcase_util.containers.DataRepository().load(filename=tmp.name)
        nose.tools.eq_(data_repository_loaded.labels, ['label1', 'label2'])
        nose.tools.eq_(data_repository_loaded.stream_ids('label1'), ['stream0', 'stream1'])
        nose.tools.eq_(data_repository_loaded.stream_ids('label2'), ['stream0', 'stream1'])

        nose.tools.eq_(data_repository_loaded.get_container(label='label1', stream_id='stream0'), {'data': 100})

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass


def test_log():
    with dcase_util.utils.DisableLogger():
        data_repository = dcase_util.containers.DataRepository(
            data={
                'label1': {
                    'stream0': {
                        'data': 100
                    },
                    'stream1': {
                        'data': 200
                    }
                },
                'label2': {
                    'stream0': {
                        'data': 300
                    },
                    'stream1': {
                        'data': 400
                    }
                }
            }
        )
        data_repository.log()
