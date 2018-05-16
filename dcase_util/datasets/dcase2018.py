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
# DCASE 2018
# =====================================================
class DCASE2018_Task5_DevelopmentSet(AcousticSceneDataset):
    """Task 5, Monitoring of domestic activities based on multi-channel acoustics, development set

    This dataset a part of the SINS database:
        Dekkers G., Lauwereins S., Thoen B., Adhana M., Brouckxon H., Van den Bergh B., van Waterschoot T., Vanrumste B., Verhelst M., Karsmakers P. (2017). The SINS database for detection of daily activities in a home environment using an Acoustic Sensor Network. Detection and Classification of Acoustic Scenes and Events 2017 (accepted). DCASE Workshop. München, Germany, 16-17 November 2017.
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.

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

        source_url = 'https://zenodo.org/record/1247102/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'DCASE2018-task5-dev.doc.zip',
                'remote_bytes': 62900,
                'remote_md5': '4517a2560820af5da20e65e4a15a2d90',
                'filename': 'DCASE2018-task5-dev.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'DCASE2018-task5-dev.meta.zip',
                'remote_bytes': 984000,
                'remote_md5': '8fd269986c168db5562e7509e6dc033a',
                'filename': 'DCASE2018-task5-dev.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.1.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'ae81259fa58b4ed11babd52386cb035a',
                'filename': 'DCASE2018-task5-dev.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.2.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '88f2fa5306f76d6b4c4c82ce63798dc4',
                'filename': 'DCASE2018-task5-dev.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.3.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '6fe16ce76abf801aa64662b06eecdacf',
                'filename': 'DCASE2018-task5-dev.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.4.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '29892d9d444db700283058ea032ed18e',
                'filename': 'DCASE2018-task5-dev.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.5.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '05aad2d1c80bf4b73d8c23ade155e9df',
                'filename': 'DCASE2018-task5-dev.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.6.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'aa9bad6f4b877e5c4c74aa26f9e31c32',
                'filename': 'DCASE2018-task5-dev.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.7.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'b87d1fb20da8ce1f45d50c56bf35c560',
                'filename': 'DCASE2018-task5-dev.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.8.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'd214fe45d50a18a18ebe7051956b872b',
                'filename': 'DCASE2018-task5-dev.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.9.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '668631009d2b3bcf872bdd3d780446c6',
                'filename': 'DCASE2018-task5-dev.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.10.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '195c2d2a810c5c4bf6523541a8536a58',
                'filename': 'DCASE2018-task5-dev.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.11.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '1c92328c0fad3f9eb4a114bac89e8b19',
                'filename': 'DCASE2018-task5-dev.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.12.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'b651887afa7558bcbd79267fc40ea6c6',
                'filename': 'DCASE2018-task5-dev.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.13.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'f05a08f5c85633210be81c5ad5da3ef0',
                'filename': 'DCASE2018-task5-dev.audio.13.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.14.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '5c97b4ed12c167bf27bf3320fc3e665d',
                'filename': 'DCASE2018-task5-dev.audio.14.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.15.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '78370c4047caedfbc002b9d010ae4172',
                'filename': 'DCASE2018-task5-dev.audio.15.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.16.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '635747f2a89eb4fee971c53585bbac93',
                'filename': 'DCASE2018-task5-dev.audio.16.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.17.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'a166c76ef8af1eef1e2c1b193de127a6',
                'filename': 'DCASE2018-task5-dev.audio.17.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.18.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'ed326b2f5e8bb65553cea738a1a42250',
                'filename': 'DCASE2018-task5-dev.audio.18.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.19.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '429874b969a345e176136f2da6c6ec13',
                'filename': 'DCASE2018-task5-dev.audio.19.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.20.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'b5779fdfb14194c3823f981f573f4784',
                'filename': 'DCASE2018-task5-dev.audio.20.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.21.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '684874d4882945145642be946dc10f39',
                'filename': 'DCASE2018-task5-dev.audio.21.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.22.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '6d1767a8ef6e3c5978f86a5b372641b6',
                'filename': 'DCASE2018-task5-dev.audio.22.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.23.zip',
                'remote_bytes': 1800000000,
                'remote_md5': '4b727a3aca0b6b1456df46dd6196ae97',
                'filename': 'DCASE2018-task5-dev.audio.23.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]

        super(DCASE2018_Task5_DevelopmentSet, self).__init__(**kwargs)