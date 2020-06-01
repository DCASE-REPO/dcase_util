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

from dcase_util.datasets import SoundDataset, AcousticSceneDataset, SyntheticSoundEventDataset, SoundEventDataset
from dcase_util.containers import MetaDataContainer, MetaDataItem, OneToOneMappingContainer, \
    DictContainer, ParameterContainer, AudioContainer
from dcase_util.utils import Path, FileFormat, is_jupyter
# Datasets released by Tampere University (TAU), formerly known as Tampere University of Technology (TUT).


# =====================================================
# DCASE 2020
# =====================================================
class TAUUrbanAcousticScenes_2020_Mobile_DevelopmentSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2020 Mobile Development dataset

    This dataset is used in DCASE2020 - Task 1, Acoustic scene classification / Subtask A / Development

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2020-mobile-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2020-mobile-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2020 Mobile, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural/Synthetic',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2020-mobile-development'
        source_url = 'https://zenodo.org/record/3819968/files/'
        kwargs['package_list'] = []

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 18066,
                'remote_md5': '175f40dc3fec144347abad4d2962b7ae',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 214159,
                'remote_md5': '6eae9db553ce48e4ea246e34e50a3cf5',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1726039031,
                'remote_md5': 'b1e85b8a908d3d6a6ab73268f385d5c8',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1782268370,
                'remote_md5': '4310a13cc2943d6ce3f70eba7ba4c784',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1870468865,
                'remote_md5': 'ed38956c4246abb56190c1e9b602b7b8',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1879413176,
                'remote_md5': '97ab8560056b6816808dedc044dcc023',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1823936584,
                'remote_md5': 'b50f5e0bfed33cd8e52cb3e7f815c6cb',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1827246144,
                'remote_md5': 'fbf856a3a86fff7520549c899dc94372',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1728630243,
                'remote_md5': '0dbffe7b6e45564da649378723284062',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1748646043,
                'remote_md5': 'bb6f77832bf0bd9f786f965beb251b2e',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1780487215,
                'remote_md5': 'a65596a5372eab10c78e08a0de797c9e',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1726068853,
                'remote_md5': '2ad595819ffa1d56d2de4c7ed43205a6',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1744480272,
                'remote_md5': '0ad29f7040a4e6a22cfd639b3a6738e5',
                'filename': filename_base + '.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.12.zip',
                'remote_bytes': 1738707195,
                'remote_md5': 'e5f4400c6b9697295fab4cf507155a2f',
                'filename': filename_base + '.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.13.zip',
                'remote_bytes': 1835797785,
                'remote_md5': '8855ab9f9896422746ab4c5d89d8da2f',
                'filename': filename_base + '.audio.13.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.14.zip',
                'remote_bytes': 1846390881,
                'remote_md5': '092ad744452cd3e7de78f988a3d13020',
                'filename': filename_base + '.audio.14.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.15.zip',
                'remote_bytes': 1869032508,
                'remote_md5': '4b5eb85f6592aebf846088d9df76b420',
                'filename': filename_base + '.audio.15.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.16.zip',
                'remote_bytes': 436971777,
                'remote_md5': '2e0a89723e58a3836be019e6996ae460',
                'filename': filename_base + '.audio.16.zip'
            },
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2020_Mobile_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

        if not item.source_label:
            item.source_label = os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[-1]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2020_Mobile_EvaluationSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2020 Mobile Evaluation dataset

    This dataset is used in DCASE2020 - Task 1, Acoustic scene classification / Subtask A / Evaluation

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2020-mobile-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2020-mobile-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2020 Mobile, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural/Synthetic',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] ='meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2020-mobile-evaluation'
        source_url = 'https://zenodo.org/record/3685828/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 8030,
                'remote_md5': '2f1ac2991111c6ee1d51bec6e27bd825',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 28811,
                'remote_md5': 'b8d9bb50faa282be170b81dc57e2b8b3',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1668607729,
                'remote_md5': '632841f6b1ef9ed962ea61f879967411',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1674217327,
                'remote_md5': '711fb0469f9b66669a300ebd1de24e9b',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1672649006,
                'remote_md5': '575e517b826a5faf020be22ce766adf8',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1665432028,
                'remote_md5': '5919fcbe217964756892a9661323c020',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1680713648,
                'remote_md5': 'c733767217f16c746f50796c65ca1dd6',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1670741441,
                'remote_md5': 'f39feb24910ffc97413e9c94b418f7ab',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1673394812,
                'remote_md5': '90bad61f14163146702d430cf8241932',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1433443122,
                'remote_md5': '4db5255382a5e5cab2d463c0d836b888',
                'filename': filename_base + '.audio.8.zip'
            }
        ]

        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2020_Mobile_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2020_3Class_DevelopmentSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2020 3Class Development dataset

    This dataset is used in DCASE2020 - Task 1, Low-Complexity Acoustic Scene Classification / Subtask B / Development

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2020-3class-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2020-3class-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2020 3Class, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2020-3class-development'
        source_url = 'https://zenodo.org/record/3670185/files/'
        kwargs['package_list'] = []

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 12026,
                'remote_md5': '1f50091832fef59ef79f7b7fcfc91525',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 154856,
                'remote_md5': '68de6dc1a81f8ef9c3a7851acda67786',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1657560336,
                'remote_md5': 'dab8b3564c1927eb8fc5906f61917ef9',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1654366875,
                'remote_md5': '82995465514560a3dff486ffc1b77cab',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1817911349,
                'remote_md5': 'fda4f39dae354d6eea8662c4f8228b70',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1818799452,
                'remote_md5': '6795666e7e872114a0bd8b7dea333761',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1803128209,
                'remote_md5': '0920299dd8600c3fec421af79588535b',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1777403835,
                'remote_md5': '65fab659046ef15c8ae3e15025737551',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1747963586,
                'remote_md5': '55dd8e47bd868611d5e7bacad57b96b5',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1720046267,
                'remote_md5': '9fdae7f1658160d6c4d844d642c1e762',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1667115976,
                'remote_md5': '6178c22394a3bf0f67b2c47d1690c6d7',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1615255858,
                'remote_md5': 'd054358cfd7c9b568c03c2c87f6461c4',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1671803243,
                'remote_md5': 'fcbb4d5835f030819e099fc0701932dc',
                'filename': filename_base + '.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.12.zip',
                'remote_bytes': 1660209697,
                'remote_md5': '92e6347acf82226d1458859b7ca281ba',
                'filename': filename_base + '.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.13.zip',
                'remote_bytes': 1673491310,
                'remote_md5': '99570283c1dd64aaf954eb526fd2e394',
                'filename': filename_base + '.audio.13.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.14.zip',
                'remote_bytes': 1660091069,
                'remote_md5': '13efa3cd2084ccdba76b1087a4fac57f',
                'filename': filename_base + '.audio.14.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.15.zip',
                'remote_bytes': 1675136726,
                'remote_md5': '1e3cc2fed352cf9331a815f2c969458a',
                'filename': filename_base + '.audio.15.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.16.zip',
                'remote_bytes': 1648250719,
                'remote_md5': 'd232c47c39d9f2683ef805565ad9b068',
                'filename': filename_base + '.audio.16.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.17.zip',
                'remote_bytes': 1693567638,
                'remote_md5': '75bd9417b8134476122c7f8a8fb11d4b',
                'filename': filename_base + '.audio.17.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.18.zip',
                'remote_bytes': 1731103523,
                'remote_md5': 'ae04e9ed8da615b2f1f9aa5e02b9c3f2',
                'filename': filename_base + '.audio.18.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.19.zip',
                'remote_bytes': 1745163308,
                'remote_md5': '284fe9195bdbd5159438bac5ea4595e1',
                'filename': filename_base + '.audio.19.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.20.zip',
                'remote_bytes': 1774048510,
                'remote_md5': '7e2f15f5f19114ffcb0b94f0a15fa272',
                'filename': filename_base + '.audio.20.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.21.zip',
                'remote_bytes': 1331132724,
                'remote_md5': 'e5d0491071d6a652fe3693586770fdc0',
                'filename': filename_base + '.audio.21.zip'
            },
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2020_3Class_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

        if not item.source_label:
            item.source_label = os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[-1]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2020_3Class_EvaluationSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2020 3Class Evaluation dataset

    This dataset is used in DCASE2020 - Low-Complexity Acoustic Scene Classification / Subtask B / Evaluation

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2020-3class-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2020-3class-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2020 Mobile, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] ='meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2020-3class-evaluation'
        source_url = 'https://zenodo.org/record/3685835/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 8040,
                'remote_md5': '68a8e716297ed3dc465f904477d139f4',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 21179,
                'remote_md5': '6ec871d4f4f8d92171d2f60e7aa157f7',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1665288283,
                'remote_md5': 'fb976f1075f42d8e4d856cc10bd52435',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1682331176,
                'remote_md5': 'e6a90881ca11c3da660d94477c530790',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1674975498,
                'remote_md5': 'b70694a133d785af635de8dfdf7fde66',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1664063924,
                'remote_md5': 'dcb5bea4fe1ce3f4707d35f19ea6009e',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1667987928,
                'remote_md5': '1ebfcca602a91187f375e4d6cb448c80',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1677609880,
                'remote_md5': '31d1843f3dc150bbbeca3424e8ca5e1e',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1676918579,
                'remote_md5': '7818751f0900b5792be7065c7b7c2743',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1671901774,
                'remote_md5': 'f75aba3f7f2d4afb46e9ea5479716498',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1684951879,
                'remote_md5': '75dc6da551f012ed26f91fd0ed37b828',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1689314640,
                'remote_md5': '8527a1a990503ccf06ad061c0a82ff3c',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1666392095,
                'remote_md5': 'e401f04f505fa41316c2b1a27c62c1d7',
                'filename': filename_base + '.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.12.zip',
                'remote_bytes': 1678306939,
                'remote_md5': '16399ebaeb036126c38aee6a56e66d07',
                'filename': filename_base + '.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.13.zip',
                'remote_bytes': 756614443,
                'remote_md5': '694f9abe00682f05929e6dbbd160e0e2',
                'filename': filename_base + '.audio.13.zip'
            }
        ]

        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2020_3Class_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


# =====================================================
# DCASE 2019
# =====================================================


class TAUUrbanAcousticScenes_2019_DevelopmentSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Development dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask A / Development

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2019-development'
        source_url = 'https://zenodo.org/record/2589280/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 11299,
                'remote_md5': '1f6879544e80da70099a191613e7e51f',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 156863,
                'remote_md5': '09782f2097e4735687af73c44919329c',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1657550587,
                'remote_md5': 'aca4ebfd9ed03d5f747d6ba8c24bc728',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1666219450,
                'remote_md5': 'c4f170408ce77c8c70c532bf268d7be0',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1817901591,
                'remote_md5': 'c7214a07211f10f3250290d05e72c37e',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1821710642,
                'remote_md5': 'a6a62110f6699cf4432072acb1dffda6',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1803118466,
                'remote_md5': '091a0b6d3c84b8e60e46940aa7d4a8a0',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1789566029,
                'remote_md5': '114f4ca13e074391b98a1cfd8140de65',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1747953866,
                'remote_md5': '5951dd2968f7a514e2afbe279c4f060d',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1728724513,
                'remote_md5': 'b0b63dc95b327e1509857c8d8a663cc3',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1667106209,
                'remote_md5': '3c32a693a6b111ffb957be3c1dd22e9b',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1632636175,
                'remote_md5': '0ffbf60006da520cc761fb74c878b98b',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1671793546,
                'remote_md5': '599055d93b4c11057c29be2df54538d4',
                'filename': filename_base + '.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.12.zip',
                'remote_bytes': 1672592150,
                'remote_md5': '98b8d162ff3665695c4c910e6c372cc8',
                'filename': filename_base + '.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.13.zip',
                'remote_bytes': 1673481614,
                'remote_md5': 'a356c08b1a5a21d433eba37ef87587f4',
                'filename': filename_base + '.audio.13.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.14.zip',
                'remote_bytes': 1666137450,
                'remote_md5': 'f8969771e7faf7dd471d1cf78b0cf011',
                'filename': filename_base + '.audio.14.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.15.zip',
                'remote_bytes': 1675127004,
                'remote_md5': '4758c4b0fb7484faa632266e78850820',
                'filename': filename_base + '.audio.15.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.16.zip',
                'remote_bytes': 1648240966,
                'remote_md5': 'a18acad9ede8ea76574216feb887f0bc',
                'filename': filename_base + '.audio.16.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.17.zip',
                'remote_bytes': 1698414214,
                'remote_md5': '1af7703484632f340da5c33662dc9632',
                'filename': filename_base + '.audio.17.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.18.zip',
                'remote_bytes': 1731093704,
                'remote_md5': 'b67402bf3e08f4da394a7c18756c0fd2',
                'filename': filename_base + '.audio.18.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.19.zip',
                'remote_bytes': 1745153640,
                'remote_md5': '035db315f19106eb848b6f9b32bcc47c',
                'filename': filename_base + '.audio.19.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.20.zip',
                'remote_bytes': 1774038704,
                'remote_md5': '9cb28c74911bf8a3eadcf53f50a5b5d6',
                'filename': filename_base + '.audio.20.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.21.zip',
                'remote_bytes': 1333808800,
                'remote_md5': '0e44ed85c88ec036a9725b4dd1dfaea0',
                'filename': filename_base + '.audio.21.zip'
            },
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_LeaderboardSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Leaderboard dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask A / Public leaderboard

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-leaderboard',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-leaderboard'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019, public leaderboard dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2019-leaderboard'
        source_url = 'https://zenodo.org/record/2672993/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7610,
                'remote_md5': '826ede1a356e40ed6c80d873a0e10a70',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 2943,
                'remote_md5': 'fa3451868a2adf9d8a91882604a2d9b5',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1720302369,
                'remote_md5': 'a5daa0df61c6fbc65b1e70f98d728ea3',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1256474601,
                'remote_md5': 'c57c37a7ab6a32233583e39ec8cfafd5',
                'filename': filename_base + '.audio.2.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_LeaderboardSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_EvaluationSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Evaluation dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask A / Evaluation

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] ='meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2019-evaluation'
        source_url = 'https://zenodo.org/record/3063822/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7714,
                'remote_md5': '2fd4dc78299fc0d05212ca43dd89d922',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 17611,
                'remote_md5': '0b42d3c337b29d2efe50edd1e9496d7e',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1718932778,
                'remote_md5': '3dfc50f8dc46f4a83a2e9cf2083d1c2a',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1720407092,
                'remote_md5': 'cc3d2a4b8e98ce0122317e401d0c6b7d',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1729024580,
                'remote_md5': 'a4815bdfd889a59f71c586cc834fc5e8',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1722331995,
                'remote_md5': 'd85f72ef7ae8a60b297da9e5bf478356',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1721621397,
                'remote_md5': '73c84daf879db5cc4811808794e373de',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1727147531,
                'remote_md5': '39d3cda72353ee9da88b78164350ff9f',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1717588287,
                'remote_md5': 'bd6fbf0d9324d1faa72968c162b574d7',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1718370134,
                'remote_md5': 'd7b4b62156f458865e2bd063b3da39e8',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1719960073,
                'remote_md5': '7dbc037eca8d1234de8cd677853f72e4',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1716083192,
                'remote_md5': '9a0b1e0d2647f6241d7b7c0649855cc7',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 643469805,
                'remote_md5': 'c2ae0b8d9270d964f8c1d8b5298fea72',
                'filename': filename_base + '.audio.11.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Mobile_DevelopmentSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Mobile Development dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask B / Development

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-mobile-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-mobile-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Mobile, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2019-mobile-development'
        source_url = 'https://zenodo.org/record/2589332/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 13293,
                'remote_md5': 'b69c1b456c4376b9760965b5d4bd7167',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 186595,
                'remote_md5': '9b2e36283882bf24be9817465d1e86cd',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1651985891,
                'remote_md5': '6bf7607097b448745926994970260dbd',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1802058101,
                'remote_md5': '54f9966def3768297a028f757fd217d5',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1795398745,
                'remote_md5': '1daa259ede9ab2b83246f49bd2f4e547',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1740187784,
                'remote_md5': '3a4c954dec030598ed5b9f0f2415024d',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1645958850,
                'remote_md5': '1f6b9e0b8c5699946466fe31fb795e68',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1649238738,
                'remote_md5': 'a857f69cbbeb56fcf123d5f0bc322786',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1653875791,
                'remote_md5': 'adf9802b1f46f6ce5f9f668cd5be8a1b',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1658513966,
                'remote_md5': '97134c6cdacc856652368997202ef06f',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1656793838,
                'remote_md5': '3caaed1a238354e9a885318e222fa77a',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1732442073,
                'remote_md5': '3bd9d1fe203111aa164d22707fbbc9f6',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1696211829,
                'remote_md5': '93f3dfbcdfce06d43cc3131ee712ba38',
                'filename': filename_base + '.audio.11.zip'
            },
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Mobile_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

        if not item.source_label:
            item.source_label = os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[-1]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Mobile_LeaderboardSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Mobile Leaderboard dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask B / Leaderboard

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-mobile-leaderboard',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-mobile-leaderboard'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Mobile, leaderboard dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] = 'meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2019-mobile-leaderboard'
        source_url = 'https://zenodo.org/record/2673004/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7996,
                'remote_md5': 'afa38519cd0f46ca1522fc48530ea155',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 2957,
                'remote_md5': 'e03c790e5d4905e066a4443e48d61395',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.zip',
                'remote_bytes': 1355731744,
                'remote_md5': 'e16a2f1e2d29aa7d91d9d5a24e89afb4',
                'filename': filename_base + '.audio.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Mobile_LeaderboardSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Mobile_EvaluationSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Mobile Evaluation dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask B / Evaluation

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-mobile-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-mobile-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Mobile, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] = 'meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2019-mobile-evaluation'
        source_url = 'https://zenodo.org/record/3063980/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 8175,
                'remote_md5': '33a02e52d6106108c28508b68f7d640d',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 26006,
                'remote_md5': '8f785eae67956bb324fcfbfa0968d23a',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1785111869,
                'remote_md5': 'acf5a19a2ab22538cb4f6da0424b1310',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1772146254,
                'remote_md5': 'a1634f3931423de49bfe661ba5309213',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1784729132,
                'remote_md5': 'c499dd9eea58374f9dd4c0b98bf550b8',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1774420842,
                'remote_md5': '05fae4928e1e6f21a06e9954f2150281',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1782016189,
                'remote_md5': '1da8f0a3eadd0ffd062f90e0bdad6700',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1768877804,
                'remote_md5': '6be98493b3bbdc930d9aebb0cdd211e0',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1780650780,
                'remote_md5': '5f5642e5d76f937103a94a62a6d03653',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 261946588,
                'remote_md5': '01a0f15937be9e8e63069ee97c31cca4',
                'filename': filename_base + '.audio.8.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Mobile_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Openset_DevelopmentSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Open set Development dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask C / Development

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-openset-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Openset, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['evaluation_setup_file_extension'] = 'csv'
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TAU-urban-acoustic-scenes-2019-openset-development'
        source_url = 'https://zenodo.org/record/2591503/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 12429,
                'remote_md5': '63b71eaedc47b474b2ba18f75c3a54b9',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 179091,
                'remote_md5': '174da059848170d2d25c71aa09db1934',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1650482337,
                'remote_md5': 'be774883d75909c24c49d9b5c40defb0',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1821682901,
                'remote_md5': 'cfe9e18456fb44b32ac642b24f0e9627',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1781169001,
                'remote_md5': '3a67e8ddc25beabc573d438817368595',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1705677749,
                'remote_md5': '725d7461435acb1ec80ca22d861a7a93',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1627912724,
                'remote_md5': 'df84114022af902862d149ee7a9c792e',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1657521956,
                'remote_md5': '0ac730ddde0a7a2f6b4e56a374470658',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1653158447,
                'remote_md5': '989e79b5c0722ca503ae9971521c0827',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1671146824,
                'remote_md5': '97e5b82493a746d55670c9202c5ac931',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1739366246,
                'remote_md5': '1248c6046e7f41d816aa546e916a390a',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1694793978,
                'remote_md5': '47c288125a3bf1d36383c17017290a3b',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 838339363,
                'remote_md5': 'fcab84b265b81d87e0afc5f280c680ae',
                'filename': filename_base + '.audio.11.zip'
            },
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Openset_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Openset_LeaderboardSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Open set Leaderboard dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask C / Leaderboard

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-openset-leaderboard',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-openset-leaderboard'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Openset, leaderboard dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2019-openset-leaderboard'
        source_url = 'https://zenodo.org/record/2673006/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7741,
                'remote_md5': 'fb85a875fb4379f6c1ef7502a6323957',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 2959,
                'remote_md5': 'df9711a4d6565118077a74b1faa6ce25',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.zip',
                'remote_bytes': 1377552625,
                'remote_md5': '5ab403c0176612b4abb1865a2c807787',
                'filename': filename_base + '.audio.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Openset_LeaderboardSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TAUUrbanAcousticScenes_2019_Openset_EvaluationSet(AcousticSceneDataset):
    """TAU Urban Acoustic Scenes 2019 Open set Evaluation dataset

    This dataset is used in DCASE2019 - Task 1, Acoustic scene classification / Subtask C / Evaluation

    """

    def __init__(self,
                 storage_name='TAU-urban-acoustic-scenes-2019-openset-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TAU-urban-acoustic-scenes-2019-openset-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TAU Urban Acoustic Scenes 2019 Openset, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'
        kwargs['check_meta'] = False

        filename_base = 'TAU-urban-acoustic-scenes-2019-openset-evaluation'
        source_url = 'https://zenodo.org/record/3064132/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7938,
                'remote_md5': '01439c436b91ba20e8b1bf29e1629a67',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 17627,
                'remote_md5': 'e4b6f2e48b8ff7e67803109d0e24c4c3',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1721556534,
                'remote_md5': 'fce651cba35d38d9d42e8656d0eb1e92',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1723583372,
                'remote_md5': '65e17fbbb7071c260937639e0e3a6dca',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1719828721,
                'remote_md5': 'a198d2c62a54bd4b19514e35b6cd0126',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1722587566,
                'remote_md5': '9e6d628bbd063fc46c12325837641732',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1316716762,
                'remote_md5': 'c66f44d78b5435cc5d27cb7c00349c09',
                'filename': filename_base + '.audio.5.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TAUUrbanAcousticScenes_2019_Openset_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


# =====================================================
# DCASE 2018
# =====================================================


class TUTUrbanAcousticScenes_2018_DevelopmentSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Development dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask A / Development

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-development'
        source_url = 'https://zenodo.org/record/1228142/files/'

        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 10517,
                'remote_md5': '28a4a9c46a6f46709ecc8eece365a3a4',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 69272,
                'remote_md5': 'e196065ee83c07af03a11a310364377d',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1657811579,
                'remote_md5': '62f97087c447e29def8716204469bf89',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1783489370,
                'remote_md5': '8e569a92025d82bff6b02b956d7c6dc9',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1809675304,
                'remote_md5': '00d2020582a4535af5e65322fb2bad56',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1756582525,
                'remote_md5': 'd691eb4271f83ba6ba9a28797accc497',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1724002546,
                'remote_md5': 'c4d64b5483b60f85e9fe080b3435a6be',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1645753049,
                'remote_md5': '2f0feee78f216697eb19497714d97642',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1671903917,
                'remote_md5': '07cfefe80a0731de6819181841239f3a',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1673304843,
                'remote_md5': '213f3c012859c2e9dcb74aacc8558458',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1674839259,
                'remote_md5': 'b724442b09abcb3bd095ebff497cef85',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1662932947,
                'remote_md5': 'a27a32fa52e283ed8013375b8a16f269',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 1751473843,
                'remote_md5': '7073a121e825ffef99832507f30d6644',
                'filename': filename_base + '.audio.11.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.12.zip',
                'remote_bytes': 1742332198,
                'remote_md5': '6567aa61db12776568b6267ce122fb18',
                'filename': filename_base + '.audio.12.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.13.zip',
                'remote_bytes': 798990513,
                'remote_md5': 'd00eeb2db0e093d8975521323a96c519',
                'filename': filename_base + '.audio.13.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TUTUrbanAcousticScenes_2018_LeaderboardSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Leaderboard dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask A / Public leaderboard

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-leaderboard',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-leaderboard'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018, public leaderboard dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-leaderboard'
        source_url = 'https://zenodo.org/record/1245181/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7592,
                'remote_md5': 'ec83e81f5c25c6f3fbaaab2930d74d5d',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 2936,
                'remote_md5': '2b52300b9de2e69cce8849b5d1daba28',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1717617702,
                'remote_md5': '33523d95683f80e488f318500c793431',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1256040072,
                'remote_md5': 'dee89b1b99fb3f2600250008ef840b18',
                'filename': filename_base + '.audio.2.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_LeaderboardSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TUTUrbanAcousticScenes_2018_EvaluationSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Evaluation dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask A / Evaluation

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Zoom F8',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] ='meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-evaluation'
        source_url = 'https://zenodo.org/record/1293883/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 7702,
                'remote_md5': '05edd37e0da5f301e86b1dbd2ccae191',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 8840,
                'remote_md5': 'b519d0b2addcb5e8569ec0c44df14e3e',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1718662668,
                'remote_md5': '4fd51d1365df3d13735b86a51ff8840b',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1715801158,
                'remote_md5': 'f6916f68a16b25f128badff441f80d8a',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1718666070,
                'remote_md5': '05a6f5d1259a4da49cda32f534c71cc6',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1716820790,
                'remote_md5': 'fcdceb6a022d698064e5537edbbd6664',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1716577566,
                'remote_md5': 'ff94b9abc4f01bf2dd9a2aca79d8590d',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 320850287,
                'remote_md5': '3dd86135fb4df726f6036ffafe0dff88',
                'filename': filename_base + '.audio.6.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Mobile Development dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask B

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-mobile-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-mobile-development'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018 Mobile, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-mobile-development'
        source_url = 'https://zenodo.org/record/1228235/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 12144,
                'remote_md5': '5694e9cdffa11cef8ec270673dc19ba0',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 88425,
                'remote_md5': 'b557b6d5d620aa4f15564ab38f1594d4',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1692337547,
                'remote_md5': 'd6f2671af84032b97f393354c124517d',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1769203601,
                'remote_md5': 'db8b3603af5d4e559869a592930a7620',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1674610746,
                'remote_md5': '703bf73523a6ad1f40d4923cb8ba3ff0',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1634599587,
                'remote_md5': '18af04ab5d6f15a72c66f16bfec0ca07',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1640894390,
                'remote_md5': 'a579efb032f209a7e77fe22e4808e9ca',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1693974078,
                'remote_md5': 'c2c56691047b3be3d98cb0ffd6858d9f',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1165383562,
                'remote_md5': 'e182e5300867f4ed4b580389cc5b931e',
                'filename': filename_base + '.audio.7.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if not item.identifier:
            item.identifier = '-'.join(os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[1:-2])

        if not item.source_label:
            item.source_label = os.path.splitext(os.path.split(item.filename)[-1])[0].split('-')[-1]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TUTUrbanAcousticScenes_2018_Mobile_LeaderboardSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Mobile Leaderboard dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask B / Public leaderboard

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-mobile-leaderboard',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-mobile-leaderboard'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018 Mobile, public leaderboard dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-mobile-leaderboard'
        source_url = 'https://zenodo.org/record/1245184/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 8032,
                'remote_md5': '7d7017a1f69f1ee91fe3c55ad9752d48',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 5994,
                'remote_md5': '36fee45acb480f75f9f9d0eb2bf58c08',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1595184268,
                'remote_md5': '5340cac647914b1dbac0058384306bdd',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 937889790,
                'remote_md5': 'd9126d1920f1a4b59a5368f8cf1d04b5',
                'filename': filename_base + '.audio.2.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_Mobile_LeaderboardSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self


class TUTUrbanAcousticScenes_2018_Mobile_EvaluationSet(AcousticSceneDataset):
    """TUT Urban Acoustic Scenes 2018 Mobile Evaluation dataset

    This dataset is used in DCASE2018 - Task 1, Acoustic scene classification / Subtask B / Evaluation

    """

    def __init__(self,
                 storage_name='TUT-urban-acoustic-scenes-2018-mobile-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-urban-acoustic-scenes-2018-mobile-evaluation'

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
            'authors': 'Toni Heittola, Annamaria Mesaros, and Tuomas Virtanen',
            'title': 'TUT Urban Acoustic Scenes 2018 Mobile, evaluation dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Various',
            'microphone_model': 'Various',
            'licence': 'free non-commercial'
        }
        kwargs['reference_data_present'] = False
        kwargs['crossvalidation_folds'] = 1
        kwargs['meta_filename'] = 'meta.csv'

        filename_base = 'TUT-urban-acoustic-scenes-2018-mobile-evaluation'
        source_url = 'https://zenodo.org/record/1293901/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + filename_base + '.doc.zip',
                'remote_bytes': 8153,
                'remote_md5': '388c33165041f7f485f5d02f8c79e5cb',
                'filename': filename_base + '.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + filename_base + '.meta.zip',
                'remote_bytes': 37135,
                'remote_md5': 'ee32d053b658994f2836525884ca4752',
                'filename': filename_base + '.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.1.zip',
                'remote_bytes': 1661884583,
                'remote_md5': '1e3142533721c67397363f73cf9d02d6',
                'filename': filename_base + '.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.2.zip',
                'remote_bytes': 1653193397,
                'remote_md5': '042ee6d3769ddcf5660be5b1ccbf27c7',
                'filename': filename_base + '.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.3.zip',
                'remote_bytes': 1649013685,
                'remote_md5': '1b1a88f891e29cdac06ddb4c5f3c114c',
                'filename': filename_base + '.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.4.zip',
                'remote_bytes': 1659605017,
                'remote_md5': 'de97d70ba7dacf37ce0c0e94d38ae068',
                'filename': filename_base + '.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.5.zip',
                'remote_bytes': 1662372447,
                'remote_md5': 'd5a9d8c9da6f14e35e43723c31cc2d2f',
                'filename': filename_base + '.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.6.zip',
                'remote_bytes': 1657254960,
                'remote_md5': '168f0dbe69a2b314b846490914e8e3f1',
                'filename': filename_base + '.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.7.zip',
                'remote_bytes': 1663811780,
                'remote_md5': 'b77db16f4615ac0f8bab2a1cb45edf0c',
                'filename': filename_base + '.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.8.zip',
                'remote_bytes': 1668115140,
                'remote_md5': 'e7bf06ab5af19e535f0614359a0fea10',
                'filename': filename_base + '.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.9.zip',
                'remote_bytes': 1657413208,
                'remote_md5': 'f4f958f7112e2901660573df3f4ed649',
                'filename': filename_base + '.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.10.zip',
                'remote_bytes': 1655476185,
                'remote_md5': 'c1c1f61f015cf492e426c9feb98b4d11',
                'filename': filename_base + '.audio.10.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + filename_base + '.audio.11.zip',
                'remote_bytes': 11141229,
                'remote_md5': '0a2d966628facf60ee875b1fbddfa11f',
                'filename': filename_base + '.audio.11.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTUrbanAcousticScenes_2018_Mobile_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and self.reference_data_present:
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='train',
                        fold=fold
                    )
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(
                        setup_part='evaluate',
                        fold=fold
                    )
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(
                filename=self.meta_file
            )

            # Load meta and cross validation
            self.load()

        return self

# =====================================================
# DCASE 2017
# =====================================================


class TUTAcousticScenes_2017_DevelopmentSet(AcousticSceneDataset):
    """TUT Acoustic scenes 2017 development dataset

    This dataset is used in DCASE2017 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='TUT-acoustic-scenes-2017-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2017-development'

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
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Acoustic Scenes 2017, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 4

        source_url = 'https://zenodo.org/record/400515/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.doc.zip',
                'remote_bytes': 54796,
                'remote_md5': '2065495aaf3f1103e795c9899e2af1df',
                'filename': 'TUT-acoustic-scenes-2017-development.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.meta.zip',
                'remote_bytes': 104321,
                'remote_md5': '9007fd4772d816590c5db5f5e9568f5d',
                'filename': 'TUT-acoustic-scenes-2017-development.meta.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.error.zip',
                'remote_bytes': 1432,
                'remote_md5': '802c700b021769e52a2c1e3b9c117a1b',
                'filename': 'TUT-acoustic-scenes-2017-development.error.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.1.zip',
                'remote_bytes': 1071445248,
                'remote_md5': '251325a9afaaad0326ad1c57f57d514a',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.2.zip',
                'remote_bytes': 1073453613,
                'remote_md5': 'c26861e05147dc319b4250eb103d9d99',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.3.zip',
                'remote_bytes': 1073077819,
                'remote_md5': 'a4815775f8a5e629179726ee4cd4f55a',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.4.zip',
                'remote_bytes': 1072822038,
                'remote_md5': '1732b03afe8c53ef8bba80ba14766e57',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.5.zip',
                'remote_bytes': 1072644652,
                'remote_md5': '611be754a0c951185c6ae4b7643c19a0',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.6.zip',
                'remote_bytes': 1072667888,
                'remote_md5': '165a201db800d3ea76fce5a9c2bd97d7',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.7.zip',
                'remote_bytes': 1073417661,
                'remote_md5': 'c7d79db84264401c0f8680dcc36013ad',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.8.zip',
                'remote_bytes': 1072381222,
                'remote_md5': '35043f25123439392338c790494c7a19',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.9.zip',
                'remote_bytes': 1072087738,
                'remote_md5': '0805dcf5d8e6871dc9610182b2efb93a',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.9.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-development.audio.10.zip',
                'remote_bytes': 1046262120,
                'remote_md5': '5df83a191295a04e290b125c634e13e7',
                'filename': 'TUT-acoustic-scenes-2017-development.audio.10.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTAcousticScenes_2017_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = raw_filename.split('_')[0]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = collections.OrderedDict()
            for fold in self.folds():
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(setup_part='train', fold=fold)
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(setup_part='evaluate', fold=fold)
                ).load()

                # Process, make sure each file is included only once.
                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item
            # Save meta
            MetaDataContainer(list(meta_data.values())).save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self


class TUTAcousticScenes_2017_EvaluationSet(AcousticSceneDataset):
    """TUT Acoustic scenes 2017 evaluation dataset

    This dataset is used in DCASE2017 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='TUT-acoustic-scenes-2017-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2017-evaluation'

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
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Acoustic Scenes 2017, development dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = None

        source_url = 'https://zenodo.org/record/1040168/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.doc.zip',
                'remote_bytes': 53687,
                'remote_md5': '53709a07416ea3b617c02fcf67dbeb9c',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.meta.zip',
                'remote_bytes': 4473,
                'remote_md5': '200eee9493e8044403e1326e3d05cfde',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.audio.1.zip',
                'remote_bytes': 1071856687,
                'remote_md5': '3d6dda4445871e9544e0fefe7d14c7d9',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.audio.2.zip',
                'remote_bytes': 1073362972,
                'remote_md5': '4085ef5fa286f2169074993a4e405953',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.audio.3.zip',
                'remote_bytes': 1071521152,
                'remote_md5': 'cac432579e7cf2dff0aec7aaed248956',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.audio.4.zip',
                'remote_bytes': 382756463,
                'remote_md5': '664bf09c3d24bd26c6b587f1d709de36',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.audio.4.zip'
            },
        ]
        kwargs['audio_paths'] = ['audio']

        super(TUTAcousticScenes_2017_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, filename_map=None, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        filename_map : OneToOneMappingContainer
            Filename map
            Default value None

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if filename_map and item.filename in filename_map:
            filename_mapped = filename_map.map(item.filename)
            item.identifier = os.path.split(filename_mapped)[1].split('_')[0]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            if os.path.isfile(self.evaluation_setup_filename(setup_part='evaluate')):
                meta_data = collections.OrderedDict()

                # Read files in
                data = MetaDataContainer(
                    filename=os.path.join(self.evaluation_setup_path, 'evaluate.txt')
                ).load()

                # Load filename mapping
                map_filename = os.path.join(self.evaluation_setup_path, 'map.txt')
                if os.path.exists(map_filename):
                    filename_map = OneToOneMappingContainer(filename=map_filename).load()
                else:
                    filename_map = {}

                for item in data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False,
                            filename_map=filename_map
                        )

                        meta_data[item.filename] = item

                # Save meta
                MetaDataContainer(list(meta_data.values())).save(filename=self.meta_file)

                # Load meta and cross validation
                self.load()

        return self


class TUTAcousticScenes_2017_FeaturesSet(AcousticSceneDataset):
    """TUT Acoustic scenes 2017 features dataset
    """

    def __init__(self,
                 storage_name='TUT-acoustic-scenes-2017-features',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2017-features'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'features', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'scene'
        kwargs['dataset_meta'] = {
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Acoustic Scenes 2017, features dataset',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 1

        source_url = 'https://zenodo.org/record/1324390/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-features.doc.zip',
                'remote_bytes': 33513,
                'remote_md5': 'bdbfd4a42a4d911c303cd27c28e22471',
                'filename': 'TUT-acoustic-scenes-2017-features.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-features.meta.zip',
                'remote_bytes': 59467,
                'remote_md5': '78458855f531e98951c34c9e904b2fe9',
                'filename': 'TUT-acoustic-scenes-2017-features.meta.zip'
            },
            {
                'content_type': 'features',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-features.features.zip',
                'remote_bytes': 881979236,
                'remote_md5': 'c9362bebb999afed363e563b19702f34',
                'filename': 'TUT-acoustic-scenes-2017-features.features.zip'
            }
        ]
        kwargs['audio_paths'] = []
        kwargs['meta_filename'] = 'meta.csv'
        kwargs['evaluation_setup_file_extension'] = 'csv'

        super(TUTAcousticScenes_2017_FeaturesSet, self).__init__(**kwargs)

        self.feature_parameters = {
            'win_length_seconds': 0.04,
            'hop_length_seconds': 0.02,
            'fs': 48000,
            'data_axis': 0,
            'time_axis': 1,
        }

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if 'features' in self.included_content_types or 'all' in self.included_content_types:
            # Split features into segment wise files
            train_segment_files_found = True
            for segment_id in range(0, 4499):
                segment_filename = os.path.join(self.local_path, 'features', 'X_train.npy','segment_{id}.npy'.format(id=segment_id))
                if not os.path.isfile(segment_filename):
                    train_segment_files_found = False

            if not train_segment_files_found:
                Path().makedirs(
                    path=os.path.join(self.local_path, 'features', 'X_train.npy')
                )

                X_train = numpy.load(os.path.join(self.local_path, 'X_train.npy'))
                for segment_id in range(0, X_train.shape[0]):
                    segment_filename = os.path.join(self.local_path, 'features', 'X_train.npy', 'segment_{id}.npy'.format(id=segment_id))
                    if not os.path.isfile(segment_filename):
                        numpy.save(
                            file=segment_filename,
                            arr=X_train[segment_id, :]
                        )

            test_segment_files_found = True
            for segment_id in range(0, 1499):
                segment_filename = os.path.join(self.local_path, 'features', 'X_test.npy','segment_{id}.npy'.format(id=segment_id))
                if not os.path.isfile(segment_filename):
                    test_segment_files_found = False

            if not test_segment_files_found:
                Path().makedirs(
                    path=os.path.join(self.local_path, 'features', 'X_test.npy')
                )

                X_test = numpy.load(os.path.join(self.local_path, 'X_test.npy'))
                for segment_id in range(0, X_test.shape[0]):
                    segment_filename = os.path.join(self.local_path, 'features', 'X_test.npy', 'segment_{id}.npy'.format(id=segment_id))
                    if not os.path.isfile(segment_filename):
                        numpy.save(
                            file=segment_filename,
                            arr=X_test[segment_id, :]
                        )

        if not self.meta_container.exists():
            meta = MetaDataContainer()

            if os.path.isfile(os.path.join(self.local_path, 'meta_train.csv')):
                meta_train = MetaDataContainer().load(os.path.join(self.local_path, 'meta_train.csv'))
                for item in meta_train:
                    item['filename'] = os.path.join('features', 'X_train.npy', 'segment_{id}.npy'.format(id=item['id']))
                    item['set_label'] = 'train'
                    del item['id']
                meta += meta_train

            if os.path.isfile(os.path.join(self.local_path, 'y_test.csv')):
                meta_test = MetaDataContainer().load(os.path.join(self.local_path, 'y_test.csv'))
                for item in meta_test:
                    item['filename'] = os.path.join('features', 'X_test.npy', 'segment_{id}.npy'.format(id=item['Id']))
                    item['scene_label'] = item['Scene_label']
                    item['identifier'] = 'Itest'
                    item['set_label'] = 'test-'+item['Usage'].lower()
                    del item['Id']
                    del item['Scene_label']
                    del item['Usage']
                meta += meta_test

            # Save meta
            meta.save(filename=self.meta_file, fields=['filename', 'scene_label', 'set_label', 'identifier'])

            # Load meta and cross validation
            self.load()

        all_folds_found = True
        for fold in self.folds():
            train_filename = self.evaluation_setup_filename(
                setup_part='train',
                fold=fold,
                file_extension='csv'
            )

            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                fold=fold,
                file_extension='csv'
            )

            eval_filename = self.evaluation_setup_filename(
                setup_part='evaluate',
                fold=fold,
                file_extension='csv'
            )

            if not os.path.isfile(train_filename):
                all_folds_found = False

            if not os.path.isfile(test_filename):
                all_folds_found = False

            if not os.path.isfile(eval_filename):
                all_folds_found = False

        if not all_folds_found:
            Path().makedirs(
                path=self.evaluation_setup_path
            )
            fold = 1
            train_filename = self.evaluation_setup_filename(
                setup_part='train',
                fold=fold,
                file_extension='csv'

            )

            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                fold=fold,
                file_extension='csv'
            )

            eval_filename = self.evaluation_setup_filename(
                setup_part='evaluate',
                fold=fold,
                file_extension='csv'
            )

            # Train
            train_meta = MetaDataContainer(
                filename=train_filename
            )
            train_meta += self.meta_container.filter(set_label='train')
            
            for item in train_meta:
                item.filename = self.absolute_to_relative_path(item.filename)
                
            train_meta.save(fields=['filename', 'scene_label', 'identifier'])

            # Test
            test_meta = MetaDataContainer(
                filename=test_filename
            )

            for item in self.meta_container.filter(set_label='test-public'):
                test_meta.append(
                    MetaDataItem(
                        {
                            'filename': self.absolute_to_relative_path(item['filename'])
                        }
                    )
                )

            for item in self.meta_container.filter(set_label='test-private'):
                test_meta.append(
                    MetaDataItem(
                        {
                            'filename': self.absolute_to_relative_path(item['filename'])
                        }
                    )
                )

            test_meta.save(fields=['filename'])

            # Evaluate
            eval_meta = MetaDataContainer(
                filename=eval_filename
            )
            eval_meta += self.meta_container.filter(set_label='test-public')
            eval_meta += self.meta_container.filter(set_label='test-private')
            
            for item in eval_meta:
                item.filename = self.absolute_to_relative_path(item.filename)
                
            eval_meta.save(fields=['filename', 'scene_label', 'identifier'])

            # Load meta and cross validation
            self.load()

        return self

    def file_features(self, filename):
        """Pre-calculated acoustic features for given file

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        numpy.ndarray
            Matrix containing acoustic features

        """

        if os.path.isfile(filename):
            return numpy.load(file=filename)

        else:
            message = '{name}: Feature file not found [{filename}]'.format(
                name=self.__class__.__name__,
                filename=filename
            )

            self.logger.exception(message)
            raise IOError(message)


class TUTRareSoundEvents_2017_DevelopmentSet(SyntheticSoundEventDataset):
    """TUT Acoustic scenes 2017 development dataset

    This dataset is used in DCASE2017 - Task 2, Rare sound event detection

    """

    def __init__(self,
                 storage_name='TUT-rare-sound-events-2017-development',
                 data_path=None,
                 included_content_types=None,
                 synth_parameters=None,
                 dcase_compatibility=True,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-rare-sound-events-2017-development'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        synth_parameters : dict
            Data synthesis parameters.
            Default value None

        dcase_compatibility : bool
            Ensure that dataset is generated same way than in DCASE2017 Challenge setup
            Default value True

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['filelisthash_exclude_dirs'] = kwargs.get(
            'filelisthash_exclude_dirs',
            [os.path.join('data', 'mixture_data')]
        )
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Aleksandr Diment, Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Rare Sound Events 2017, development dataset',
            'url': None,
            'audio_source': 'Synthetic',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Unknown',
        }
        kwargs['crossvalidation_folds'] = 1

        source_url = 'https://zenodo.org/record/401395/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.doc.zip',
                'remote_bytes': 21042,
                'remote_md5': '47c424fe90d2bdc53d9fdd84341c2783',
                'filename': 'TUT-rare-sound-events-2017-development.doc.zip'
            },
            {
                'content_type': 'code',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.code.zip',
                'remote_bytes': 81518,
                'remote_md5': '4cacdf0803daf924a60bf9daa573beb7',
                'filename': 'TUT-rare-sound-events-2017-development.code.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.1.zip',
                'remote_bytes': 1072175672,
                'remote_md5': '6f1f4156d41b541d1188fcf44c9a8267',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.2.zip',
                'remote_bytes': 1073378284,
                'remote_md5': 'ff5dcbe250e45cc404b7b8a6013002ac',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.3.zip',
                'remote_bytes': 1069766123,
                'remote_md5': 'fb356ae309a40d2f0a38fc1c746835cb',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.4.zip',
                'remote_bytes': 1070042681,
                'remote_md5': '2a68575b2ec7a69e2cc8b16b87fae0c9',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.5.zip',
                'remote_bytes': 1073380909,
                'remote_md5': '84e70d855457a18115108e42ec04501a',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.6.zip',
                'remote_bytes': 1073021941,
                'remote_md5': '048ce898bd434097dd489027f7ba361d',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.7.zip',
                'remote_bytes': 1069890239,
                'remote_md5': '3ef1c89fcfac39918a5edc5abc6ed29b',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.8.zip',
                'remote_bytes': 180860904,
                'remote_md5': '69dcb81e70f4e6605e178693afcd7722',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_bgs_and_cvsetup.8.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-development.source_data_events.zip',
                'remote_bytes': 639119477,
                'remote_md5': 'dc4b7eb77078b4cf1b670c6362679473',
                'filename': 'TUT-rare-sound-events-2017-development.source_data_events.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']

        default_synth_parameters = DictContainer({
            'train': {
                'seed': 42,
                'event_presence_prob': 0.5,
                'mixtures_per_class': 500,
                'ebr_list': [-6, 0, 6],
            },
            'test': {
                'seed': 42,
                'event_presence_prob': 0.5,
                'mixtures_per_class': 500,
                'ebr_list': [-6, 0, 6],
            }
        })
        if synth_parameters is None:
            synth_parameters = {}

        # Override synth parameters
        synth_parameters = default_synth_parameters.merge(synth_parameters)

        # Meta filename depends on synth_parameters
        kwargs['meta_filename'] = 'meta_'+synth_parameters.get_hash_for_path()+'.txt'

        self.synth_parameters = synth_parameters

        # Add parameter hash
        self.synth_parameters['train']['param_hash'] = hashlib.md5(
            yaml.dump(
                {
                    'event_presence_prob': self.synth_parameters['train']['event_presence_prob'],
                    'mixtures_per_class': self.synth_parameters['train']['mixtures_per_class'],
                    'ebrs': self.synth_parameters['train']['ebr_list'],
                    'seed': self.synth_parameters['train']['seed']
                }
            ).encode('utf-8')).hexdigest()

        self.synth_parameters['test']['param_hash'] = hashlib.md5(
            yaml.dump(
                {
                    'event_presence_prob': self.synth_parameters['test']['event_presence_prob'],
                    'mixtures_per_class': self.synth_parameters['test']['mixtures_per_class'],
                    'ebrs': self.synth_parameters['test']['ebr_list'],
                    'seed': self.synth_parameters['test']['seed']
                }
            ).encode('utf-8')).hexdigest()

        self.dcase_compatibility = dcase_compatibility

        # Initialize baseclass
        super(TUTRareSoundEvents_2017_DevelopmentSet, self).__init__(**kwargs)

        # Add code package to be downloaded always
        if 'code' not in self.included_content_types or 'all' not in self.included_content_types:
            self.included_content_types.append('code')

    def event_labels(self, scene_label=None):
        """List of unique event labels in the meta data.

        Parameters
        ----------

        Returns
        -------
        labels : list
            List of event labels in alphabetical order.

        """

        labels = ['babycry', 'glassbreak', 'gunshot']
        labels.sort()
        return labels

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        # Make sure evaluation_setup directory exists
        Path().makedirs(path=os.path.join(self.local_path, self.evaluation_setup_folder))

        return self

    def synthesize(self):
        # Create init so we can call functions
        if os.path.exists(os.path.join(self.local_path, 'TUT_Rare_sound_events_mixture_synthesizer', '__init__.py')):
            open(os.path.join(self.local_path, 'TUT_Rare_sound_events_mixture_synthesizer', '__init__.py'), 'a').close()

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        # Add synth code to the search path
        sys.path.append(os.path.join(self.local_path, 'TUT_Rare_sound_events_mixture_synthesizer'))
        from core import generate_mixture_recipes
        from core import do_mixing

        scene_label = 'synthetic'
        subset_map = {'train': 'devtrain',
                      'test': 'devtest'}

        data_path = os.path.join(os.path.abspath(self.local_path), 'data')

        set_progress = tqdm(['train', 'test'],
                            desc="{0: <25s}".format('Set'),
                            file=sys.stdout,
                            leave=False,
                            disable=self.disable_progress_bar,
                            ascii=self.use_ascii_progress_bar)

        for subset_label in set_progress:
            if self.log_system_progress:
                self.logger.info('  {title:<15s} [{subset_label:<30s}]'.format(
                    title='Set ',
                    subset_label=subset_label)
                )

            # Translated subset name
            subset_name_on_disk = subset_map[subset_label]

            # Get parameters
            mixing_params = {
                'event_presence_prob': self.synth_parameters[subset_label]['event_presence_prob'],
                'mixtures_per_class': self.synth_parameters[subset_label]['mixtures_per_class'],
                'ebrs': self.synth_parameters[subset_label]['ebr_list'],
                'seed': self.synth_parameters[subset_label]['seed']
            }

            # Get parameter hash
            param_hash = self.synth_parameters[subset_label]['param_hash']

            # Save parameters
            mixture_parameters = os.path.join(
                self.local_path, 'data', 'mixture_data', subset_name_on_disk, param_hash, 'parameters.yaml'
            )
            if not os.path.isfile(mixture_parameters):
                # Make sure directory exists
                Path().makedirs(
                    path=os.path.join(self.local_path, 'data', 'mixture_data', subset_name_on_disk, param_hash)
                )

                # Save
                ParameterContainer(mixing_params).save(filename=mixture_parameters)

            # Check do we need to generate recipes
            recipes_exists = True
            for event_label in self.event_labels():
                recipe_filename = 'mixture_recipes_' + subset_name_on_disk + '_' + event_label + '.yaml'
                if not os.path.isfile(os.path.join(self.local_path, 'data', 'mixture_data',
                                                   subset_name_on_disk, param_hash, 'meta', recipe_filename)):
                    recipes_exists = False

            if not recipes_exists:
                # Generate mixture recipes
                generate_mixture_recipes(
                    data_path=data_path,
                    current_subsets=numpy.array([subset_name_on_disk]),
                    mixing_params=mixing_params
                )

            # Check do we need to generate mixtures
            mixture_audio_exists = True
            audio_files = Path().file_list(
                path=os.path.join(self.local_path, 'data', 'mixture_data', subset_name_on_disk, param_hash, 'audio'))

            for event_label in self.event_labels():
                event_audio = []
                for f in audio_files:
                    if event_label in f:
                        event_audio.append(f)
                if len(event_audio) != self.synth_parameters[subset_label]['mixtures_per_class']:
                    mixture_audio_exists = False

            if not mixture_audio_exists:
                # Generate mixture audio based on recipes
                do_mixing(
                    data_path=data_path,
                    current_subsets=numpy.array([subset_name_on_disk]),
                    magic_anticlipping_factor=0.2,
                    param_hash=param_hash,
                    dcase_compatibility_mode=True
                )

        if not self.meta_container.exists():
            # Collect meta data
            meta_data = MetaDataContainer()
            for class_label in self.event_labels():
                for subset_label, subset_name_on_disk in iteritems(subset_map):
                    subset_name_on_disk = subset_map[subset_label]

                    # Get parameter hash
                    param_hash = self.synth_parameters[subset_label]['param_hash']

                    mixture_path = os.path.join(
                        'data',
                        'mixture_data',
                        subset_name_on_disk,
                        param_hash,
                        'audio'
                    )

                    mixture_meta_path = os.path.join(
                        self.local_path,
                        'data',
                        'mixture_data',
                        subset_name_on_disk,
                        param_hash,
                        'meta'
                    )

                    event_list_filename = os.path.join(
                        mixture_meta_path,
                        'event_list_' + subset_name_on_disk + '_' + class_label + '.csv'
                    )

                    if os.path.isfile(event_list_filename):
                        current_meta = MetaDataContainer(
                            filename=event_list_filename
                        ).load(
                            fields=['filename', 'onset', 'offset', 'event_label']
                        )

                        for item in current_meta:
                            item.filename = os.path.join(mixture_path, item.filename)
                            item.scene_label = scene_label

                        meta_data += current_meta

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        # Evaluation setup filenames
        train_filename = self.evaluation_setup_filename(
            setup_part='train',
            fold=1,
            file_extension='txt'
        )

        test_filename = self.evaluation_setup_filename(
            setup_part='test',
            fold=1,
            file_extension='txt'
        )

        evaluate_filename = self.evaluation_setup_filename(
            setup_part='evaluate',
            fold=1,
            file_extension='txt'
        )

        # Check that evaluation setup exists
        evaluation_setup_exists = True
        if not os.path.isfile(train_filename) or not os.path.isfile(test_filename) or not os.path.isfile(evaluate_filename):
            evaluation_setup_exists = False

        if not evaluation_setup_exists:
            # Get parameter hash
            param_hash_train = self.synth_parameters['train']['param_hash']

            mixture_meta_path_train = os.path.join(
                self.local_path,
                'data',
                'mixture_data',
                subset_map['train'],
                param_hash_train,
                'meta'
            )
            mixture_path_train = os.path.join(
                'data',
                'mixture_data',
                subset_map['train'],
                param_hash_train,
                'audio'
            )

            # Get parameter hash
            param_hash_test = self.synth_parameters['test']['param_hash']

            mixture_meta_path_test = os.path.join(
                self.local_path,
                'data',
                'mixture_data',
                subset_map['test'],
                param_hash_test,
                'meta'
            )
            mixture_path_test = os.path.join(
                'data',
                'mixture_data',
                subset_map['test'],
                param_hash_test,
                'audio'
            )

            train_meta = MetaDataContainer()
            for class_label in self.event_labels():
                event_list_filename = os.path.join(
                    mixture_meta_path_train,
                    'event_list_' + subset_map['train'] + '_' + class_label + '.csv'
                )
                current_meta = MetaDataContainer(
                    filename=event_list_filename
                ).load(
                    fields=['filename', 'onset', 'offset', 'event_label']
                )
                for item in current_meta:
                    item.filename = os.path.join(mixture_path_train, item.filename)
                    item.scene_label = scene_label

                train_meta += current_meta
            train_meta.save(filename=train_filename)

            test_meta = MetaDataContainer()
            for class_label in self.event_labels():
                event_list_filename = os.path.join(
                    mixture_meta_path_test,
                    'event_list_' + subset_map['test'] + '_' + class_label + '.csv'
                )
                current_meta = MetaDataContainer(
                    filename=event_list_filename
                ).load(
                    fields=['filename', 'onset', 'offset', 'event_label']
                )
                current_meta_ = MetaDataContainer()
                for item in current_meta:
                    item.filename = os.path.join(mixture_path_test, item.filename)
                    current_meta_.append(MetaDataItem(
                        {
                            'filename': item.filename,
                            'scene_label': scene_label
                        }
                    ))
                test_meta += current_meta_
            test_meta.save(filename=test_filename)

            eval_meta = MetaDataContainer()
            for class_label in self.event_labels():
                event_list_filename = os.path.join(
                    mixture_meta_path_test,
                    'event_list_' + subset_map['test'] + '_' + class_label + '.csv'
                )
                current_meta = MetaDataContainer(
                    filename=event_list_filename
                ).load(
                    fields=['filename', 'onset', 'offset', 'event_label']
                )
                for item in current_meta:
                    item.filename = os.path.join(mixture_path_test, item.filename)
                    item.scene_label = scene_label

                eval_meta += current_meta
            eval_meta.save(filename=evaluate_filename)

            # Load meta and cross validation
            self.load()

    def evaluation_setup_filename(self, setup_part='train', fold=None, scene_label=None, file_extension='txt'):
        parts = []

        if setup_part == 'test' or setup_part == 'evaluate':
            subset_label = 'test'
        else:
            subset_label = 'train'

        param_hash = self.synth_parameters[subset_label]['param_hash']

        if setup_part == 'train':
            parts.append('train')

        elif setup_part == 'test':
            parts.append('test')

        elif setup_part == 'evaluate':
            parts.append('evaluate')

        else:
            message = '{name}: Unknown setup_part [{setup_part}]'.format(
                name=self.__class__.__name__,
                setup_part=setup_part
            )

            self.logger.exception(message)
            raise ValueError(message)

        return os.path.join(self.evaluation_setup_path, '_'.join(parts) + '_' + param_hash + '.' + file_extension)

    def train(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of training items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value "None"
        scene_label : str
            Scene label
            Default value "None"
        event_label : str
            Event label
            Default value "None"
        filename_contains : str:
            String found in filename
             Default value "None"

        Returns
        -------
        list : list of dicts
            List containing all meta data assigned to training set for given fold.

        """
        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['train'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data

    def test(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of testing items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value "None"
        scene_label : str
            Scene label
            Default value "None"
        event_label : str
            Event label
            Default value "None"
        filename_contains : str:
            String found in filename
             Default value "None"

        Returns
        -------
        list : list of dicts
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['test'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data

    def eval(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of evaluation items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value "None"
        scene_label : str
            Scene label
            Default value "None"
        event_label : str
            Event label
            Default value "None"
        filename_contains : str:
            String found in filename
             Default value "None"

        Returns
        -------
        list : list of dicts
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['evaluate'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data


class TUTRareSoundEvents_2017_EvaluationSet(SyntheticSoundEventDataset):
    """TUT Acoustic scenes 2017 evaluation dataset

    This dataset is used in DCASE2017 - Task 2, Rare sound event detection

    """

    def __init__(self,
                 storage_name='TUT-rare-sound-events-2017-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-rare-sound-events-2017-evaluation'

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
        kwargs['reference_data_present'] = True
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Aleksandr Diment, Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Rare Sound Events 2017, evaluation dataset',
            'url': None,
            'audio_source': 'Synthetic',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Unknown',
        }
        kwargs['crossvalidation_folds'] = None

        source_url = 'https://zenodo.org/record/1160455/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.doc.zip',
                'remote_bytes': 11701,
                'remote_md5': '36db98a94ce871c6bdc5bd5238383114',
                'filename': 'TUT-rare-sound-events-2017-evaluation.doc.zip'
            },
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'LICENSE.txt',
                'remote_bytes': 0,
                'remote_md5': '0707857098fc74d17beb824416fb74b1',
                'filename': 'LICENSE.txt'
            },
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'FREESOUNDCREDITS.txt',
                'remote_bytes': 0,
                'remote_md5': '3ecea52bdb0eadd6e1af52a21f735d6d',
                'filename': 'FREESOUNDCREDITS.txt'
            },
            {
                'content_type': ['audio', 'meta'],
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.mixture_data.1.zip',
                'remote_bytes': 1071143794,
                'remote_md5': 'db4aecd5175dead27ceb2692e7f28bb1',
                'filename': 'TUT-rare-sound-events-2017-evaluation.mixture_data.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.mixture_data.2.zip',
                'remote_bytes': 1071773516,
                'remote_md5': 'e97d5842c46805cdb94e6d4017870cde',
                'filename': 'TUT-rare-sound-events-2017-evaluation.mixture_data.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.mixture_data.3.zip',
                'remote_bytes': 1073505512,
                'remote_md5': '1fe20c762cecd26979e2c5303c8e9f48',
                'filename': 'TUT-rare-sound-events-2017-evaluation.mixture_data.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.mixture_data.4.zip',
                'remote_bytes': 1071132551,
                'remote_md5': '5042cd00aed9af6b37a253e24f88554f',
                'filename': 'TUT-rare-sound-events-2017-evaluation.mixture_data.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.mixture_data.5.zip',
                'remote_bytes': 308314939,
                'remote_md5': '72180597ed5bfaa73491755f74b84738',
                'filename': 'TUT-rare-sound-events-2017-evaluation.mixture_data.5.zip'
            }
        ]
        kwargs['audio_paths'] = [os.path.join('data', 'mixture_data', 'evaltest', 'bbb81504db15a03680a0044474633b67', 'audio')]

        # Initialize base class
        super(TUTRareSoundEvents_2017_EvaluationSet, self).__init__(**kwargs)

    def scene_labels(self):
        return ['synthetic']

    def event_labels(self, scene_label=None):
        """List of unique event labels in the meta data.

        Parameters
        ----------

        Returns
        -------
        labels : list
            List of event labels in alphabetical order.

        """

        labels = ['babycry', 'glassbreak', 'gunshot']
        labels.sort()
        return labels

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        scene_label = 'synthetic'
        subset_map = {'test': 'evaltest'}
        param_hash = 'bbb81504db15a03680a0044474633b67'
        # Make sure evaluation_setup directory exists
        Path().makedirs(path=os.path.join(self.local_path, self.evaluation_setup_folder))

        if not self.meta_container.exists() and self.reference_data_present:
            # Collect meta data
            meta_data = MetaDataContainer()
            for class_label in self.event_labels():
                for subset_label, subset_name_on_disk in iteritems(subset_map):
                    subset_name_on_disk = subset_map[subset_label]

                    mixture_path = os.path.join(
                        'data',
                        'mixture_data',
                        subset_name_on_disk,
                        param_hash,
                        'audio'
                    )

                    mixture_meta_path = os.path.join(
                        self.local_path,
                        'data',
                        'mixture_data',
                        subset_name_on_disk,
                        param_hash,
                        'meta'
                    )

                    event_list_filename = os.path.join(
                        mixture_meta_path,
                        'event_list_' + subset_name_on_disk + '_' + class_label + '.csv'
                    )

                    if os.path.isfile(event_list_filename):
                        current_meta = MetaDataContainer(
                            filename=event_list_filename
                        ).load(
                            fields=['filename', 'onset', 'offset', 'event_label']
                        )

                        for item in current_meta:
                            item.filename = os.path.join(mixture_path, item.filename)
                            item.scene_label = scene_label

                        meta_data += current_meta

            # Save meta
            meta_data.save(filename=self.meta_file)


        test_filename = self.evaluation_setup_filename(
            setup_part='test',
            fold=None,
            file_extension='txt'
        )

        evaluate_filename = self.evaluation_setup_filename(
            setup_part='evaluate',
            fold=None,
            file_extension='txt'
        )

        # Check that evaluation setup exists
        evaluation_setup_exists = True
        if not os.path.isfile(test_filename) or not os.path.isfile(evaluate_filename):
            evaluation_setup_exists = False

        if not evaluation_setup_exists:
            # Get parameter hash
            mixture_meta_path_test = os.path.join(
                self.local_path,
                'data',
                'mixture_data',
                subset_map['test'],
                param_hash,
                'meta'
            )
            mixture_path_test = os.path.join(
                'data',
                'mixture_data',
                subset_map['test'],
                param_hash,
                'audio'
            )

            test_meta = MetaDataContainer()
            for class_label in self.event_labels():
                event_list_filename = os.path.join(
                    mixture_meta_path_test,
                    'event_list_' + subset_map['test'] + '_' + class_label + '.csv'
                )
                current_meta = MetaDataContainer(
                    filename=event_list_filename
                ).load(
                    fields=['filename', 'onset', 'offset', 'event_label']
                )
                current_meta_ = MetaDataContainer()
                for item in current_meta:
                    item.filename = os.path.join(mixture_path_test, item.filename)
                    current_meta_.append(MetaDataItem(
                        {
                            'filename': item.filename,
                            'scene_label': scene_label
                        }
                    ))
                test_meta += current_meta_
            test_meta.save(filename=test_filename)

            eval_meta = MetaDataContainer()
            for class_label in self.event_labels():
                event_list_filename = os.path.join(
                    mixture_meta_path_test,
                    'event_list_' + subset_map['test'] + '_' + class_label + '.csv'
                )
                current_meta = MetaDataContainer(
                    filename=event_list_filename
                ).load(
                    fields=['filename', 'onset', 'offset', 'event_label']
                )
                for item in current_meta:
                    item.filename = os.path.join(mixture_path_test, item.filename)
                    item.scene_label = scene_label

                eval_meta += current_meta
            eval_meta.save(filename=evaluate_filename)

            # Load meta and cross validation
            self.load()

        return self

    def evaluation_setup_filename(self, setup_part='train', fold=None, scene_label=None, file_extension='txt'):
        parts = []

        if setup_part == 'test' or setup_part == 'evaluate':
            subset_label = 'test'
        else:
            subset_label = 'train'

        if setup_part == 'train':
            parts.append('train')

        elif setup_part == 'test':
            parts.append('test')

        elif setup_part == 'evaluate':
            parts.append('evaluate')

        else:
            message = '{name}: Unknown setup_part [{setup_part}]'.format(
                name=self.__class__.__name__,
                setup_part=setup_part
            )

            self.logger.exception(message)
            raise ValueError(message)

        return os.path.join(self.evaluation_setup_path, '_'.join(parts) + '.' + file_extension)

    def train(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of training items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value None

        scene_label : str
            Scene label
            Default value None"

        event_label : str
            Event label
            Default value None"

        filename_contains : str:
            String found in filename
             Default value None

        Returns
        -------
        list
            List containing all meta data assigned to training set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['train'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data

    def test(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of testing items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value None

        scene_label : str
            Scene label
            Default value None

        event_label : str
            Event label
            Default value None

        filename_contains : str:
            String found in filename
             Default value None

        Returns
        -------
        list
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['test'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data

    def eval(self, fold=None, scene_label=None, event_label=None, filename_contains=None, **kwargs):
        """List of evaluation items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.
            Default value None

        scene_label : str
            Scene label
            Default value None

        event_label : str
            Event label
            Default value None

        filename_contains : str:
            String found in filename
             Default value None

        Returns
        -------
        list
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['evaluate'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        if filename_contains:
            data_ = MetaDataContainer()
            for item in data:
                if filename_contains in item.filename:
                    data_.append(item)
            data = data_

        return data


class TUTSoundEvents_2017_DevelopmentSet(SoundEventDataset):
    """TUT Sound events 2017 development dataset

    This dataset is used in DCASE2017 - Task 3, Sound event detection in real life audio

    """

    def __init__(self,
                 storage_name='TUT-sound-events-2017-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-sound-events-2017-development'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Sound Events 2016, development dataset',
            'url': 'https://zenodo.org/record/45759',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 4

        source_url = 'https://zenodo.org/record/814831/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-sound-events-2017-development.doc.zip',
                'remote_bytes': 56150,
                'remote_md': 'aa6024e70f5bff3fe15d962b01753e23',
                'filename': 'TUT-sound-events-2017-development.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-sound-events-2017-development.meta.zip',
                'remote_bytes': 140684,
                'remote_md': '50e870b3a89ed3452e2a35b508840929',
                'filename': 'TUT-sound-events-2017-development.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2017-development.audio.1.zip',
                'remote_bytes': 1062653169,
                'remote_md': '6f1cd31592b8240a14be3ee513db6a23',
                'filename': 'TUT-sound-events-2017-development.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2017-development.audio.2.zip',
                'remote_bytes': 213232458,
                'remote_md': 'adcff03341b84dc8d35f035b93c1efa0',
                'filename': 'TUT-sound-events-2017-development.audio.2.zip'
            }
        ]
        kwargs['audio_paths'] = [os.path.join('audio', 'street')]
        super(TUTSoundEvents_2017_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = raw_filename.split('_')[0]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = MetaDataContainer()
            annotation_files = Path().file_list(path=os.path.join(self.local_path, 'meta'), extensions=['ann'])
            for annotation_filename in annotation_files:
                data = MetaDataContainer(filename=annotation_filename).load()
                for item in data:
                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                meta_data += data

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self


class TUTSoundEvents_2017_EvaluationSet(SoundEventDataset):
    """TUT Sound events 2017 evaluation dataset

    This dataset is used in DCASE2017 - Task 3, Sound event detection in real life audio

    """

    def __init__(self,
                 storage_name='TUT-sound-events-2017-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-sound-events-2017-evaluation'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Sound Events 2016, development dataset',
            'url': 'https://zenodo.org/record/45759',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = None

        source_url = 'https://zenodo.org/record/1040179/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-sound-events-2017-evaluation.doc.zip',
                'remote_bytes': 54606,
                'remote_md5': '8bbf41671949edee15d6cdc3f9e726c9',
                'filename': 'TUT-sound-events-2017-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-sound-events-2017-evaluation.meta.zip',
                'remote_bytes': 762,
                'remote_md5': 'a951598abaea87296ca409e30fb0b379',
                'filename': 'TUT-sound-events-2017-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2017-evaluation.audio.zip',
                'remote_bytes': 388173790,
                'remote_md5': '1d3aa81896be0f142130ca9ca7a2b871',
                'filename': 'TUT-sound-events-2017-evaluation.audio.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']
        super(TUTSoundEvents_2017_EvaluationSet, self).__init__(**kwargs)

    def scene_labels(self):
        labels = ['street']
        labels.sort()
        return labels

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = os.path.splitext(raw_filename)[0]
        item.source_label = 'mixture'

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            evaluate_filename = self.evaluation_setup_filename(
                setup_part='evaluate',
                scene_label=self.scene_labels()[0]
            )
            eval_file = MetaDataContainer(filename=evaluate_filename)

            if eval_file.exists():
                # Get meta data from evaluation file
                meta_data = MetaDataContainer()
                eval_file.load()
                for item in eval_file:
                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                meta_data += eval_file

                # Save meta
                meta_data.save(filename=self.meta_file)

                # Load meta and cross validation
                self.load()

            elif os.path.isdir(os.path.join(self.local_path, 'meta')):
                annotation_files = Path().file_list(path=os.path.join(self.local_path, 'meta'), extensions=['ann'])

                # Get meta data from annotation files
                meta_data = MetaDataContainer()

                for annotation_filename in annotation_files:
                    data = MetaDataContainer(filename=annotation_filename).load()
                    for item in data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                    meta_data += data

                # Save meta
                meta_data.save(filename=self.meta_file)

                # Load meta and cross validation
                self.load()

        return self


# =====================================================
# DCASE 2016
# =====================================================


class TUTAcousticScenes_2016_DevelopmentSet(AcousticSceneDataset):
    """TUT Acoustic scenes 2016 development dataset

    This dataset is used in DCASE2016 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='TUT-acoustic-scenes-2016-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2016-development'

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
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Acoustic Scenes 2016, development dataset',
            'url': 'https://zenodo.org/record/45739',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 4

        source_url = 'https://zenodo.org/record/45739/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.doc.zip',
                'remote_bytes': 69671,
                'remote_md5': 'f94ad46eb36325d9fbce5d60f7fc9926',
                'filename': 'TUT-acoustic-scenes-2016-development.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.meta.zip',
                'remote_bytes': 28815,
                'remote_md5': '779b33da2ebbf8bde494b3c981827251',
                'filename': 'TUT-acoustic-scenes-2016-development.meta.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.error.zip',
                'remote_bytes': 1283,
                'remote_md5': 'a0d3e0d81b0a36ece87d0f3a9124a386',
                'filename': 'TUT-acoustic-scenes-2016-development.error.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.1.zip',
                'remote_bytes': 1070981236,
                'remote_md5': 'e39546e65f2e72517b6335aaf0c8323d',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.2.zip',
                'remote_bytes': 1067186166,
                'remote_md5': 'd36cf3253e2c041f68e937a3fe804807',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.3.zip',
                'remote_bytes': 1073644405,
                'remote_md5': '0393a9620ab882b1c26d884eccdcffdd',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.4.zip',
                'remote_bytes': 1072111347,
                'remote_md5': 'fb3e4e0cd7ea82120ec07031dee558ce',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.5.zip',
                'remote_bytes': 1069681513,
                'remote_md5': 'a19cf600b33c8f88f6ad607bafd74057',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.5.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.6.zip',
                'remote_bytes': 1072890150,
                'remote_md5': '591aad3219d1155342572cc1f6af5680',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.6.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.7.zip',
                'remote_bytes': 1069265197,
                'remote_md5': '9e6c1897789e6bce13ac69c6caedb7ab',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.7.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-development.audio.8.zip',
                'remote_bytes': 528461098,
                'remote_md5': 'c4718354f48fcc9dfc7305f6cd8325c8',
                'filename': 'TUT-acoustic-scenes-2016-development.audio.8.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(TUTAcousticScenes_2016_DevelopmentSet, self).__init__(**kwargs)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = {}
            for fold in range(1, self.crossvalidation_folds):
                # Read train files in
                fold_data = MetaDataContainer(
                    filename=self.evaluation_setup_filename(setup_part='train', fold=fold)
                ).load()

                # Read eval files in
                fold_data += MetaDataContainer(
                    filename=self.evaluation_setup_filename(setup_part='evaluate', fold=fold)
                ).load()

                for item in fold_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

            # Save meta
            MetaDataContainer(list(meta_data.values())).save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()
        return self

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)
        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = raw_filename.split('_')[0]


class TUTAcousticScenes_2016_EvaluationSet(AcousticSceneDataset):
    """TUT Acoustic scenes 2016 evaluation dataset

    This dataset is used in DCASE2016 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='TUT-acoustic-scenes-2016-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2016-evaluation'

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
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Acoustic Scenes 2016, evaluation dataset',
            'url': 'https://zenodo.org/record/165995',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = None

        source_url = 'https://zenodo.org/record/165995/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-evaluation.doc.zip',
                'remote_bytes': 69217,
                'remote_md5': 'ef315bf912d1124050646888cc3ceba2',
                'filename': 'TUT-acoustic-scenes-2016-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-evaluation.meta.zip',
                'remote_bytes': 5962,
                'remote_md5': '0d5c131fc3f50c682de62e0e648aceba',
                'filename': 'TUT-acoustic-scenes-2016-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-evaluation.audio.1.zip',
                'remote_bytes': 1067685684,
                'remote_md5': '7c6c2e54b8a9c4c37a803b81446d16fe',
                'filename': 'TUT-acoustic-scenes-2016-evaluation.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-evaluation.audio.2.zip',
                'remote_bytes': 1068308900,
                'remote_md5': '7930f1dc26707ab3ba9526073af87333',
                'filename': 'TUT-acoustic-scenes-2016-evaluation.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2016-evaluation.audio.3.zip',
                'remote_bytes': 538894804,
                'remote_md5': '17187d633d6402aee4b481122a1b28f0',
                'filename': 'TUT-acoustic-scenes-2016-evaluation.audio.3.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']
        super(TUTAcousticScenes_2016_EvaluationSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        if item.filename_original is not None:
            raw_path, raw_filename = os.path.split(item.filename_original)
            item.identifier = raw_filename.split('_')[0]
            del item['filename_original']

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            evaluate_filename = self.evaluation_setup_filename(
                setup_part='evaluate'
            )

            eval_file = MetaDataContainer(filename=evaluate_filename)
            if eval_file.exists():
                eval_data = eval_file.load()
                meta_data = {}
                for item in eval_data:
                    if item.filename not in meta_data:
                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                        meta_data[item.filename] = item

                # Save meta
                MetaDataContainer(list(meta_data.values())).save(filename=self.meta_file)

                # Load meta and cross validation
                self.load()

        return self


class TUTSoundEvents_2016_DevelopmentSet(SoundEventDataset):
    """TUT Sound events 2016 development dataset

    This dataset is used in DCASE2016 - Task 3, Sound event detection in real life audio

    """

    def __init__(self,
                 storage_name='TUT-sound-events-2016-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-acoustic-scenes-2016-development'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Sound Events 2016, development dataset',
            'url': 'https://zenodo.org/record/45759',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = 4

        source_url = 'https://zenodo.org/record/45759/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-sound-events-2016-development.doc.zip',
                'remote_bytes': 70918,
                'remote_md5': '33fd26a895530aef607a07b08704eacd',
                'filename': 'TUT-sound-events-2016-development.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-sound-events-2016-development.meta.zip',
                'remote_bytes': 122321,
                'remote_md5': '7b29f0e2b82b3f264653cb4fa43da75d',
                'filename': 'TUT-sound-events-2016-development.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2016-development.audio.zip',
                'remote_bytes': 1014040667,
                'remote_md5': 'a6006efaa85bb69d5064b00c6802a8f8',
                'filename': 'TUT-sound-events-2016-development.audio.zip'
            }
        ]
        kwargs['audio_paths'] = [
            os.path.join('audio', 'home'),
            os.path.join('audio', 'residential_area')
        ]
        super(TUTSoundEvents_2016_DevelopmentSet, self).__init__(**kwargs)

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = os.path.splitext(raw_filename)[0]
        item.source_label = 'mixture'

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = MetaDataContainer()
            annotation_files = Path().file_list(path=os.path.join(self.local_path, 'meta'), extensions=['ann'])
            for annotation_filename in annotation_files:
                scene_label = os.path.split(os.path.split(annotation_filename)[0])[1]
                identifier = os.path.splitext(os.path.split(annotation_filename)[1])[0]
                audio_filename = os.path.join('audio', scene_label, identifier + '.wav')

                data = MetaDataContainer(filename=annotation_filename).load()
                for item in data:
                    item.filename = audio_filename
                    item.scene_label = scene_label

                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                meta_data += data

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self


class TUTSoundEvents_2016_EvaluationSet(SoundEventDataset):
    """TUT Sound events 2016 evaluation dataset

    This dataset is used in DCASE2016 - Task 3, Sound event detection in real life audio

    """
    def __init__(self,
                 storage_name='TUT-sound-events-2016-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-sound-events-2016-evaluation'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen',
            'title': 'TUT Sound Events 2016, evaluation dataset',
            'url': 'http://www.cs.tut.fi/sgn/arg/dcase2016/download/',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Roland Edirol R-09',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
            'licence': 'free non-commercial'
        }
        kwargs['crossvalidation_folds'] = None

        source_url = 'https://zenodo.org/record/996424/files/'
        kwargs['package_list'] = [
            {
                'content_type': 'documentation',
                'remote_file': source_url + 'TUT-sound-events-2016-evaluation.doc.zip',
                'remote_bytes': 69834,
                'remote_md5': '0644b54d96f4cefd0ecb2c7ea9161aa9',
                'filename': 'TUT-sound-events-2016-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-sound-events-2016-evaluation.meta.zip',
                'remote_bytes': 41608,
                'remote_md5': '91c266b0780ac619a0d74298a3805e9e',
                'filename': 'TUT-sound-events-2016-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2016-evaluation.audio.zip',
                'remote_bytes': 471072452,
                'remote_md5': '29434e8c53bd51206df0234e6cf2238c',
                'filename': 'TUT-sound-events-2016-evaluation.audio.zip'
            }
        ]
        kwargs['audio_paths'] = [
            os.path.join('audio', 'home'),
            os.path.join('audio', 'residential_area')
        ]
        super(TUTSoundEvents_2016_EvaluationSet, self).__init__(**kwargs)

    def scene_labels(self):
        labels = ['home', 'residential_area']
        labels.sort()
        return labels

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists() and os.path.isdir(os.path.join(self.local_path, 'meta')):
            meta_data = MetaDataContainer()
            annotation_files = Path().file_list(path=os.path.join(self.local_path, 'meta'), extensions=['ann'])
            for annotation_filename in annotation_files:
                scene_label = os.path.split(os.path.split(annotation_filename)[0])[1]
                identifier = os.path.splitext(os.path.split(annotation_filename)[1])[0]
                audio_filename = os.path.join('audio', scene_label, identifier + '.wav')

                data = MetaDataContainer(filename=annotation_filename).load(decimal='comma')
                for item in data:
                    item.filename = audio_filename
                    item.scene_label = scene_label

                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                meta_data += data

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self

# =====================================================
# Others
# =====================================================


class TUT_SED_Synthetic_2016(SoundEventDataset):
    """TUT SED Synthetic 2016

    """

    def __init__(self,
                 storage_name='TUT-SED-synthetic-2016',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'TUT-SED-synthetic-2016'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Emre Cakir',
            'title': 'TUT-SED Synthetic 2016',
            'url': 'http://www.cs.tut.fi/sgn/arg/taslp2017-crnn-sed/tut-sed-synthetic-2016',
            'audio_source': 'Field recording',
            'audio_type': 'Synthetic',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Unknown',
        }
        kwargs['crossvalidation_folds'] = 1

        source_url = 'http://www.cs.tut.fi/sgn/arg/taslp2017-crnn-sed/datasets/TUT-SED-synthetic-2016/'
        kwargs['package_list'] = [
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.meta.zip',
                'remote_bytes': 973618,
                'remote_md5': 'e2ae895bdf39f2a359a97bb0bcf76101',
                'filename': 'TUT-SED-synthetic-2016.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.audio.1.zip',
                'remote_bytes': 1026369647,
                'remote_md5': 'ede8b9c6d1b0d1d64bfc5791404f58fb',
                'filename': 'TUT-SED-synthetic-2016.audio.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.audio.2.zip',
                'remote_bytes': 1018650039,
                'remote_md5': 'cde647a377a58fc74e3012139d65c447',
                'filename': 'TUT-SED-synthetic-2016.audio.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.audio.3.zip',
                'remote_bytes': 1070239392,
                'remote_md5': '5fc2824dcce442f441f4c6a975881789',
                'filename': 'TUT-SED-synthetic-2016.audio.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.audio.4.zip',
                'remote_bytes': 1040622610,
                'remote_md5': '4ba016d949171ccc8493d3d274009825',
                'filename': 'TUT-SED-synthetic-2016.audio.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.audio.5.zip',
                'remote_bytes': 264812997,
                'remote_md5': '6a44578dd7738bd4ba044d5d2b9a5448',
                'filename': 'TUT-SED-synthetic-2016.audio.5.zip'
            },
            {
                'content_type': 'features',
                'remote_file': source_url + 'TUT-SED-synthetic-2016.features.zip',
                'remote_bytes': 480894082,
                'remote_md5': '66bc0abc19a276986964a6d4a2d2f6bc',
                'filename': 'TUT-SED-synthetic-2016.features.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']
        super(TUT_SED_Synthetic_2016, self).__init__(**kwargs)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_files = Path().file_list(path=os.path.join(self.local_path, 'meta'), extensions=['txt'])
            meta_data = MetaDataContainer()
            for meta_filename in meta_files:
                audio_filename = os.path.join('audio', os.path.split(meta_filename)[1].replace('.txt', '.wav'))
                data = MetaDataContainer(filename=meta_filename).load()
                for item in data:
                    item.filename = audio_filename
                    item.scene_label = 'synthetic'
                    item.source_label = 'm'
                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                meta_data += data

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self

    def evaluation_setup_filename(self, setup_part='train', fold=None, scene_label=None, file_extension='txt'):
        parts = []
        if scene_label:
            parts.append(scene_label)

        if fold:
            parts.append('fold' + str(fold))

        if setup_part == 'train':
            return os.path.join(self.evaluation_setup_path, 'train+validate' + '.' + file_extension)

        elif setup_part == 'test':
            return os.path.join(self.evaluation_setup_path, 'test' + '.' + file_extension)

        elif setup_part == 'validate':
            return os.path.join(self.evaluation_setup_path, 'validate' + '.' + file_extension)

        elif setup_part == 'evaluate':
            return os.path.join(self.evaluation_setup_path, 'evaluate' + '.' + file_extension)

    def validation_split(self, fold=None, scene_label=None, **kwargs):
        validation_files = MetaDataContainer(
            filename=self.evaluation_setup_filename(setup_part='validate', fold=fold)
        ).load().unique_files

        for index, filename in enumerate(validation_files):
            validation_files[index] = self.relative_to_absolute_path(filename)

        return validation_files

    def file_features(self, filename):
        """Pre-calculated acoustic features for given file

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        data : numpy.ndarray
            Matrix containing acoustic features

        """

        filename_ = self.absolute_to_relative_path(filename).replace('audio/', 'features/')
        filename_ = os.path.splitext(filename_)[0] + '.cpickle'
        if os.path.isfile(os.path.join(self.local_path, filename_)):
            feature_data = pickle.load(open(os.path.join(self.local_path, filename_), "rb"))
            return feature_data['feat']

        else:
            return None


class DBR_Dataset(SoundDataset):
    """DBR (Dog, Bird and Rain) dataset

    """

    def __init__(self,
                 storage_name='dbr-dataset',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'dbr-dataset'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Ville-Veikko Eklund',
            'title': 'DBR Dataset',
            'url': 'https://zenodo.org/record/1069747',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'unknown',
            'microphone_model': 'unknown',
            'licence': 'free non-commercial'
        }

        kwargs['crossvalidation_folds'] = 4
        kwargs['meta_filename'] = 'meta.csv'
        kwargs['evaluation_setup_file_extension'] = 'csv'

        source_url = 'https://zenodo.org/record/1069747/files/'
        kwargs['package_list'] = [
            {
                'content_type': ['audio', 'meta'],
                'remote_file': source_url + 'dbr-dataset.zip',
                'remote_bytes': 653971085,
                'remote_md5': '716f8e3c9a679519b027541d866a81a7',
                'filename': 'dbr-dataset.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']
        super(DBR_Dataset, self).__init__(**kwargs)
        self.audio_fs = 44100
        self.audio_mono = True

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute
            Default value True

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

        else:
            item.filename = self.absolute_to_relative_path(item.filename)

        raw_path, raw_filename = os.path.split(item.filename)
        item.identifier = os.path.splitext(raw_filename)[0]

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        event_label_list = ['dog', 'bird', 'rain']

        Path().makedirs(path=os.path.join(self.local_path, 'audio'))
        # process audio, cut segments and make sampling rate and channel count uniform.
        for event_label in event_label_list:
            annotation_files = Path().file_list(path=os.path.join(self.local_path, event_label), extensions=['txt'])

            for annotation_filename in annotation_files:
                base_name = os.path.split(annotation_filename)[-1]
                audio_filename_source = os.path.join(self.local_path, event_label, os.path.splitext(base_name)[0] + '.wav')

                data = MetaDataContainer(filename=annotation_filename).load(
                    file_format=FileFormat.CSV,
                    fields=['onset', 'offset', 'class_id'],
                    csv_header=False,
                    decimal='comma'
                )

                for item in data:
                    filename = '{base}.seg.{extension}'.format(
                        base=os.path.splitext(base_name)[0],
                        extension='wav'
                    )
                    audio_filename_target = os.path.join(self.local_path, 'audio', filename)
                    if not os.path.exists(audio_filename_target):
                        audio_data = AudioContainer().load(
                            filename=audio_filename_source,
                            fs=self.audio_fs,
                            mono=self.audio_mono
                        )

                        audio_data.set_focus(start_seconds=item.onset, stop_seconds=item.offset)
                        audio_data.freeze()
                        audio_data.save(filename=audio_filename_target)

        if not self.meta_container.exists():
            meta_data = MetaDataContainer()
            for event_label in event_label_list:
                annotation_files = Path().file_list(path=os.path.join(self.local_path, event_label), extensions=['txt'])

                for annotation_filename in annotation_files:
                    data = MetaDataContainer(filename=annotation_filename).load(
                        file_format=FileFormat.CSV,
                        fields=['onset', 'offset', 'class_id'],
                        csv_header=False,
                        decimal='comma'
                    )
                    base_name = os.path.split(annotation_filename)[-1]
                    filename = '{base}.seg.{extension}'.format(
                        base=os.path.splitext(base_name)[0],
                        extension='wav'
                    )

                    for item in data:
                        item.filename = os.path.join('audio', filename)
                        item.event_label = event_label

                        del item['class_id']
                        del item['onset']
                        del item['offset']

                        self.process_meta_item(
                            item=item,
                            absolute_path=False
                        )

                    meta_data += data

            # Save meta
            meta_data.save(filename=self.meta_file, fields=['filename', 'event_label', 'identifier'])

            # Load meta and cross validation
            self.load()

        all_folds_found = True
        for fold in self.folds():
            train_filename = self.evaluation_setup_filename(
                setup_part='train',
                fold=fold
            )

            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                fold=fold
            )

            if not os.path.isfile(train_filename):
                all_folds_found = False

            if not os.path.isfile(test_filename):
                all_folds_found = False

        if not all_folds_found:
            Path().makedirs(
                path=self.evaluation_setup_path
            )

            classes = []
            files = []
            for item in self.meta:
                classes.append(item.event_label)
                files.append(item.filename)

            files = numpy.array(files)

            from sklearn.model_selection import StratifiedShuffleSplit
            sss = StratifiedShuffleSplit(
                n_splits=self.crossvalidation_folds,
                test_size=0.3,
                random_state=0
            )

            fold = 1
            for train_index, test_index in sss.split(X=numpy.zeros(len(classes)), y=classes):
                train_files = files[train_index]
                test_files = files[test_index]
                train_filename = self.evaluation_setup_filename(
                    setup_part='train',
                    fold=fold
                )

                test_filename = self.evaluation_setup_filename(
                    setup_part='test',
                    fold=fold
                )

                eval_filename = self.evaluation_setup_filename(
                    setup_part='evaluate',
                    fold=fold
                )

                # Create meta containers and save them

                # Train
                train_meta = MetaDataContainer(
                    filename=train_filename
                )

                for filename in train_files:
                    train_meta += self.meta_container.filter(
                        filename=filename
                    )

                for item in train_meta:
                    item.filename = self.absolute_to_relative_path(item.filename)

                train_meta.save(fields=['filename', 'event_label'])

                # Test
                test_meta = MetaDataContainer(
                    filename=test_filename
                )

                for filename in test_files:
                    test_meta.append(
                        MetaDataItem(
                            {
                                'filename': self.absolute_to_relative_path(filename)
                            }
                        )
                    )

                for item in test_meta:
                    item.filename = self.absolute_to_relative_path(item.filename)

                test_meta.save(fields=['filename'])

                # Evaluate
                eval_meta = MetaDataContainer(
                    filename=eval_filename
                )

                for filename in test_files:
                    eval_meta += self.meta_container.filter(
                        filename=filename
                    )

                for item in eval_meta:
                    item.filename = self.absolute_to_relative_path(item.filename)

                eval_meta.save(fields=['filename', 'event_label'])

                fold += 1

            # Load cross validation
            self.load()

        return self
