""" Unit tests for AppParameterContainer """

import nose.tools
import dcase_util
import tempfile
import os


def test_container():
    param = dcase_util.containers.DCASEAppParameterContainer(
        {
            'active_set': 'set1',
            'sets': [
                {
                    'set_id': 'set1',
                    'general': {
                        'field1': 100,
                    }
                },
                {
                    'set_id': 'set2',
                    'general': {
                        'field1': 200,
                    }
                },
                {
                    'set_id': 'set3',
                    'general': {
                        'field1': 300,
                    }
                },
            ],
            'defaults': {
                'path': {
                    'application': {
                        'base': 'system',
                        'feature_extractor': 'feature_extractor',
                        'feature_normalizer': 'feature_normalizer',
                        'learner': 'learner',
                        'recognizer': 'recognizer',
                        'evaluator': 'evaluator',
                    }
                },
                'logging': {
                    'enable': True,
                    'parameters': {
                        'handlers': {
                            'console': {
                                'class': 'logging.StreamHandler',
                                'level': 'DEBUG',
                                'formatter': 'simple',
                                'stream': 'ext://sys.stdout'
                            }
                        }
                    }
                },
                'general': {
                    'field1': 1,
                    'scene_handling': 'scene_handling',
                    'event_handling': 'event_handling',
                    'active_scenes': 'active_scenes',
                    'active_events': 'active_events'
                },
                'dataset_method_parameters': {
                    'field': 'test'
                },
                'feature_extractor': {
                    'fs': 44100,
                    'win_length_seconds': 0.04,
                    'hop_length_seconds': 0.02,
                },
                'feature_extractor_method_parameters': {
                    'mel': {
                        'n_mels': 40
                    },
                    'mfcc': {
                        'n_mfccs': 20
                    },
                    'mfcc_delta': {
                        'width': 9
                    }

                },
                'feature_stacker': {
                    'stacking_recipe': 'mel;mfcc;mfcc_delta',
                },
                'feature_normalizer': {
                    'enable': True,
                    'type': 'global'
                },
                'feature_aggregator': {
                    'enable': True,
                    'aggregation_recipe': 'flatten',
                    'win_length_seconds': 0.1,
                    'hop_length_seconds': 0.02,
                },
                'learner': {
                    'method': 'gmm'
                },
                'learner_method_parameters': {
                    'gmm': {
                        'nc': 16
                    }
                },
                'recognizer': {
                    'test': 'test',
                    'frame_accumulation': {
                        'enable': True,
                    },
                    'event_activity_processing': {
                        'enable': True,
                        'window_length_seconds': 1.0
                    }
                },
                'evaluator': {
                    'test': 'test'
                }
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app'),
    )
    param.process()
    nose.tools.eq_(param['general']['field1'], 100)
    nose.tools.eq_(
        param['path']['application']['base'],
        os.path.join(tempfile.gettempdir(), 'dcase_util_app', 'system')
    )
    nose.tools.eq_(
        param['path']['application']['feature_extractor']['mel'],
        os.path.join(
            tempfile.gettempdir(),
            'dcase_util_app',
            'system',
            'feature_extractor',
            'feature_extractor_32f4f694c22356bd4529290397a41bda'
        )
    )

    nose.tools.eq_(param['feature_extractor']['hop_length_samples'], 882)
    nose.tools.eq_(param['feature_extractor']['parameters']['mel']['n_mels'], 40)
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc']['n_mfccs'], 20)
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc_delta']['width'], 9)
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc_delta']['dependency_method'], 'mfcc')
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc_delta']['dependency_parameters']['fs'], 44100)

    nose.tools.eq_(param['learner']['parameters']['nc'], 16)

    nose.tools.eq_(param['feature_aggregator']['hop_length_frames'], 1)


