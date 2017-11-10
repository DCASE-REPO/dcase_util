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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)
        else:
            item.filename = self.absolute_to_relative(item.filename)

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
                        self.process_meta_item(item=item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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
                'remote_md5': '47bbdc0614b468d2bfadbc49e561a320',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.meta.zip',
                'remote_bytes': 4473,
                'remote_md5': 'e006cfec14a49dd79a6ab8f8d5b1c5e6',
                'filename': 'TUT-acoustic-scenes-2017-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-acoustic-scenes-2017-evaluation.audio.1.zip',
                'remote_bytes': 1071856687,
                'remote_md5': '5d97dea8461baec8027ae4a0c2b18d4b',
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

        filename_map : OneToOneMappingContainer
            Filename map

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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
                        self.process_meta_item(item=item, absolute_path=False, filename_map=filename_map)
                        meta_data[item.filename] = item

                # Save meta
                MetaDataContainer(list(meta_data.values())).save(filename=self.meta_file)

                # Load meta and cross validation
                self.load()

        return self


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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

        source_url = 'http://www.cs.tut.fi/sgn/arg/dcase2017/data/TUT-rare-sound-events-2017-development/'
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
                        current_meta = MetaDataContainer(filename=event_list_filename).load()
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
                current_meta = MetaDataContainer(filename=event_list_filename).load()
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
                current_meta = MetaDataContainer(filename=event_list_filename).load()
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
                current_meta = MetaDataContainer(filename=event_list_filename).load()
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['reference_data_present'] = False
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

        source_url = 'http://www.cs.tut.fi/sgn/arg/dcase2017/data/TUT-rare-sound-events-2017-evaluation/'
        kwargs['package_list'] = [
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.1.zip',
                'remote_bytes': 1072283898,
                'remote_md5': '9db7740e57813cf9dcc7fc5e75bf3845',
                'filename': 'TUT-rare-sound-events-2017-evaluation.1.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.2.zip',
                'remote_bytes': 1070947558,
                'remote_md5': '080fcbff19c39cbca410853f8438b5d8',
                'filename': 'TUT-rare-sound-events-2017-evaluation.2.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.3.zip',
                'remote_bytes': 1072470355,
                'remote_md5': '7a58cd495b0326381d8faecfa8b2ef9c',
                'filename': 'TUT-rare-sound-events-2017-evaluation.3.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.4.zip',
                'remote_bytes': 1073265283,
                'remote_md5': 'f8bb2e729d54b08305e601096dfacc01',
                'filename': 'TUT-rare-sound-events-2017-evaluation.4.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-rare-sound-events-2017-evaluation.5.zip',
                'remote_bytes': 306612051,
                'remote_md5': 'e08c30e98161b0104ad381c0f68838a8',
                'filename': 'TUT-rare-sound-events-2017-evaluation.5.zip'
            }
        ]
        kwargs['audio_paths'] = ['audio']

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

        # Make sure evaluation_setup directory exists
        Path().makedirs(path=os.path.join(self.local_path, self.evaluation_setup_folder))

        if not self.meta_container.exists() and self.reference_data_present:
            message = '{name}: Meta file not found [{filename}]'.format(
                name=self.__class__.__name__,
                filename=self.meta_container.filename
            )

            self.logger.exception(message)
            raise IOError(message)

        if not self.reference_data_present:
            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                file_extension='txt',
                scene_label=scene_label
            )

            if not os.path.isfile(test_filename):
                files = Path().file_list(
                    path=os.path.join(self.local_path, 'audio'),
                    extensions=self.default_audio_extension
                )
                test_meta = MetaDataContainer()
                for audio_filename in files:
                    item = MetaDataItem(
                        {
                            'filename': os.path.join('audio', os.path.split(audio_filename)[1]),
                            'scene_label': scene_label
                        }
                    )
                    test_meta.append(item)

                test_meta.save(filename=test_filename)

                # Load meta and cross validation
                self.load()
        return self

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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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
                    self.process_meta_item(item=item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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
                'remote_md5': '9d4378427b50e830efcdcbac95335448',
                'filename': 'TUT-sound-events-2017-evaluation.doc.zip'
            },
            {
                'content_type': 'meta',
                'remote_file': source_url + 'TUT-sound-events-2017-evaluation.meta.zip',
                'remote_bytes': 762,
                'remote_md5': 'e5e343c25909d14df282eebcf301a672',
                'filename': 'TUT-sound-events-2017-evaluation.meta.zip'
            },
            {
                'content_type': 'audio',
                'remote_file': source_url + 'TUT-sound-events-2017-evaluation.audio.zip',
                'remote_bytes': 388173790,
                'remote_md5': '857f8d3f56e0e8ac55fe082e5b792007',
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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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
                    self.process_meta_item(item=item, absolute_path=False)
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
                        self.process_meta_item(item=item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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
                        self.process_meta_item(item=item, absolute_path=False)
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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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
                        self.process_meta_item(item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

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

                    self.process_meta_item(item=item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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

                    self.process_meta_item(item=item, absolute_path=False)
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

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

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
                    self.process_meta_item(item=item, absolute_path=False)

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

        filename_ = self.absolute_to_relative(filename).replace('audio/', 'features/')
        filename_ = os.path.splitext(filename_)[0] + '.cpickle'
        if os.path.isfile(os.path.join(self.local_path, filename_)):
            feature_data = pickle.load(open(os.path.join(self.local_path, filename_), "rb"))
            return feature_data['feat']
        else:
            return None
