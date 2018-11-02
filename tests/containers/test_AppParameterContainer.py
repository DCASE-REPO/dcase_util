""" Unit tests for AppParameterContainer """

import nose.tools
import dcase_util
import tempfile
import os


def test_container():
    # 1
    param = dcase_util.containers.AppParameterContainer(
        {
            'test': {
                'test': True,
                'process': False
            },
            'path': {
                'external': {
                    'log': 'test'
                }
            },
            'feature_extraction': {
                'mel': {
                    'value': 1,
                },
                'stacking_recipe': 'mel;mfcc=1:1-20',
            },
            'learner': {
                'param': 1234.1234
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app'),
    )
    param.process()
    nose.tools.eq_(param['_hash'], 'fa21fe5962a01a67d7e7e4d8f5536c7c')
    nose.tools.eq_(param['feature_extraction']['_hash'], 'ef0a20431310a36b05ef942f3f5b6a5a')

    nose.tools.eq_(param['feature_extraction']['stacking_recipe'][0]['label'], 'mel')

    # 2
    param = dcase_util.containers.AppParameterContainer(
        {
            'test': {
                'test': True,
                'process': False
            },
            'path': {
                'external': {
                    'log': 'test/'
                }
            },
            'feature_extraction': {
                'mel': {
                    'value': 1,
                },
                'stacking_recipe': 'mel;mfcc=1:1-20',
            },
            'learner': {
                'param': 1234.1234
            }
        }
    )
    param.process()
    nose.tools.eq_(param['_hash'], 'fa21fe5962a01a67d7e7e4d8f5536c7c')
    nose.tools.eq_(param['feature_extraction']['_hash'], 'ef0a20431310a36b05ef942f3f5b6a5a')

    nose.tools.eq_(param['feature_extraction']['stacking_recipe'][0]['label'], 'mel')

    # 3
    param = dcase_util.containers.AppParameterContainer(
        {
            'test': {
                'test': True,
                'process': False
            },
            'directories': {
                'external': {
                    'log': 'test'
                }
            },
            'feature_extraction': {
                'mel': {
                    'value': 1,
                },
                'stacking_formula': 'mel;mfcc=1:1-20',
            },
            'learner': {
                'param': 1234.1234
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app'),
        field_labels={
            'RECIPE': 'formula'
        },
        section_labels={
            'PATH': 'directories',
        },
    )
    param.process()
    nose.tools.eq_(param['_hash'], '74501e81cabe55b4f05f001b502e5e3d')
    nose.tools.eq_(param['feature_extraction']['_hash'], '7e5e46979cd59e83662703686acd8b82')

    nose.tools.eq_(param['feature_extraction']['stacking_formula'][0]['label'], 'mel')
    nose.tools.eq_(
        param['directories']['external']['log'],
        os.path.join(tempfile.gettempdir(), 'dcase_util_app', 'test')
    )

    # 4
    param = dcase_util.containers.AppParameterContainer(
        {
            'active_set': 'set1',
            'sets': [
                {
                    'set_id': 'set1',
                    'field1': 100
                },
                {
                    'set_id': 'set2',
                    'field1': 200
                },
                {
                    'set_id': 'set3',
                    'field1': 300
                },
            ],
            'defaults': {
                'field1': 1
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app')
    )
    param.process()
    nose.tools.eq_(param['_hash'], '99914b932bd37a50b983c5e7c90ae93b')
    nose.tools.eq_(param['field1'], 100)
    nose.tools.eq_(param['set_id'], 'set1')

    # 5
    param = dcase_util.containers.AppParameterContainer(
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
                'general': {
                    'field1': 1,
                },
                'feature_extractor2': {
                    'method': 'mel',
                    'fs': 44100
                },
                'feature_extractor2_method_parameters': {
                    'mel': {
                        'n_mels': 40
                    }
                },
                'feature_extractor': {
                    'recipe': 'mel;mfcc',
                    'fs': 44100
                },
                'feature_extractor_method_parameters': {
                    'mel': {
                        'n_mels': 40
                    },
                    'mfcc': {
                        'n_mfccs': 20
                    }
                }
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app'),
        method_dependencies={
            'FEATURE_EXTRACTOR': {
                'mel': None,
                'mfcc': 'FEATURE_EXTRACTOR.mel'
            }
        },
        section_labels={
            'FEATURE_EXTRACTOR': 'feature_extractor',
            'FEATURE_EXTRACTOR2': 'feature_extractor2',
        }
    )
    param.process(create_paths=True)

    nose.tools.eq_(param['general']['field1'], 100)
    nose.tools.eq_(
        param['path']['application']['base'],
        os.path.join(tempfile.gettempdir(), 'dcase_util_app', 'system')
    )

    nose.tools.eq_(
        param['path']['application']['feature_extractor'],
        os.path.join(tempfile.gettempdir(), 'dcase_util_app', 'system', 'feature_extractor')
    )

    nose.tools.eq_(param['feature_extractor2']['parameters']['n_mels'], 40)

    nose.tools.eq_(param['feature_extractor']['parameters']['mel']['n_mels'], 40)
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc']['n_mfccs'], 20)
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc']['dependency_method'], 'mel')
    nose.tools.eq_(param['feature_extractor']['parameters']['mfcc']['dependency_parameters']['n_mels'], 40)

    # 6
    param = dcase_util.containers.AppParameterContainer(
        {
            'active_set': 'set3',
            'sets': [
                {
                    'set_id': 'set1',
                    'field1': 100,
                    'field2': {
                        'field3': 12
                    }
                },
                {
                    'set_id': 'set2',
                    'field1': 200,
                    'field2': {
                        'field3': 1234
                    }
                },
                {
                    'set_id': 'set3',
                    'field1': 300,
                    'field2': {
                        'field3': 123456789
                    }
                },
            ],
            'defaults': {
                'field1': 1,
                'field2': {
                    'field3': 123
                }

            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app')
    )
    param.process()
    param.override(
        {
            'field1': 1000,
            'field2': {
                'field3': 222
            }
        }
    )
    nose.tools.eq_(param['field1'], 1000)
    nose.tools.eq_(param['field2']['field3'], 222)


def test_sets():
    param = dcase_util.containers.AppParameterContainer(
        {
            'active_set': 'set1',
            'sets': [
                {
                    'set_id': 'set1',
                    'section1': {
                        'field1': 100,
                        'field2': 100,
                    }
                },
                {
                    'set_id': 'set2',
                    'section1': {
                        'field1': 200,
                        'field3': 200,
                    }
                },
                {
                    'set_id': 'set3',
                    'section1': {
                        'field1': 300,
                        'field4': 300
                    }
                },
            ],
            'defaults': {
                'field1': 1
            }
        },
        app_base=os.path.join(tempfile.gettempdir(), 'dcase_util_app')
    )
    param.process()

    nose.tools.eq_(param['set_id'], 'set1')
    nose.tools.eq_(param['section1']['field1'], 100)
    nose.tools.eq_(param['section1']['field2'], 100)
    nose.tools.eq_(param['_hash'], '0afad0d180c377ea63b085bb6de7a9ee')

    nose.tools.eq_(param.set_ids(), ['set1', 'set2', 'set3'])

    param.update_parameter_set(set_id='set2')

    nose.tools.eq_(param['set_id'], 'set2')
    nose.tools.eq_(param['section1']['field1'], 200)
    nose.tools.eq_(param['section1']['field3'], 200)
    nose.tools.eq_(param['_hash'], 'd350d91259caa812c7eb363c8c065c39')

