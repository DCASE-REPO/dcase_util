# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import os

from dcase_util.datasets import AudioTaggingDataset
from dcase_util.containers import MetaDataContainer, MetaDataItem, ListDictContainer, DictContainer
from dcase_util.utils import Path


class CHiMEHome_DomesticAudioTag_DevelopmentSet(AudioTaggingDataset):
    def __init__(self,
                 storage_name='CHiMeHome-audiotag-development',
                 data_path=None,
                 included_content_types=None,
                 sample_mode='16kHz',
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'CHiMeHome-audiotag-development'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        sample_mode : str
            Sample rate mode, '16kHz' or '48kHz'
            Default value '16kHz'

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'tag'
        kwargs['dataset_meta'] = {
            'authors': 'Peter Foster, Siddharth Sigtia, Sacha Krstulovic, Jon Barker, and Mark Plumbley',
            'title': 'The CHiME-Home dataset is a collection of annotated domestic environment audio recordings',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Unknown',
        }
        kwargs['crossvalidation_folds'] = 5
        kwargs['package_list'] = [
            {
                'content_type': ['documentation', 'meta', 'audio'],
                'remote_file': 'https://archive.org/download/chime-home/chime_home.tar.gz',
                'remote_bytes': 4162513717,
                'remote_md5': '9ce9d584e229b465b3aa08db2d7fee67',
                'filename': 'chime_home.tar.gz'
            }
        ]
        kwargs['audio_paths'] = [
            os.path.join('chime_home', 'chunks')
        ]
        super(CHiMEHome_DomesticAudioTag_DevelopmentSet, self).__init__(**kwargs)

        self.sample_mode = '.' + sample_mode
        self.tag_map = {
            'c': 'child speech',
            'm': 'adult male speech',
            'f': 'adult female speech',
            'v': 'video game/tv',
            'p': 'percussive sound',
            'b': 'broadband noise',
            'o': 'other',
            'S': 'silence/background',
            'U': 'unidentifiable'
        }

    @property
    def audio_files(self):
        """Get all audio files in the dataset, use only files from CHime-Home-refined set.

        Parameters
        ----------

        Returns
        -------
        files : list
            audio files

        """

        if self.files is None:
            self.files = []
            for path in self.audio_paths:
                if path:
                    dir_list = os.listdir(path)

                    for file_item in dir_list:
                        file_name, file_extension = os.path.splitext(file_item)

                        if file_extension[1:] in self.audio_extensions and file_name.endswith(self.sample_mode):
                            if os.path.abspath(os.path.join(path, file_item)) not in self.files:
                                self.files.append(os.path.abspath(os.path.join(path, file_item)))

            self.files.sort()
        return self.files

    def tagcode_to_taglabel(self, tag):
        if tag in self.tag_map:
            return self.tag_map[tag]

        else:
            return None

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

        name = os.path.split(item.filename)[1]
        segment_name = name[0:name.find('_chunk')]
        chunk_name = name[name.find('_chunk') + 1:].split('.')[0]

        item.identifier = segment_name

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            scene_label = 'home'

            dcase_cross_val_data = ListDictContainer(
                filename=os.path.join(self.local_path, 'chime_home',
                                      'development_chunks_refined_crossval_dcase2016.csv')
            ).load(fields=['id', 'filename', 'set_id'])

            audio_files = {}
            for item in dcase_cross_val_data:
                audio_filename = os.path.join('chime_home', 'chunks', item['filename'] + self.sample_mode + '.wav')
                annotation_filename = os.path.join('chime_home', 'chunks', item['filename'] + '.csv')

                if audio_filename not in audio_files:
                    audio_files[audio_filename] = {
                        'audio': audio_filename,
                        'meta': annotation_filename
                    }

            meta_data = MetaDataContainer()
            for audio_filename, data in iteritems(audio_files):
                current_meta_data = DictContainer(filename=os.path.join(self.local_path, data['meta'])).load()
                tags = []
                for i, tag in enumerate(current_meta_data['majorityvote']):
                    if tag is not 'S' and tag is not 'U':
                        tags.append(self.tagcode_to_taglabel(tag))

                name = os.path.split(audio_filename)[1]
                segment_name = name[0:name.find('_chunk')]
                chunk_name = name[name.find('_chunk')+1:].split('.')[0]

                item = MetaDataItem({
                    'filename': audio_filename,
                    'scene_label': scene_label,
                    'tags': ';'.join(tags)+';',
                    'identifier': segment_name
                })

                self.process_meta_item(
                    item=item,
                    absolute_path=False
                )

                meta_data.append(item)

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        all_folds_found = True
        for fold in range(1, self.crossvalidation_folds+1):
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

            if not os.path.isfile(train_filename):
                all_folds_found = False

            if not os.path.isfile(test_filename):
                all_folds_found = False

            if not os.path.isfile(eval_filename):
                all_folds_found = False

        if not all_folds_found:
            Path().makedirs(path=self.evaluation_setup_path)

            dcase_crossval = {
                1: [],
                2: [],
                3: [],
                4: [],
                5: [],
            }
            dcase_cross_val_data = ListDictContainer(
                filename=os.path.join(self.local_path, 'chime_home',
                                      'development_chunks_refined_crossval_dcase2016.csv')
            ).load(fields=['id', 'filename', 'set_id'])

            for item in dcase_cross_val_data:
                dcase_crossval[int(item['set_id']) + 1].append(
                    self.relative_to_absolute_path(
                        os.path.join('chime_home', 'chunks', item['filename'] + self.sample_mode + '.wav')
                    )
                )

            for fold in range(1, self.crossvalidation_folds+1):
                # Collect training and testing files
                train_files = []
                for f in range(1, self.crossvalidation_folds+1):
                    if f is not fold:
                        train_files += dcase_crossval[f]
                test_files = dcase_crossval[fold]

                # Create meta containers and save them

                # Train
                train_filename = self.evaluation_setup_filename(
                    setup_part='train',
                    fold=fold
                )

                train_meta = MetaDataContainer(filename=train_filename)
                for filename in train_files:
                    item = self.file_meta(filename)[0]
                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                    train_meta.append(item)

                train_meta.save()

                # Test
                test_filename = self.evaluation_setup_filename(
                    setup_part='test',
                    fold=fold
                )

                test_meta = MetaDataContainer(filename=test_filename)
                for filename in test_files:
                    item = MetaDataItem({'filename': self.absolute_to_relative_path(filename)})
                    test_meta.append(item)

                test_meta.save()

                # Evaluate
                eval_filename = self.evaluation_setup_filename(
                    setup_part='evaluate',
                    fold=fold
                )

                eval_meta = MetaDataContainer(filename=eval_filename)
                for filename in test_files:
                    item = self.file_meta(filename)[0]
                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                    eval_meta.append(item)

                eval_meta.save()

            # Load meta and cross validation
            self.load()

        return self


class CHiMEHome_DomesticAudioTag_EvaluationSet(CHiMEHome_DomesticAudioTag_DevelopmentSet):
    def __init__(self,
                 storage_name='CHiMeHome-audiotag-evaluation',
                 data_path=None,
                 included_content_types=None,
                 sample_mode='16kHz',
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'CHiMeHome-audiotag-evaluation'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        sample_mode : str
            Sample rate mode, '16kHz' or '48kHz'
            Default value '16kHz'

        """

        kwargs['evaluation_setup_folder'] = 'evaluation_setup_evaluation'
        kwargs['meta_filename'] = 'meta_evaluation.txt'
        kwargs['local_path'] = os.path.join(data_path, 'CHiMeHome-audiotag-development')
        kwargs['filelisthash_filename'] = 'filelist_evaluation.python.hash'

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'tag'
        kwargs['dataset_meta'] = {
            'authors': 'Peter Foster, Siddharth Sigtia, Sacha Krstulovic, Jon Barker, and Mark Plumbley',
            'title': 'The CHiME-Home dataset is a collection of annotated domestic environment audio recordings',
            'url': None,
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Unknown',
        }

        kwargs['package_list'] = [
            {
                'content_type': ['documentation', 'meta', 'audio'],
                'remote_file': 'https://archive.org/download/chime-home/chime_home.tar.gz',
                'remote_bytes': 4162513717,
                'remote_md5': '9ce9d584e229b465b3aa08db2d7fee67',
                'filename': 'chime_home.tar.gz'
            }
        ]
        kwargs['audio_paths'] = [
            os.path.join('chime_home', 'chunks')
        ]
        super(CHiMEHome_DomesticAudioTag_EvaluationSet, self).__init__(**kwargs)
        self.crossvalidation_folds = None
        self.sample_mode = '.' + sample_mode
        self.tag_map = {
            'c': 'child speech',
            'm': 'adult male speech',
            'f': 'adult female speech',
            'v': 'video game/tv',
            'p': 'percussive sound',
            'b': 'broadband noise',
            'o': 'other',
            'S': 'silence/background',
            'U': 'unidentifiable'
        }

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """
        if not self.meta_container.exists():
            scene_label = 'home'

            evaluation_chunks = ListDictContainer(
                filename=os.path.join(self.local_path, 'chime_home',
                                      'evaluation_chunks_refined.csv')
            ).load(fields=['id', 'filename', 'set_id'])

            audio_files = {}
            for item in dcase_cross_val_data:
                audio_filename = os.path.join('chime_home', 'chunks', item['filename'] + self.sample_mode + '.wav')
                annotation_filename = os.path.join('chime_home', 'chunks', item['filename'] + '.csv')

                if audio_filename not in audio_files:
                    audio_files[audio_filename] = {
                        'audio': audio_filename,
                        'meta': annotation_filename
                    }

            meta_data = MetaDataContainer()
            for audio_filename, data in iteritems(audio_files):
                current_meta_data = DictContainer(filename=os.path.join(self.local_path, data['meta'])).load()
                tags = []
                for i, tag in enumerate(current_meta_data['majorityvote']):
                    if tag is not 'S' and tag is not 'U':
                        tags.append(self.tagcode_to_taglabel(tag))

                name = os.path.split(audio_filename)[1]
                segment_name = name[0:name.find('_chunk')]
                chunk_name = name[name.find('_chunk')+1:].split('.')[0]

                item = MetaDataItem({
                    'filename': audio_filename,
                    'scene_label': scene_label,
                    'tags': ';'.join(tags)+';',
                    'identifier': segment_name
                })

                self.process_meta_item(
                    item=item,
                    absolute_path=False
                )

                meta_data.append(item)

            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        all_folds_found = True

        train_filename = self.evaluation_setup_filename(
            setup_part='train'
        )

        test_filename = self.evaluation_setup_filename(
            setup_part='test'
        )

        eval_filename = self.evaluation_setup_filename(
            setup_part='evaluate'
        )

        if not os.path.isfile(train_filename):
            all_folds_found = False

        if not os.path.isfile(test_filename):
            all_folds_found = False

        if not os.path.isfile(eval_filename):
            all_folds_found = False

        if not all_folds_found:
            Path().makedirs(path=self.evaluation_setup_path)

            # Train
            train_filename = self.evaluation_setup_filename(
                setup_part='train'
            )

            train_meta = MetaDataContainer(filename=train_filename)
            for filename in self.train_files():
                train_meta.append(self.file_meta(filename)[0])

            train_meta.save()

            # Test
            test_filename = self.evaluation_setup_filename(
                setup_part='test'
            )

            test_meta = MetaDataContainer(filename=test_filename)
            for filename in self.test_files():
                test_meta.append(MetaDataItem({'filename': self.absolute_to_relative_path(filename)}))

            test_meta.save()

            # Evaluate
            eval_filename = self.evaluation_setup_filename(
                setup_part='evaluate'
            )

            eval_meta = MetaDataContainer(filename=eval_filename)
            for filename in self.test_files():
                eval_meta.append(self.file_meta(filename)[0])

            eval_meta.save()

            # Load meta and cross validation
            self.load()

        return self
