# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import collections
import hashlib
import os
import pickle
import sys

import numpy
import yaml
from six import iteritems
from tqdm import tqdm


from dcase_util.datasets import AcousticSceneDataset, SyntheticSoundEventDataset, SoundEventDataset
from dcase_util.containers import MetaDataContainer, MetaDataItem, OneToOneMappingContainer, \
    DictContainer, ParameterContainer
from dcase_util.utils import Path

# =====================================================
# DCASE 2017
# =====================================================


class DCASE2018_Task5_DevelopmentSet(AcousticSceneDataset):
    """Task 5, Monitoring of domestic activities based on multi-channel acoustics, development set

    This dataset a part of the SINS database:
    Dekkers G., Lauwereins S., Thoen B., Adhana M., Brouckxon H., Van den Bergh B., van Waterschoot T., Vanrumste B.,
    Verhelst M., Karsmakers P. (2017). The SINS database for detection of daily activities in a home environment
    using an Acoustic Sensor Network. Detection and Classification of Acoustic Scenes and Events 2017 (accepted).
    DCASE Workshop. München, Germany, 16-17 November 2017.
    A subset is used for "DCASE2018 - Task 5, Monitoring of domestic activities based on multi-channel acoustics"

    """

    def __init__(self,
                 storage_name='DCASE18-Task5-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'DCASE18-Task5-development'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'scene'
        kwargs['dataset_meta'] = {
            'authors': 'Gert Dekkers and Peter Karsmakers',
            'title': 'Task 5, Monitoring of domestic activities based on multi-channel acoustics, development set',
            'url': None,
            'audio_source': 'Daily living activities in a domestic environment',
            'audio_type': 'Natural',
            'recording_device_model': 'Silicon Labs (EFM32WG980) microcontroller',
            'microphone_model': 'Sonion N8AC03 MEMS microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 4

		#ToDo: add own challenge data, this is currently acoustic scene repo
        source_url = 'https://zenodo.org/record/1195855/files'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                #'remote_file': source_url + 'DCASE2018-task5-dev.doc.zip',
                'remote_bytes': 54796,
                'remote_md5': '2f7cb69f9d18c05c7d15ec384acb24b3',
                'filename': 'DCASE2018-task5-dev.doc.zip'
            },
            {
                'content_type': 'meta',
                #'remote_file': source_url + 'DCASE2018-task5-dev.meta.zip',
                'remote_bytes': 104321,
                'remote_md5': '07013ceb276a9f98bed9525549a4f0e9',
                'filename': 'DCASE2018-task5-dev.meta.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.1.zip',
                'remote_bytes': 1071445248,
                'remote_md5': '0bdec2752eb23344dff9ca58646b887b',
                'filename': 'DCASE2018-task5-dev.audio.1.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.2.zip',
                'remote_bytes': 1073453613,
                'remote_md5': 'b6151aa629a42ac5ad96f067040c7d2d',
                'filename': 'DCASE2018-task5-dev.audio.2.zip '
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.3.zip',
                'remote_bytes': 1073077819,
                'remote_md5': 'd4bdc9399a4e9e91a7f2a7e4f4b2f165',
                'filename': 'DCASE2018-task5-dev.audio.3.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.4.zip',
                'remote_bytes': 1072822038,
                'remote_md5': '3e98b910147a440a3af09139d8716135',
                'filename': 'DCASE2018-task5-dev.audio.4.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.5.zip',
                'remote_bytes': 1072644652,
                'remote_md5': 'f5179dc25d2a78999b6748da68e138e5',
                'filename': 'DCASE2018-task5-dev.audio.5.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.6.zip',
                'remote_bytes': 1072667888,
                'remote_md5': 'ceff680679ba99e59d7b82b5e376fc02',
                'filename': 'DCASE2018-task5-dev.audio.6.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.7.zip',
                'remote_bytes': 1073417661,
                'remote_md5': '5caa36893e8e431e43e1c2e3c2c95027',
                'filename': 'DCASE2018-task5-dev.audio.7.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.8.zip',
                'remote_bytes': 1072381222,
                'remote_md5': '455525547ebc9b3f5282946d487ac359',
                'filename': 'DCASE2018-task5-dev.audio.8.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.9.zip',
                'remote_bytes': 1072087738,
                'remote_md5': 'e6d739ba3529d059d08b017738ad6f7b',
                'filename': 'DCASE2018-task5-dev.audio.9.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.10.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '551a1d33fe6f1af4ef7c394407aa75e6',
                'filename': 'DCASE2018-task5-dev.audio.10.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.11.zip',
                'remote_bytes': 1046262120,
                'remote_md5': 'fd2db37cbe61f78bd157da6f00155a05',
                'filename': 'DCASE2018-task5-dev.audio.11.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.12.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '042757ec7b15d2f9104508d1191d5fcc',
                'filename': 'DCASE2018-task5-dev.audio.12.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.13.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '7d6e0ef9b1a8e1c80bc2b6ccc8f257d3',
                'filename': 'DCASE2018-task5-dev.audio.13.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.14.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '40c73c4e94cff908b3f3cd6d8e973bb2',
                'filename': 'DCASE2018-task5-dev.audio.14.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.15.zip',
                'remote_bytes': 1046262120,
                'remote_md5': 'b6a2c6845f2b31e872ad6272aa42f9ed',
                'filename': 'DCASE2018-task5-dev.audio.15.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.16.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '078522ab8034153871da143510ce462e',
                'filename': 'DCASE2018-task5-dev.audio.16.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.17.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '27713bb9c0baf66e9aa9bf3f09f79763',
                'filename': 'DCASE2018-task5-dev.audio.17.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.18.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '93ffda6c5c4c4ddc3742805a59efefc7',
                'filename': 'DCASE2018-task5-dev.audio.18.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.19.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '251ff2faeffbf1caf1c078b860322167',
                'filename': 'DCASE2018-task5-dev.audio.19.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.20.zip',
                'remote_bytes': 1046262120,
                'remote_md5': 'a064c1e27f86fc869485d84d5820c68f',
                'filename': 'DCASE2018-task5-dev.audio.20.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.21.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '273117dac491e254b426a2478533bcb8',
                'filename': 'DCASE2018-task5-dev.audio.21.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.22.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '2975760db7ebdc61de14f9a081d12766',
                'filename': 'DCASE2018-task5-dev.audio.22.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.23.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '5d46c05ed4b3e0fa162f76e475d853f2',
                'filename': 'DCASE2018-task5-dev.audio.23.zip'
            },
            {
                'content_type': 'audio',
                #'remote_file': source_url + 'DCASE2018-task5-dev.audio.24.zip',
                'remote_bytes': 1046262120,
                'remote_md5': 'cf111eab709a1414c5b3f71ee2561b04',
                'filename': 'DCASE2018-task5-dev.audio.24.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]

        super(DCASE2018_Task5_DevelopmentSet, self).__init__(**kwargs)