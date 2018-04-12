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

        source_url = 'https://zenodo.org/record/1217452/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'DCASE2018-task5-dev.doc.zip',
                'remote_bytes': 118300,
                'remote_md5': '7c85f21c8d9e37a8de582c45acaa109b',
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
                'remote_md5': '1b00b50177bafef2f013e5a911578d22',
                'filename': 'DCASE2018-task5-dev.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.2.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'c75b1c1b3cc1340cfcace37559aed63f',
                'filename': 'DCASE2018-task5-dev.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.3.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '4cdc067f07093a8bd291a6626f679341',
                'filename': 'DCASE2018-task5-dev.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.4.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '548a05a7b9d8c4bb049fa0f50851e53d',
                'filename': 'DCASE2018-task5-dev.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.5.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'b17a8d90c5a01291841755360c5f3831',
                'filename': 'DCASE2018-task5-dev.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.6.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '6c0969113bc6181401557c2de82295f2',
                'filename': 'DCASE2018-task5-dev.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.7.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'd17fd35d44f6ff2969ebaf4e89a2ef1b',
                'filename': 'DCASE2018-task5-dev.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.8.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '7599fb9d73c95e48daef4dc956ae923c',
                'filename': 'DCASE2018-task5-dev.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.9.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '464276df297552db9501825b4d43a6c9',
                'filename': 'DCASE2018-task5-dev.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.10.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '8f33c008bc9c5f03b3942ebe7c0668da',
                'filename': 'DCASE2018-task5-dev.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.11.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'bd024a1664c0b47bbfcbffd1e49d88e2',
                'filename': 'DCASE2018-task5-dev.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.12.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '4d54480c449f658e9452d5d038e620d6',
                'filename': 'DCASE2018-task5-dev.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.13.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '189b882158f4ba7bc72d674408f9ca09',
                'filename': 'DCASE2018-task5-dev.audio.13.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.14.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'd7577ffb014f85e73f4e311af9a4ce2b',
                'filename': 'DCASE2018-task5-dev.audio.14.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.15.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'dbaa64f4659a291e9ef7fc364b526d6c',
                'filename': 'DCASE2018-task5-dev.audio.15.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.16.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'ce3a3a58c7b030baf8c9d566e3c6d8b4',
                'filename': 'DCASE2018-task5-dev.audio.16.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.17.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '5aed62b76c76c6672a827db992814b2f',
                'filename': 'DCASE2018-task5-dev.audio.17.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.18.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'cc0de32cf63da580e21c0c4644e85cb5',
                'filename': 'DCASE2018-task5-dev.audio.18.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.19.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '2adfcf66fb33ded9d64b806674031abf',
                'filename': 'DCASE2018-task5-dev.audio.19.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.20.zip',
                'remote_bytes': 2000000000,
                'remote_md5': 'b7aae8cfb445d7a76b01a052a3696c91',
                'filename': 'DCASE2018-task5-dev.audio.20.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.21.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '1040c4eaba91f2f379dc5b36ba6554b0',
                'filename': 'DCASE2018-task5-dev.audio.21.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.22.zip',
                'remote_bytes': 2000000000,
                'remote_md5': '2e3707dbbc175a736af067c39f1d8a60',
                'filename': 'DCASE2018-task5-dev.audio.22.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'DCASE2018-task5-dev.audio.23.zip',
                'remote_bytes': 1800000000,
                'remote_md5': '05575e618e64f942ed4e43fcce4c146c',
                'filename': 'DCASE2018-task5-dev.audio.23.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]

        super(DCASE2018_Task5_DevelopmentSet, self).__init__(**kwargs)