#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import pkg_resources
import numpy


class Example(object):
    """Example files for tutorials"""
    example_folder = 'example_data'

    def __init__(self):
        pass

    @classmethod
    def audio_filename(cls):
        return pkg_resources.resource_filename(__name__, os.path.join(cls.example_folder, 'acoustic_scene.wav'))

    @classmethod
    def acoustic_scene_audio_filename(cls):
        return pkg_resources.resource_filename(__name__, os.path.join(cls.example_folder, 'acoustic_scene.wav'))

    @classmethod
    def audio_filename_mp3(cls):
        return pkg_resources.resource_filename(__name__, os.path.join(cls.example_folder, 'acoustic_scene.mp3'))

    @classmethod
    def acoustic_scene_audio_filename_mp3(cls):
        return pkg_resources.resource_filename(__name__, os.path.join(cls.example_folder, 'acoustic_scene.mp3'))

    @classmethod
    def audio_container(cls):
        from dcase_util.containers import AudioContainer
        container = AudioContainer(fs=44100)
        t = numpy.linspace(0, 2, 2 * container.fs, endpoint=False)
        x1 = numpy.sin(220 * 2 * numpy.pi * t)
        x2 = numpy.sin(440 * 2 * numpy.pi * t)
        container.data = numpy.vstack([x1, x2])

        return container

    @classmethod
    def audio_container_ch4(cls):
        from dcase_util.containers import AudioContainer
        container = AudioContainer(fs=44100)
        t = numpy.linspace(0, 2, 2 * container.fs, endpoint=False)
        x1 = numpy.sin(220 * 2 * numpy.pi * t)
        x2 = numpy.sin(440 * 2 * numpy.pi * t)
        x3 = numpy.sin(660 * 2 * numpy.pi * t)
        x4 = numpy.sin(880 * 2 * numpy.pi * t)
        container.data = numpy.vstack([x1, x2, x3, x4])

        return container

    @classmethod
    def scene_metadata_container(cls, filename=None):
        from dcase_util.containers import MetaDataContainer

        if filename is not None:
            return MetaDataContainer().load(
                filename=filename
            )

        else:
            return MetaDataContainer(
                [
                    {
                        'filename': cls.audio_filename(),
                        'scene_label': 'street'
                    },
                    {
                        'filename': 'test1.wav',
                        'scene_label': 'home'
                    },
                    {
                        'filename': 'test2.wav',
                        'scene_label': 'office'
                    },
                    {
                        'filename': 'test3.wav',
                        'scene_label': 'car'
                    },
                    {
                        'filename': 'test4.wav',
                        'scene_label': 'bus'
                    },
                ]
            )

    @classmethod
    def event_metadata_container(cls, filename=None):
        from dcase_util.containers import MetaDataContainer

        if filename is not None:
            return MetaDataContainer().load(
                filename=filename
            )

        else:
            return MetaDataContainer(
                [
                    {
                        'filename': cls.audio_filename(),
                        'scene_label': 'street',
                        'event_label': 'car',
                        'onset': 0.0,
                        'offset': 10.0
                    },
                    {
                        'filename': cls.audio_filename(),
                        'scene_label': 'street',
                        'event_label': 'bicycle',
                        'onset': 0.0,
                        'offset': 3.641
                    },
                    {
                        'filename': 'test1.wav',
                        'scene_label': 'street',
                        'event_label': 'car',
                        'onset': 3.0,
                        'offset': 5.0
                    },
                    {
                        'filename': 'test1.wav',
                        'scene_label': 'street',
                        'event_label': 'bicycle',
                        'onset': 6.0,
                        'offset': 7.0
                    },
                    {
                        'filename': 'test1.wav',
                        'scene_label': 'street',
                        'event_label': 'car',
                        'onset': 7.0,
                        'offset': 8.0
                    },
                ]
            )

    @classmethod
    def tag_metadata_container(cls, filename=None):
        from dcase_util.containers import MetaDataContainer

        if filename is not None:
            return MetaDataContainer().load(
                filename=filename
            )

        else:
            return MetaDataContainer(
                [
                    {
                        'filename': cls.audio_filename(),
                        'scene_label': 'street',
                        'tags': 'car, bicycle',
                    }
                ]
            )

    @classmethod
    def feature_container(cls, filename=None):
        if filename is None:
            filename = cls.audio_filename()

        from dcase_util.containers import AudioContainer, FeatureContainer
        from dcase_util.features import MelExtractor
        audio_container = AudioContainer(filename=filename).load().mixdown()
        mel_extractor = MelExtractor(fs=audio_container.fs)
        feature_data = mel_extractor.extract(audio_container.data)
        feature_container = FeatureContainer(
            data=feature_data,
            time_resolution=mel_extractor.hop_length_seconds
        )

        return feature_container

    @classmethod
    def feature_repository(cls, filename=None):
        from dcase_util.processors import ProcessingChain

        if filename is None:
            filename = cls.audio_filename()

        fs = 44100
        chain = ProcessingChain([
            {
                'processor_name': 'dcase_util.processors.MonoAudioReadingProcessor',
                'init_parameters': {
                    'fs': fs
                }
            },
            {
                'processor_name': 'dcase_util.processors.RepositoryFeatureExtractorProcessor',
                'init_parameters': {
                    'parameters': {
                        'mel': {},
                        'mfcc': {},
                        'mfcc_delta': {},
                        'mfcc_acceleration': {},
                        'zcr': {},
                        'rmse': {},
                        'centroid': {},
                    }
                }
            }
        ])
        return chain.process(filename=filename)